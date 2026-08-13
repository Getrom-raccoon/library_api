from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

class UserAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='test@test.com', password='test123')

    def test_register(self):
        data = {
            'email': 'newuser@test.com',
            'password': 'newpass123',
            'phone': '123456789'
        }
        response = self.client.post('/api/users/register/', data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)

    def test_login(self):
        data = {
            'email': 'test@test.com',
            'password': 'test123'
        }
        response = self.client.post('/api/users/token/', data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)

    def test_profile(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/users/profile/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['email'], 'test@test.com')

    def test_unauthorized_access(self):
        client = APIClient()
        response = client.get('/api/loans/')
        self.assertEqual(response.status_code, 401)