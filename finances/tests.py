from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from finances.models import Paper
# Create your tests here.

user_name = "Homer"
user_email = '123@bebe.com'
user_password = '123'


class PaperTestCase(TestCase):

    def setUp(self):
        User = get_user_model()
        User.objects.create_user(user_name, user_email, user_password)

    def test_denies_unauthorised_access(self):
        response = self.client.get(reverse("paper"))
        self.assertEqual(response.status_code, 401)

    def test_get_paper(self):
        name = str()
        price = int()
        paper = Paper.objects.create(name=name, price=price)
        self.client.login(username=user_name, password=user_password)
        response = self.client.get(reverse("paper"), {'paper_id': paper.id})
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result['name'], name)
        self.assertEqual(result['id'], paper.id)

    def test_paper_id_out_of_range(self):
        name = str()
        price = int()
        paper = Paper.objects.create(name=name, price=price)
        self.client.login(username=user_name, password=user_password)
        response = self.client.get(reverse("paper"), {'paper_id': paper.id+1})
        self.assertEqual(response.status_code, 404)
