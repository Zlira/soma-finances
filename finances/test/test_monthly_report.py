from datetime import date, timedelta

from django.test import TestCase

from finances.accounting import get_months_earnings_report, \
    get_months_expenses_report
from finances.models import Paper, Participant, ParticipantPaper, \
    RegularClass, ClassUnit, Teacher, ClassParticipation, Donation, \
    SingleEvent, Expense


class TestMonthlyEarnings(TestCase):
    def setUp(self):
        self.limited_paper = Paper.objects.create(
            name='limited', price=500
        )
        self.limitless_paper = Paper.objects.create(
            name='limitless', price=1000
        )
        self.start_date = date(2019, 1, 1)
        self.end_date = date(2019, 1, 31)

    def test_earnings_include_papers_bought_by_type(self):
        participant_1 = Participant.objects.create(name='solpav')
        participant_2 = Participant.objects.create(name='kvasyk')

        # one limitless, two limitted
        ParticipantPaper.objects.create(
            participant=participant_1, paper=self.limited_paper,
            date_purchased=self.start_date
        )
        ParticipantPaper.objects.create(
            participant=participant_1, paper=self.limitless_paper,
            date_purchased=self.start_date
        )
        ParticipantPaper.objects.create(
            participant=participant_2, paper=self.limited_paper,
            date_purchased=self.start_date
        )

        earnings_report = get_months_earnings_report(
            self.start_date.year, self.start_date.month
        )
        expected_report = {
            'total': 2000,
            'detailed': {
                'limited': {'count': 2, 'amount': 1000},
                'limitless': {'count': 1, 'amount': 1000},
            }
        }
        self.assertDictEqual(
            earnings_report['папірці'], expected_report
        )

    def test_earnings_dont_include_papers_from_other_months(self):
        participant_1 = Participant.objects.create(name='solpav')

        ParticipantPaper.objects.create(
            participant=participant_1, paper=self.limited_paper,
            date_purchased=self.start_date - timedelta(days=1)
        )
        ParticipantPaper.objects.create(
            participant=participant_1, paper=self.limitless_paper,
            date_purchased=self.end_date + timedelta(days=1)
        )

        earnings_report = get_months_earnings_report(
            self.start_date.year, self.start_date.month
        )
        expected_report = {
            'total': 0,
            'detailed': {}
        }
        self.assertDictEqual(
            earnings_report['папірці'], expected_report
        )

    def test_earnings_dont_include_volunteer_papers(self):
        participant_1 = Participant.objects.create(name='solpav')

        ParticipantPaper.objects.create(
            participant=participant_1, paper=self.limited_paper,
            date_purchased=self.start_date, is_volunteer=True,
        )
        ParticipantPaper.objects.create(
            participant=participant_1, paper=self.limitless_paper,
            date_purchased=self.end_date + timedelta(days=1)
        )

        earnings_report = get_months_earnings_report(
            self.start_date.year, self.start_date.month
        )
        expected_report = {
            'total': 0,
            'detailed': {}
        }
        self.assertDictEqual(
            earnings_report['папірці'], expected_report
        )

    def test_earnings_include_one_time_payments_for_classes(self):
        teacher = Teacher.objects.create(name='Master Cheng')
        regular_class_1 = RegularClass.objects.create(
            name='Spanish 101', one_time_price=100, start_date=self.start_date
        )
        unit_1 = ClassUnit.objects.create(
            regular_class=regular_class_1, teacher=teacher, date=self.start_date
        )
        regular_class_2 = RegularClass.objects.create(
            name='Spanish 102', one_time_price=200, start_date=self.start_date
        )
        unit_2 = ClassUnit.objects.create(
            regular_class=regular_class_2, teacher=teacher, date=self.start_date
        )

        participant_1 = Participant.objects.create(name="Troy")
        participant_2 = Participant.objects.create(name="Abed")

        # two payments for class_1 and one for class_2
        ClassParticipation.objects.create(
            participant=participant_1, class_unit=unit_1,
            paid_one_time_price=True
        )
        ClassParticipation.objects.create(
            participant=participant_2, class_unit=unit_1,
            paid_one_time_price=True
        )
        ClassParticipation.objects.create(
            participant=participant_1, class_unit=unit_2,
            paid_one_time_price=True
        )
        earnings_report = get_months_earnings_report(
            self.start_date.year, self.start_date.month
        )
        expected_class_payments = {
            'total': 400,
            'detailed': {
                'Spanish 101': {'count': 2, 'amount': 200},
                'Spanish 102': {'count': 1, 'amount': 200},
            }
        }
        self.assertDictEqual(
            earnings_report['за заняття'],
            expected_class_payments,
        )

    def test_earnings_dont_include_one_time_payments_from_other_months(self):
        teacher = Teacher.objects.create(name='Master Cheng')
        regular_class = RegularClass.objects.create(
            name='Spanish 101', one_time_price=100, start_date=self.start_date
        )
        unit_before = ClassUnit.objects.create(
            regular_class=regular_class, teacher=teacher,
            date=self.start_date-timedelta(days=1)
        )
        unit_after = ClassUnit.objects.create(
            regular_class=regular_class, teacher=teacher,
            date=self.end_date+timedelta(days=1)
        )

        participant = Participant.objects.create(name="Troy")

        ClassParticipation.objects.create(
            participant=participant, class_unit=unit_before,
            paid_one_time_price=True
        )
        ClassParticipation.objects.create(
            participant=participant, class_unit=unit_after,
            paid_one_time_price=True
        )

        earnings_report = get_months_earnings_report(
            self.start_date.year, self.start_date.month
        )
        expected_class_payments = {
            'total': 0,
            'detailed': {}
        }
        self.assertDictEqual(
            earnings_report['за заняття'],
            expected_class_payments,
        )

    def test_earnings_dont_include_participations_with_cards(self):
        teacher = Teacher.objects.create(name='Master Cheng')
        regular_class = RegularClass.objects.create(
            name='Spanish 101', one_time_price=100, start_date=self.start_date
        )
        unit = ClassUnit.objects.create(
            regular_class=regular_class, teacher=teacher,
            date=self.start_date,
        )

        participant = Participant.objects.create(name="Troy")
        participant_paper = ParticipantPaper.objects.create(
            participant=participant, paper=self.limited_paper,
            date_purchased=self.start_date,
        )

        ClassParticipation.objects.create(
            participant=participant, class_unit=unit,
            paid_one_time_price=False,
            paper_used=participant_paper,
        )

        earnings_report = get_months_earnings_report(
            self.start_date.year, self.start_date.month
        )
        expected_class_payments = {
            'total': 0,
            'detailed': {}
        }
        self.assertDictEqual(
            earnings_report['за заняття'],
            expected_class_payments,
        )


        pass

    def test_earnins_include_donations(self):
        donation_1 = Donation.objects.create(
            date=self.start_date, amount=100
        )
        donation_2 = Donation.objects.create(
            date=self.start_date+timedelta(days=2), amount=1000,
        )

        earnings_report = get_months_earnings_report(
            self.start_date.year, self.start_date.month,
        )
        expected_donation_earnings = {
            'total': donation_1.amount + donation_2.amount
        }
        self.assertDictEqual(
            earnings_report['донації'], expected_donation_earnings,
        )

    def test_earnins_dont_include_donations_from_other_months(self):
        Donation.objects.create(
            date=self.start_date - timedelta(days=1), amount=100
        )
        Donation.objects.create(
            date=self.end_date + timedelta(days=2), amount=1000,
        )

        earnings_report = get_months_earnings_report(
            self.start_date.year, self.start_date.month,
        )
        expected_donation_earnings = {
            'total': 0
        }
        self.assertDictEqual(
            earnings_report['донації'], expected_donation_earnings,
        )

    def test_earnings_include_single_events(self):
        single_event_1 = SingleEvent.objects.create(
            name='Pagan ritual', date=self.start_date,
            admission_sum=1000, bar_sum=0,
        )
        single_event_2 = SingleEvent.objects.create(
            name="Knitting session", date=self.start_date,
            admission_sum=400, bar_sum=800,
        )

        earnings_report = get_months_earnings_report(
            self.start_date.year, self.start_date.month
        )
        expected_event_earnings = {
            'total': 2200,
            'detailed': {
                single_event_1.name: {
                    'admission': single_event_1.admission_sum,
                    'bar': single_event_1.bar_sum,
                },
                single_event_2.name: {
                    'admission': single_event_2.admission_sum,
                    'bar': single_event_2.bar_sum,
                }
            }
        }
        self.assertDictEqual(
            earnings_report['події'],
            expected_event_earnings
        )

    def test_earnings_dont_include_events_from_other_months(self):
        SingleEvent.objects.create(
            name='Pagan ritual', date=self.start_date-timedelta(days=1),
            admission_sum=1000, bar_sum=0,
        )
        SingleEvent.objects.create(
            name="Knitting session", date=self.end_date+timedelta(days=2),
            admission_sum=400, bar_sum=800,
        )

        earnings_report = get_months_earnings_report(
            self.start_date.year, self.start_date.month
        )
        expected_event_earnings = {
            'total': 0,
            'detailed': {}
        }
        self.assertDictEqual(
            earnings_report['події'],
            expected_event_earnings
        )


class TestMonthlyExpenses(TestCase):
    def setUp(self):
        self.start_date = date(2019, 1, 1)
        self.end_date = date(2019, 1, 31)
        self.year = self.start_date.year
        self.month = self.start_date.month
        self.date_before = self.start_date - timedelta(days=1)
        self.date_after = self.end_date + timedelta(days=1)

    def test_expenses_include_teachers_fees(self):
        salary_1 = Expense.objects.create(
            date=self.start_date,
            category=Expense.FEES_CAT,
            amount=3000,
            description='Solpavchyks salary for February'
        )
        salary_2 = Expense.objects.create(
            date=self.end_date,
            category=Expense.FEES_CAT,
            amount=2500,
            description='Kvasyks salary for February'
        )

        expenses_report = get_months_expenses_report(self.year, self.month)
        expected_fees = {
            'total': salary_1.amount + salary_2.amount,
            'detailed': {
                salary_1.description: salary_1.amount,
                salary_2.description: salary_2.amount,
            }
        }
        self.assertDictEqual(expenses_report['гонорари'], expected_fees)

    def test_expenses_dont_include_teachers_fees_from_other_months(self):
        Expense.objects.create(
            date=self.date_before,
            category=Expense.FEES_CAT,
            amount=3000,
            description='Solpavchyks salary for February'
        )
        Expense.objects.create(
            date=self.date_after,
            category=Expense.FEES_CAT,
            amount=2500,
            description='Kvasyks salary for February'
        )

        expenses_report = get_months_expenses_report(self.year, self.month)
        expected_fees = {
            'total': 0,
            'detailed': {}
        }
        self.assertDictEqual(expenses_report['гонорари'], expected_fees)

    def test_expenses_include_main_section(self):
        expense_1 = Expense.objects.create(
            date=self.start_date,
            category=Expense.MAIN_CAT,
            amount=3000,
            description='Rent'
        )
        expense_2 = Expense.objects.create(
            date=self.end_date,
            category=Expense.MAIN_CAT,
            amount=2500,
            description='Electricity'
        )

        expenses_report = get_months_expenses_report(self.year, self.month)
        expected_fees = {
            'total': expense_1.amount + expense_2.amount,
            'detailed': {
                expense_1.description: expense_1.amount,
                expense_2.description: expense_2.amount,
            }
        }
        self.assertDictEqual(expenses_report['основні'], expected_fees)

    def test_expenses_dont_include_main_section_from_other_months(self):
        Expense.objects.create(
            date=self.date_before,
            category=Expense.MAIN_CAT,
            amount=3000,
            description='Rent'
        )
        Expense.objects.create(
            date=self.date_after,
            category=Expense.MAIN_CAT,
            amount=2500,
            description='Electricity'
        )

        expenses_report = get_months_expenses_report(self.year, self.month)
        expected_fees = {
            'total': 0,
            'detailed': {}
        }
        self.assertDictEqual(expenses_report['основні'], expected_fees)

    def test_expenses_include_bar(self):
        bar_1 = Expense.objects.create(
            date=self.start_date,
            category=Expense.BAR_CAT,
            amount=3000,
            description='Випивка'
        )
        bar_2 = Expense.objects.create(
            date=self.end_date,
            category=Expense.BAR_CAT,
            amount=2500,
            description='Закуска'
        )

        expenses_report = get_months_expenses_report(self.year, self.month)
        self.assertEqual(
            expenses_report['бар']['total'], bar_1.amount + bar_2.amount
        )

    def test_expenses_include_space(self):
        space_1 = Expense.objects.create(
            date=self.start_date,
            category=Expense.SPACE_CAT,
            amount=3000,
            description='Фломастери'
        )
        space_2 = Expense.objects.create(
            date=self.end_date,
            category=Expense.SPACE_CAT,
            amount=2500,
            description='Слаймік'
        )

        expenses_report = get_months_expenses_report(self.year, self.month)
        self.assertEqual(
            expenses_report['простір']['total'], space_1.amount + space_2.amount
        )