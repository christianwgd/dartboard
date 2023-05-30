from django.urls import reverse
from django.contrib import auth
from django.test import TestCase
from faker import Faker

from player.models import Player

User = auth.get_user_model()


class IndexTest(TestCase):

    def setUp(self) -> None:
        self.fake = Faker('de_DE')
        self.user = User.objects.create(
            username=self.fake.user_name(),
            first_name=self.fake.first_name(),
            last_name=self.fake.last_name(),
            password=self.fake.password()
        )
        self.player = Player.objects.create(
            user=self.user,
            nickname='Test'
        )

    def test_index_unauthenticated(self):
        response = self.client.get(reverse('home'))
        # Should be redirected to log in
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"{reverse('login')}?next=/")

    def test_index_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
