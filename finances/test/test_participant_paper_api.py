from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from finances.models import ParticipantPaper

user_name = "Homer"
user_email = "123@bebe.com"
user_password = "123"


class ParticipantPaperTestCase(TestCase):

    def setUp(self):
        User = get_user_model()
        User.objects.create_user(user_name, user_email, user_password)
        self.client.login(username=user_name, password=user_password)

    def test_denies_unauthorised_access(self):
        self.client.logout()
        response = self.client.get(
            reverse("participant_papers", kwargs={'participant_id': 0})
        )
        self.assertEqual(response.status_code, 401)

    def test_participant_id_out_of_range(self):
        response = self.client.get(
            reverse('participant_papers', kwargs={'participant_id': 0})
        )
        self.assertEqual(response.status_code, 404)

    def test_participant_id(self):
        pass
