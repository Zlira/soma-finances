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

    def test_denies_unauthorised_access(self):
        response = self.client.get(
            reverse("participant_papers", kwargs={'participant_id': 1})
        )
        self.assertEqual(response.status_code, 401)
