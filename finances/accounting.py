from calendar import monthrange
from collections import namedtuple, OrderedDict, defaultdict
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date
from itertools import groupby
from operator import itemgetter

from django.db.models import Value, F

from .models import Constants, Paper, ClassUnit, ParticipantPaper, \
    ClassParticipation, Donation, SingleEvent, Expense


ONE_TIME_PRICE_LABEL = 'одноразова ціна'
ONE_TIME_PRICE_ID = 0
UNIT_SALARY_LABEL = 'всього за заняття'


@dataclass(frozen=True)
class Payment:
    teachers_share: int
    id_: int
    name: str


@dataclass(frozen=True)
class OneTimePayment(Payment):
    id_: int = 0
    name: str = 'одноразова ціна'


class ClassUnitPayments:
    def __init__(self, class_unit, class_payments=None):
        self._payment_counts = {}
        self._min_salary = None
        self.class_payments = class_payments
        self.class_unit = class_unit

    @property
    def payment_counts(self):
        if not self._payment_counts:
            self._payment_counts = defaultdict(
                int, self.class_unit.get_payement_method_counts()
            )
        return self._payment_counts

    @property
    def min_salary(self):
        # TODO a query for every unit!
        if self._min_salary is None:
            self._min_salary = Constants.get_min_teachers_salary()
        return self._min_salary

    def set_class_payments(self, class_payments):
        self.class_payments = class_payments

    def sum_teachers_share(self):
        if not self.class_payments:
            raise ValueError(
                'Cannot calculate teachers share without class_payments.possible_payments'
            )
        possible_payments = self.class_payments.possible_payments
        share = 0
        for payment_id, payment_type in possible_payments.items():
            share += self.payment_counts.get(payment_id, 0) * payment_type.teachers_share
        if share == 0:
            return share
        return share if share > self.min_salary else self.min_salary


class RegularClassPayments:
    def __init__(self, name, unit_payments, possible_payments):
        self.name = name
        self.unit_payments = unit_payments
        self.possible_payments = possible_payments
        for u_p in self.unit_payments:
            u_p.set_class_payments(self)

    def sum_teachers_share(self):
        return sum(
            unit.sum_teachers_share()
            for unit in self.unit_payments
        )


class PaymentTypes:
    def __init__(self):
        self._paper_payments = OrderedDict()

    @property
    def paper_payments(self):
        if not self._paper_payments:
            paper_prices = (
                Paper.objects
                .annotate(
                    teachers_share=Paper.get_one_time_price_expression() / 2,
                    id_=F('id')
                )
                .values('id_', 'teachers_share', 'name')
            )
            for paper in paper_prices:
                self._paper_payments[paper['id_']] = Payment(**paper)
        return self._paper_payments

    def get_for_class(self, regular_class):
        payment_types = OrderedDict(self.paper_payments)
        one_time_payment = OneTimePayment(
            teachers_share=regular_class.one_time_price / 2
        )
        payment_types[one_time_payment.id_] = one_time_payment
        return payment_types



def get_detailed_teachers_salary_for_period(teacher, start_date, end_date):
    res = []
    units = teacher.get_units_for_period(start_date, end_date)
    if not units:
        return res
    unit_payments = [
        ClassUnitPayments(unit) for unit in units
    ]
    payment_types = PaymentTypes()
    for regular_class, unit_group in groupby(
        unit_payments, lambda up: up.class_unit.regular_class
    ):
        possible_payments = payment_types.get_for_class(regular_class)
        class_payments = RegularClassPayments(
            name=regular_class.name,
            possible_payments=possible_payments,
            unit_payments=list(unit_group),
        )
        res.append(class_payments)
    return res


def month_to_range(year, month):
    month_range = namedtuple('MonthRange', ('start_date', 'end_date'))
    start_date = date(year, month, 1)
    months_end_day = monthrange(year, month)[1]
    end_date = date(year, month, months_end_day)
    return month_range(start_date, end_date)


def default_salary_range():
    DateRange = namedtuple('DataRange', ('start_date', 'end_date'))
    today = date.today()
    months_end_day = monthrange(today.year, today.month)[1]
    months_middle_day = 15
    if today.day <= months_middle_day:
        return DateRange(
            date(today.year, today.month, 1),
            date(today.year, today.month, months_middle_day)
        )
    else:
        return DateRange(
            date(today.year, today.month, months_middle_day + 1),
            date(today.year, today.month, months_end_day)
        )


def get_months_earnings_report(year, month):
    start_date, end_date = month_to_range(year, month)

    papers = list(ParticipantPaper.aggregate_earnings_for_period(start_date, end_date))
    # TODO move this to the model method
    total_from_papers = sum(p['amount'] for p in papers)
    detailed_papers = {p['paper__name']: {'count': p['count'], 'amount': p['amount']} for p in papers}

    one_time_payments = list(ClassParticipation.aggregate_earnings_for_period(
        start_date, end_date
    ))
    # TODO move this to the model method
    total_from_one_time_payments = sum(cp['amount'] for cp in one_time_payments)
    detailed_one_time_payments = {
        cp['class_name']: {'count': cp['count'], 'amount': cp['amount']}
        for cp in one_time_payments
    }

    donations = Donation.aggregate_earnings_for_period(start_date, end_date)
    events = SingleEvent.aggregate_earnings_for_period(start_date, end_date)

    return {
        'папірці': {
            'total': total_from_papers,
            'detailed': detailed_papers,
        },
        'за заняття': {
            'total': total_from_one_time_payments,
            'detailed': detailed_one_time_payments,
        },
        'донації': donations,
        'події': events,
    }


def get_months_expenses_report(year, month):
    start_date, end_date = month_to_range(year, month)
    return Expense.aggregate_for_period(start_date, end_date)


def get_months_report(year, month):
    earnings = get_months_earnings_report(year, month)
    expenses = get_months_expenses_report(year, month)

    earnings['total'] = sum(
        category['total'] for category in earnings.values()
    )
    expenses['total'] = sum(
        category['total'] for category in expenses.values()
    )
    return {
        'earnings': earnings,
        'expenses': expenses,
    }