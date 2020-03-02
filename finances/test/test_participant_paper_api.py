from datetime import date, datetime, timedelta

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from finances.models import ParticipantPaper, Paper, Participant, Teacher, \
    RegularClass, ClassParticipation, ClassUnit

user_name = "Homer"
user_email = "123@bebe.com"
user_password = "123"
paper_name = 'Maupa'
participant_name = 'Oopyr'
teacer_name = 'Petyr'
class_name = 'EndlessRave'
test_date = date.today()


class ParticipantPaperTestCase(TestCase):

    def setUp(self):
        User = get_user_model()
        User.objects.create_user(user_name, user_email, user_password)
        self.create_paper()
        self.client.login(username=user_name, password=user_password)
        self.participant = Participant.objects.create(name=participant_name)
        self.participantPaper = ParticipantPaper.objects.create(
            participant=self.participant,
            paper=self.paper,
            date_purchased=test_date
        )
        self.teacher = Teacher.objects.create(name=teacer_name)
        self.regularClass = RegularClass.objects.create(
            name=class_name,
            start_date=test_date
        )

    def create_paper(self, days_valid=1):
        self.paper = Paper.objects.create(
            name=paper_name,
            price=0,
            number_of_uses=2,
            days_valid=days_valid
        )

    def create_classUnit(self, date=test_date):
        self.classUnit = ClassUnit.objects.create(
            regular_class=self.regularClass,
            date=date,
            teacher=self.teacher
        )

    def create_classParticipation(self):
        self.classParticipation = ClassParticipation.objects.create(
            class_unit=self.classUnit,
            participant=self.participant,
            paper_used=self.participantPaper
        )

    def test_denies_unauthorised_access(self):
        self.client.logout()
        response = self.client.get(
            reverse("participant_papers", kwargs={
                    'participant_id': self.participant.id})
        )
        self.assertEqual(response.status_code, 401)

    def test_can_not_found_participant_with_not_existing_id(self):
        response = self.client.get(
            reverse('participant_papers', kwargs={
                    'participant_id': self.participant.id+1})
        )
        self.assertEqual(response.status_code, 404)

    def test_response_for_participant_with_existing_id(self):
        self.create_classUnit()
        self.create_classParticipation()
        response = self.client.get(
            reverse('participant_papers', kwargs={
                    'participant_id': self.participant.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['participantPapers'][0], {
                         'id': self.participant.id,
                         'days_in_use': (date.today() - test_date).days,
                         'times_used': 1,
                         'name': 'Maupa',
                         'tentatively_expired': False
                         })

    def test_response_when_paper_exceeded_number_of_uses(self):
        self.create_classUnit()
        self.create_classParticipation()
        self.create_classParticipation()
        response = self.client.get(
            reverse('participant_papers', kwargs={
                    'participant_id': self.participant.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['participantPapers']), 0)

    def test_response_when_paper_exceeded_number_of_days_valid(self):
        self.create_classUnit(date=date(2020, 1, 1))
        self.create_classParticipation()
        response = self.client.get(
            reverse('participant_papers', kwargs={
                    'participant_id': self.participant.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['participantPapers']), 0)

    def test_response_when_paper_tentatively_expired(self):
        self.create_classUnit(date=(date.today()-timedelta(days=2)))
        self.create_classParticipation()
        response = self.client.get(
            reverse('participant_papers', kwargs={
                    'participant_id': self.participant.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['participantPapers'][0], {
                         'id': self.participant.id,
                         'days_in_use': (date.today() - (date.today()-timedelta(days=2))).days,
                         'times_used': 1,
                         'name': 'Maupa',
                         'tentatively_expired': True
                         })
