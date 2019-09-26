from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework import status


class RegisterTest(APITestCase):
    def setUp(self):
        self.test_user = User.objects.create_user('testuser', 'testpassword')
        self.create_url = reverse('register')

    def test_create_user(self):
        data = {
            'username': 'adamvizly',
            'password': 'incorrect'
        }

        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], data['username'])
        self.assertFalse('password' in response.data)
