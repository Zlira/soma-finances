from datetime import date

from django.test import TestCase

from finances.models import Teacher,\
    RegularClass, ClassUnit, Participant,\
    ClassParticipation, Paper, ParticipantPaper, Constants
from finances.accounting import get_detailed_teachers_salary_for_period, \
    PaymentTypes


class TestPaymentTypes(TestCase):

    def test_retrieves_paper_payments(self):
        paper_1 = Paper.objects.create(
            name='name 1', price=8, number_of_uses=2
        )
        paper_2 = Paper.objects.create(
            name='name 2', price=16, number_of_uses=2
        )
        pt = PaymentTypes()
        payments = pt.paper_payments
        self.assertEqual(len(payments), 2)

        payment_1 = payments[paper_1.id]
        self.assertEqual(
            payment_1.teachers_share,
            paper_1.price / paper_1.number_of_uses / 2
        )
        self.assertEqual(payment_1.name, paper_1.name)

    def test_includes_regular_class_price(self):
        Paper.objects.create(
            name='name 1', price=8, number_of_uses=2
        )
        class_ = RegularClass.objects.create(
            name='how not to suck at testing',
            one_time_price=20, start_date=date.today()
        )
        pt = PaymentTypes()
        payments = pt.get_for_class(class_)

        self.assertEqual(len(payments), 2)
        one_time_payment = payments[0]
        self.assertEqual(
            one_time_payment.teachers_share,
            class_.one_time_price / 2
        )


class TestSalary(TestCase):

    def create_class_and_unit(
        self, class_name, unit_date, one_time_price=100,
        teacher=None
    ):
        teacher = teacher or self.teacher
        reg_class = RegularClass.objects.create(
            name=class_name, start_date=unit_date,
            one_time_price=one_time_price,
        )
        class_unit = ClassUnit.objects.create(
            regular_class=reg_class, date=unit_date, teacher=teacher
        )
        return reg_class, class_unit

    def add_participant_to_class_unit(self, class_unit, paper_used=None):
        participant = Participant.objects.create(name="Oopyr")
        if paper_used:
            paper_used = ParticipantPaper.objects.create(
                paper=paper_used,
                participant=participant,
                date_purchased=class_unit.date
            )
        return ClassParticipation.objects.create(
            class_unit=class_unit,
            participant=participant,
            paid_one_time_price=paper_used is None,
            paper_used=paper_used
        )

    def setUp(self):
        self.teacher = Teacher.objects.create(name='Homer')

    def test_salary_empty_if_no_classes(self):
        res = get_detailed_teachers_salary_for_period(
            self.teacher, '2019-02-01', '2019-02-03')

        self.assertListEqual(res, [])

    def test_salary_is_0_if_no_participants(self):
        unit_date = date(2019, 2, 10)
        reg_class_name = 'Yoga'
        self.create_class_and_unit(
            reg_class_name, unit_date
        )

        res = get_detailed_teachers_salary_for_period(
            self.teacher, unit_date, unit_date
        )

        # if nobody was present at the class techer gets nothing
        self.assertEqual(
            res[0].sum_teachers_share(), 0
        )

    def test_onetime_price_is_used_if_participant_without_paper(self):
        unit_date = date(2019, 2, 10)
        reg_class_name = 'Yoga'
        reg_class_price = 500
        reg_class, class_unit = self.create_class_and_unit(
            reg_class_name, unit_date, reg_class_price
        )
        self.add_participant_to_class_unit(class_unit)

        res = get_detailed_teachers_salary_for_period(
            self.teacher, unit_date, unit_date)

        self.assertEqual(
            res[0].sum_teachers_share(), reg_class_price/2
        )
        unit_payments = res[0].unit_payments[0]
        one_time_price_id = 0
        self.assertEqual(unit_payments.payment_counts[one_time_price_id], 1)

    def test_includes_only_units_inside_period(self):
        unit_date = date(2019, 2, 10)
        date_before_class = date(2019, 2, 9)
        date_after_class = date(2019, 2, 11)
        reg_class_name = 'Yoga'
        reg_class, class_unit = self.create_class_and_unit(
            reg_class_name, unit_date
        )
        self.add_participant_to_class_unit(class_unit)

        salary_for_earlier_period = get_detailed_teachers_salary_for_period(
            self.teacher, date_before_class, date_before_class
        )
        self.assertListEqual(salary_for_earlier_period, [])

        salary_for_later_period = get_detailed_teachers_salary_for_period(
            self.teacher, date_after_class, date_after_class
        )
        self.assertListEqual(salary_for_later_period, [])

    def test_doesnt_include_units_from_other_teachers(self):
        unit_date = date(2019, 2, 10)
        reg_class_name = 'Yoga'
        other_teacher = Teacher.objects.create(name='Grishnak')
        reg_class, class_unit = self.create_class_and_unit(
            reg_class_name, unit_date, teacher=other_teacher
        )
        self.add_participant_to_class_unit(class_unit)

        salary_for_this_teacher = get_detailed_teachers_salary_for_period(
            self.teacher, unit_date, unit_date
        )

        self.assertListEqual(salary_for_this_teacher, [])

    def test_adds_half_of_paper_one_time_price_to_salary(self):
        unit_date = date(2019, 2, 10)
        reg_class_name = 'Yoga'
        paper_price = 1000
        paper_name = 'Maupa'
        reg_class, class_unit = self.create_class_and_unit(
            reg_class_name, unit_date
        )
        paper = Paper.objects.create(
            name=paper_name,
            price=paper_price,
            number_of_uses=1
        )
        self.add_participant_to_class_unit(class_unit, paper_used=paper)

        res = get_detailed_teachers_salary_for_period(
            self.teacher, unit_date, unit_date
        )
        self.assertEqual(
            res[0].sum_teachers_share(), paper_price/2
        )
        unit_payments = res[0].unit_payments[0]
        self.assertEqual(unit_payments.payment_counts[paper.id], 1)

    def test_includes_units_from_different_classes(self):
        unit_date = date(2019, 2, 10)
        yoga_name = 'Yoga'
        beer_eating_name = 'BeerEating'
        yoga_class, yoga_unit = self.create_class_and_unit(
            yoga_name, unit_date
        )
        beer_eating_class, beer_eating_unit = self.create_class_and_unit(
            beer_eating_name, unit_date
        )
        paper_price = 1000
        paper_name = 'Maupa'
        paper = Paper.objects.create(
            name=paper_name,
            price=paper_price,
            number_of_uses=1
        )
        self.add_participant_to_class_unit(yoga_unit, paper)
        self.add_participant_to_class_unit(beer_eating_unit, paper)

        res = get_detailed_teachers_salary_for_period(
            self.teacher, unit_date, unit_date
        )

        self.assertEqual(len(res), 2)
        yoga_salary = next(
            class_payment for class_payment in res
            if class_payment.name==yoga_name
        )
        self.assertEqual(yoga_salary.sum_teachers_share(), paper_price/2)
        self.assertEqual(yoga_salary.unit_payments[0].payment_counts[paper.id], 1)

        beer_salary = next(
            class_payment for class_payment in res
            if class_payment.name==beer_eating_name
        )
        self.assertEqual(beer_salary.sum_teachers_share(), paper_price/2)
        self.assertEqual(beer_salary.unit_payments[0].payment_counts[paper.id], 1)

    def test_salary_for_unit_no_less_than_min_salary(self):
        min_salary = Constants.get_min_teachers_salary()
        unit_date = date(2019, 2, 10)
        reg_class_name = 'Yoga'
        paper_price = min_salary / 2
        paper_name = 'Maupa'
        reg_class, class_unit = self.create_class_and_unit(
            reg_class_name, unit_date
        )
        paper = Paper.objects.create(
            name=paper_name,
            price=paper_price,
            number_of_uses=1
        )
        self.add_participant_to_class_unit(class_unit, paper)

        res = get_detailed_teachers_salary_for_period(
            self.teacher, unit_date, unit_date
        )
        self.assertEqual(
            res[0].sum_teachers_share(), min_salary
        )

    def test_includes_payments_from_multiple_participants(self):
        unit_date = date(2019, 2, 10)
        reg_class_name = 'Yoga'
        paper_name = 'Maupa'
        paper_price = 1000
        one_time_price = 150
        reg_class, class_unit = self.create_class_and_unit(
            reg_class_name, unit_date, one_time_price=one_time_price
        )
        paper = Paper.objects.create(
            name=paper_name,
            price=paper_price,
            number_of_uses=1
        )
        self.add_participant_to_class_unit(class_unit, paper)
        self.add_participant_to_class_unit(class_unit)

        res = get_detailed_teachers_salary_for_period(
            self.teacher, unit_date, unit_date
        )

        self.assertEqual(
            res[0].sum_teachers_share(), (paper_price + one_time_price)/2
        )
