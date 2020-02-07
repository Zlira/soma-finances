from contextlib import contextmanager
from itertools import groupby
from operator import itemgetter

from .models import Constants, Paper, ClassUnit


ONE_TIME_PRICE_LABEL = 'одноразова ціна'
ONE_TIME_PRICE_ID = 0
UNIT_SALARY_LABEL = 'всього за заняття'


class PricePerParticipantTable:
    def __init__(self):
        self._paper_prices = None
        self._one_time_price = None

    @property
    def paper_prices(self):
        if not self._paper_prices:
            paper_prices = (
                Paper.objects
                .annotate(one_time_price=Paper.get_one_time_price_expression())
                .values('id', 'one_time_price', 'name')
            )
            self._paper_prices = {
                item['id']: {'name': item['name'], 'price': item['one_time_price']}
                for item in paper_prices
            }
        return self._paper_prices

    @contextmanager
    def set_one_time_price(self, one_time_price):
        if one_time_price is None:
            raise ValueError("one_time_price must be a number")
        self._one_time_price = one_time_price
        yield
        self._one_time_price = None

    def get_price(self, id):
        if id == ONE_TIME_PRICE_ID:
            if self._one_time_price is None:
                raise ValueError(
                    "Cannot return one time price, use set_one_time_price manager"
                )
            return self._one_time_price
        return self.paper_prices[id]['price']

    def get_name(self, id):
        if id == ONE_TIME_PRICE_ID:
            return ONE_TIME_PRICE_LABEL
        return self.paper_prices[id]['name']

    def get_ids(self):
        yield from sorted(self.paper_prices.keys())
        yield ONE_TIME_PRICE_ID


def count_salary_for_unit(prices_table, teachers_min_salary, unit_payments):
    res = {}
    unit_sum = 0
    for payment_method_id in prices_table.get_ids():
        participants_payed = unit_payments.get(payment_method_id, 0)
        res[prices_table.get_name(payment_method_id)] = participants_payed
        unit_sum += participants_payed * prices_table.get_price(payment_method_id) / 2
    if 0 < unit_sum < teachers_min_salary:
        unit_sum = teachers_min_salary
    res[UNIT_SALARY_LABEL] = unit_sum
    return res



def get_detailed_teachers_salary_for_period(teacher, start_date, end_date):
        res = {}
        units = teacher.get_units_for_period(start_date, end_date)
        if not units:
            return res
        prices_table = PricePerParticipantTable()
        unit_payments = []
        for unit in units:
            payment_methods = unit.get_price_by_payement_methods()
            unit_payments.append({
                'regular_class': unit.regular_class, 'date': unit.date,
                'payment_methods': payment_methods,
            })

        res = {}
        teachers_min_salary = Constants.get_min_teachers_salary()
        for regular_class, unit_group in groupby(unit_payments, itemgetter('regular_class')):
            one_time_price = regular_class.one_time_price
            salary_per_unit = {}
            with prices_table.set_one_time_price(one_time_price):
                for unit in unit_group:
                    salary_per_unit[unit['date']] = count_salary_for_unit(
                        prices_table, teachers_min_salary, unit['payment_methods']
                    )
            res[regular_class.name] = salary_per_unit
        return res