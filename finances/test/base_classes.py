from django.test import TestCase

from django.contrib.auth import get_user_model


class SuperUserTestCase(TestCase):

    def setUp(self):
        super().setUp()
        User = get_user_model()
        username = 'me'
        password = 'mypassword'
        email = 'my@email.com'
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
        self.client.login(username=username, password=password)