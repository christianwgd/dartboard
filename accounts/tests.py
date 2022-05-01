from django.contrib import auth
from django.test import TestCase
from django.urls import reverse
from faker import Faker


User = auth.get_user_model()


class IndexTest(TestCase):

    def setUp(self) -> None:
        self.fake = Faker('de_DE')
        self.credentials = {
            'username': self.fake.user_name(),
            'password': self.fake.password(),
        }
        self.user = User.objects.create_user(**self.credentials)

    def test_login(self):
        url = reverse('login')
        response = self.client.post(url, self.credentials, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'], self.user)
        self.assertTrue(self.user.is_authenticated)

    def test_logout(self):
        url = reverse('logout')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
