from datetime import date

from django.test import TestCase

from finances.models import Teacher,\
    RegularClass, ClassUnit, Participant,\
    ClassParticipation, Paper, ParticipantPaper, Constants
from finances.accounting import get_detailed_teachers_salary_for_period

# res['Йога']['мега папірець'][date(2019, 12, 1)]
UNIT_SALARY_LABEL = 'всього за заняття'


class TestSalary(TestCase):

    def setUp(self):
        self.teacher = Teacher.objects.create(name='Homer')

    def test_without_classes(self):
        res = get_detailed_teachers_salary_for_period(
            self.teacher, '2019-02-01', '2019-02-03')
        self.assertDictEqual(res, {})

    def test_without_participants(self):
        unit_date = date(2019, 2, 10)
        reg_class_name = 'Yoga'
        reg_class = RegularClass.objects.create(
            name=reg_class_name, start_date='2019-02-01',
            one_time_price=100,
        )
        ClassUnit.objects.create(regular_class=reg_class,
                                 date=unit_date,
                                 teacher=self.teacher)
        res = get_detailed_teachers_salary_for_period(
            self.teacher, unit_date, unit_date)
        # if nobody was present at the class techer gets nothing
        self.assertEqual(
            res[reg_class_name][unit_date][UNIT_SALARY_LABEL], 0
        )

    def test_onetime_price(self):
        unit_date = date(2019, 2, 10)
        reg_class_name = 'Yoga'
        reg_class_price = 500
        reg_class = RegularClass.objects.create(
            name=reg_class_name,
            start_date='2019-02-01',
            one_time_price=reg_class_price
        )
        class_unit = ClassUnit.objects.create(
            regular_class=reg_class,
            date=unit_date,
            teacher=self.teacher
        )
        participant = Participant.objects.create(name='Oopyr')
        ClassParticipation.objects.create(
            class_unit=class_unit,
            participant=participant,
            paid_one_time_price=True
        )
        res = get_detailed_teachers_salary_for_period(
            self.teacher, unit_date, unit_date)
        self.assertEqual(
            res[reg_class_name][unit_date][UNIT_SALARY_LABEL],
            reg_class_price/2
        )

    def test_invalid_salary_period(self):
        unit_date = date(2019, 2, 10)
        date_before_class = date(2019, 2, 9)
        date_after_class = date(2019, 2, 11)
        reg_class_name = 'Yoga'
        reg_class = RegularClass.objects.create(
            name=reg_class_name,
            start_date='2019-02-01'
        )
        class_unit = ClassUnit.objects.create(
            regular_class=reg_class,
            date=unit_date,
            teacher=self.teacher
        )
        participant = Participant.objects.create(name='Oopyr')

        ClassParticipation.objects.create(
            class_unit=class_unit,
            participant=participant,
        )
        res = get_detailed_teachers_salary_for_period(
            self.teacher, date_before_class, date_before_class)
        self.assertEqual(res, {})

        res = get_detailed_teachers_salary_for_period(
            self.teacher, date_after_class, date_after_class)
        self.assertEqual(res, {})

    def test_other_teacher(self):
        unit_date = date(2019, 2, 10)
        reg_class_name = 'Yoga'
        other_teacher = Teacher.objects.create(name='Grishnak')
        reg_class = RegularClass.objects.create(
            name=reg_class_name,
            start_date='2019-02-01',
        )
        class_unit = ClassUnit.objects.create(
            regular_class=reg_class,
            date=unit_date,
            teacher=other_teacher
        )
        participant = Participant.objects.create(name='Oopyr')
        ClassParticipation.objects.create(
            class_unit=class_unit,
            participant=participant,
        )
        res = get_detailed_teachers_salary_for_period(
            self.teacher, unit_date, unit_date)
        self.assertEqual(res, {})

    def test_paper(self):
        unit_date = date(2019, 2, 10)
        reg_class_name = 'Yoga'
        paper_price = 1000
        paper_name = 'Maupa'
        reg_class = RegularClass.objects.create(
            name=reg_class_name, one_time_price=100,
            start_date='2019-02-01',
        )
        class_unit = ClassUnit.objects.create(
            regular_class=reg_class,
            date=unit_date,
            teacher=self.teacher
        )
        participant = Participant.objects.create(name='Oopyr')
        paper = Paper.objects.create(
            name=paper_name,
            price=paper_price,
            number_of_uses=1
        )
        participant_paper = ParticipantPaper.objects.create(
            participant=participant,
            paper=paper,
            date_purchased='2019-02-01'
        )
        ClassParticipation.objects.create(
            class_unit=class_unit,
            participant=participant,
            paper_used=participant_paper
        )
        res = get_detailed_teachers_salary_for_period(
            self.teacher, unit_date, unit_date)
        self.assertEqual(
            res[reg_class_name][unit_date][UNIT_SALARY_LABEL],
            paper_price/2
        )

    def test_multiple_regular_class(self):
        unit_date = date(2019, 2, 10)
        first_reg_class_name = 'Yoga'
        second_reg_class_name = 'BeerEating'
        paper_price = 1000
        paper_name = 'Maupa'
        first_reg_class = RegularClass.objects.create(
            name=first_reg_class_name, one_time_price=100,
            start_date='2019-02-01',
        )
        second_reg_class = RegularClass.objects.create(
            name=second_reg_class_name, one_time_price=100,
            start_date='2019-02-01',
        )
        first_class_unit = ClassUnit.objects.create(
            regular_class=first_reg_class,
            date=unit_date,
            teacher=self.teacher
        )
        second_class_unit = ClassUnit.objects.create(
            regular_class=second_reg_class,
            date=unit_date,
            teacher=self.teacher
        )
        participant = Participant.objects.create(name='Oopyr')
        paper = Paper.objects.create(
            name=paper_name,
            price=paper_price,
            number_of_uses=1
        )
        participant_paper = ParticipantPaper.objects.create(
            participant=participant,
            paper=paper,
            date_purchased='2019-02-01'
        )
        ClassParticipation.objects.create(
            class_unit=first_class_unit,
            participant=participant,
            paper_used=participant_paper
        )
        ClassParticipation.objects.create(
            class_unit=second_class_unit,
            participant=participant,
            paper_used=participant_paper
        )
        res = get_detailed_teachers_salary_for_period(
            self.teacher, unit_date, unit_date)
        self.assertEqual(
            res[first_reg_class_name][unit_date][UNIT_SALARY_LABEL],
            paper_price/2
        )
        self.assertEqual(
            res[second_reg_class_name][unit_date][UNIT_SALARY_LABEL],
            paper_price/2
        )

    def test_min_salary(self):
        unit_date = date(2019, 2, 10)
        reg_class_name = 'Yoga'
        paper_price = Constants.get_min_teachers_salary()/2
        paper_name = 'Maupa'
        reg_class = RegularClass.objects.create(
            name=reg_class_name, one_time_price=100,
            start_date='2019-02-01',
        )
        class_unit = ClassUnit.objects.create(
            regular_class=reg_class,
            date=unit_date,
            teacher=self.teacher
        )
        participant = Participant.objects.create(name='Oopyr')
        paper = Paper.objects.create(
            name=paper_name,
            price=paper_price,
            number_of_uses=1
        )
        participant_paper = ParticipantPaper.objects.create(
            participant=participant,
            paper=paper,
            date_purchased='2019-02-01'
        )
        ClassParticipation.objects.create(
            class_unit=class_unit,
            participant=participant,
            paper_used=participant_paper
        )
        res = get_detailed_teachers_salary_for_period(
            self.teacher, unit_date, unit_date)
        self.assertEqual(
            res[reg_class_name][unit_date][UNIT_SALARY_LABEL],
            Constants.get_min_teachers_salary()
        )

    def test_multiple_participants(self):
        unit_date = date(2019, 2, 10)
        reg_class_name = 'Yoga'
        paper_name = 'Maupa'
        paper_price = 1000
        one_time_price = 150
        reg_class = RegularClass.objects.create(
            name=reg_class_name,
            start_date='2019-02-01',
            one_time_price=one_time_price
        )
        class_unit = ClassUnit.objects.create(
            regular_class=reg_class,
            date=unit_date,
            teacher=self.teacher
        )
        first_participant = Participant.objects.create(name='Oopyr')
        second_participant = Participant.objects.create(name='Knoor')
        paper = Paper.objects.create(
            name=paper_name,
            price=paper_price,
            number_of_uses=1
        )
        participant_paper = ParticipantPaper.objects.create(
            participant=first_participant,
            paper=paper,
            date_purchased='2019-02-01'
        )
        ClassParticipation.objects.create(
            class_unit=class_unit,
            participant=first_participant,
            paper_used=participant_paper
        )
        ClassParticipation.objects.create(
            class_unit=class_unit,
            participant=second_participant,
            paid_one_time_price=True
        )
        res = get_detailed_teachers_salary_for_period(
            self.teacher, unit_date, unit_date)
        self.assertEqual(
            res[reg_class_name][unit_date][UNIT_SALARY_LABEL],
            (paper_price + one_time_price)/2
        )
