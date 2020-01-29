from datetime import date

from django.test import TestCase

from finances.models import Teacher, RegularClass, ClassUnit, Participant, ClassParticipation
from finances.models.constants import MIN_TEACHERS_SALARY

# res['Йога']['мега папірець'][date(2019, 12, 1)]
UNIT_SALARY_LABEL = 'всього за заняття'


class TestSalary(TestCase):

    def setUp(self):
        self.teacher = Teacher.objects.create(name='Homer')

    def test_without_classes(self):
        res = self.teacher.get_detailed_salary_for_period(
            '2019-02-01', '2019-02-03')
        self.assertDictEqual(res, {})

    def test_without_participants(self):
        unit_date = date(2019, 2, 10)
        reg_class_name = 'Yoga'
        reg_class = RegularClass.objects.create(
            name=reg_class_name, start_date='2019-02-01')
        class_unit = ClassUnit.objects.create(regular_class=reg_class,
                                              date=unit_date,
                                              teacher=self.teacher)
        res = self.teacher.get_detailed_salary_for_period(
            unit_date, unit_date)
        self.assertEqual(
            res[reg_class_name][UNIT_SALARY_LABEL][unit_date],
            MIN_TEACHERS_SALARY
        )

    def test_onetime_price(self):
        unit_date = date(2019, 2, 10)
        reg_class_name = 'Yoga'
        reg_class_price = 500
        reg_class = RegularClass.objects.create(
            name=reg_class_name, start_date='2019-02-01', one_time_price=reg_class_price)
        class_unit = ClassUnit.objects.create(regular_class=reg_class,
                                              date=unit_date,
                                              teacher=self.teacher)
        participant = Participant.objects.create(name='Oopyr')
        ClassParticipation.objects.create(
            class_unit=class_unit, participant=participant, paid_one_time_price=True)
        res = self.teacher.get_detailed_salary_for_period(
            unit_date, unit_date)
        self.assertEqual(
            res[reg_class_name][UNIT_SALARY_LABEL][unit_date],
            reg_class_price/2
        )
