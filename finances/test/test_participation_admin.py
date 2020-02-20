from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse

from finances.models import RegularClass, Teacher, Participant, Paper, \
    ParticipantPaper, ClassUnit, ClassParticipation
from .base_classes import SuperUserTestCase


class TestParticipationAdmin(SuperUserTestCase):

    def setUp(self):
        super().setUp()
        self.regular_class = RegularClass.objects.create(
            name='Digesting class', start_date=date(1990, 1, 7))
        self.teacher = Teacher.objects.create(name="Super DJster")
        self.paper_with_limit = Paper.objects.create(
            name='Limited digest', price=100, number_of_uses=2
        )
        self.paper_without_limit = Paper.objects.create(
            name="Unlimited digest", price=1000,
        )

    def create_participant(self):
        return Participant.objects.create(name="Girl Unable To Digest")

    def create_participant_with_paper(self, paper_limited=True):
        paper = self.paper_with_limit if paper_limited else self.paper_without_limit
        participant = self.create_participant()
        participants_paper = ParticipantPaper.objects.create(
            paper=paper, participant=participant
        )
        return participant, participants_paper

    def expire_paper(self, participants_paper):
        past_date = date.today() - timedelta(participants_paper.paper.days_valid + 1)
        unit = ClassUnit.objects.create(
            regular_class=self.regular_class, date=past_date, teacher=self.teacher)
        ClassParticipation.objects.create(
            class_unit=unit, participant=participants_paper.participant,
            paper_used=participants_paper
        )

    def get_post_data(self, participations):
        data = {
            'regular_class': self.regular_class.id,
            'date': date.today(),
            'teacher': self.teacher.id,
            'comment': '',
            'classparticipation_set-TOTAL_FORMS': len(participations),
            'classparticipation_set-INITIAL_FORMS': '0',
        }
        for (index, (participant, paper_used, payed_on_time)) in enumerate(participations):
            field_prefix = f'classparticipation_set-{index}-'
            data.update({
                field_prefix + 'id': '',
                field_prefix + 'class_unit': '',
                field_prefix + 'participant': participant.id,
                field_prefix + 'paper_used': paper_used.id if paper_used else '',
            })
            if payed_on_time:
                data[field_prefix + 'paid_one_time_price'] = 'on'
        return data

    def test_can_save_class_unit_with_participants(self):
        participant, participants_paper = self.create_participant_with_paper()
        data = self.get_post_data([(participant, participants_paper, False)])
        url = reverse('admin:finances_classunit_add')
        response = self.client.post(url, data=data)

        # this is redirect after successfull post, but it can also mean something else
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('admin:finances_classunit_changelist'))

        self.assertEqual(self.regular_class.classunit_set.count(), 1)
        class_unit = self.regular_class.classunit_set.first()
        self.assertEqual(class_unit.teacher, self.teacher)
        self.assertEqual(class_unit.classparticipation_set.count(), 1)
        class_participation = class_unit.classparticipation_set.first()
        self.assertEqual(class_participation.participant, participant)
        self.assertEqual(class_participation.paper_used, participants_paper)
        self.assertFalse(class_participation.paid_one_time_price)

    def test_cannot_add_same_participant_twice(self):
        participant, participants_paper = self.create_participant_with_paper()
        data = self.get_post_data([
            (participant, participants_paper, False),
            (participant, participants_paper, False),
        ])

        url = reverse('admin:finances_classunit_add')
        response = self.client.post(url, data=data)

        # this is same page with errors marked, but it can also mean something else
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.regular_class.classunit_set.count(), 0)

        # TODO check messages or errors

    def test_doesnt_let_participant_use_someone_elses_paper(self):
        participant, participants_paper = self.create_participant_with_paper()
        participant_2, p_paper_2 = self.create_participant_with_paper()
        data = self.get_post_data([
            (participant, p_paper_2, False),
        ])

        url = reverse('admin:finances_classunit_add')
        response = self.client.post(url, data=data)

        # this is same page with errors marked, but it can also mean something else
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.regular_class.classunit_set.count(), 0)

        # TODO check messages or errors

    def test_participant_cannot_use_paper_and_pay_one_time_price(self):
        participant, participants_paper = self.create_participant_with_paper()
        data = self.get_post_data([(participant, participants_paper, True)])
        url = reverse('admin:finances_classunit_add')
        response = self.client.post(url, data=data)

        # this is same page with errors marked, but it can also mean something else
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.regular_class.classunit_set.count(), 0)

        # TODO check messages or errors

    def test_cannot_participate_without_payment(self):
        participant, participants_paper = self.create_participant_with_paper()

        data = self.get_post_data([(participant, None, False)])
        url = reverse('admin:finances_classunit_add')
        response = self.client.post(url, data=data)

        # this is same page with errors marked, but it can also mean something else
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.regular_class.classunit_set.count(), 0)

        # TODO check messages or errors

    def test_warns_when_expired_paper_is_used(self):
        participant, participants_paper = self.create_participant_with_paper()
        self.expire_paper(participants_paper)

        data = self.get_post_data([(participant, participants_paper, False)])
        url = reverse('admin:finances_classunit_add')
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('admin:finances_classunit_changelist'))

        # TODO check messages

    def test_doesnt_allow_to_use_expired_paper_without_use_limit(self):
        participant, participants_paper = self.create_participant_with_paper(paper_limited=False)
        self.expire_paper(participants_paper)

        data = self.get_post_data([(participant, participants_paper, False)])
        url = reverse('admin:finances_classunit_add')
        response = self.client.post(url, data=data)

        # this is same page with errors marked, but it can also mean something else
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.regular_class.classunit_set.count(), 0)

        # TODO check messages or errors

    def test_dosent_allow_to_use_paper_after_use_limit_reached(self):
        participant, participants_paper = self.create_participant_with_paper(paper_limited=False)
        for _ in range(2):
            class_unit = ClassUnit.objects.create(
                date=date.today(),
                regular_class=self.regular_class,
                teacher=self.teacher
            )
            ClassParticipation.objects.create(
                participant=participant, paper_used=participants_paper, class_unit=class_unit
            )

        data = self.get_post_data([(participant, participants_paper, False)])
        url = reverse('admin:finances_classunit_add')
        response = self.client.post(url, data=data)

        # this is same page with errors marked, but it can also mean something else
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.regular_class.classunit_set.count(), 0)

        # TODO check messages or errors