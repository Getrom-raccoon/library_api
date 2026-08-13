from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.books.models import Book, Author

User = get_user_model()

class BookAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='test@test.com', password='test123')
        self.client.force_authenticate(user=self.user)
        self.author = Author.objects.create(name='Test Author')
        self.book = Book.objects.create(
            title='Test Book',
            author=self.author,
            genre='Fiction',
            isbn='1234567890123',
            published_year=2024,
            total_copies=5,
            available_copies=5
        )

    def test_list_books(self):
        response = self.client.get('/api/books/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_create_book(self):
        data = {
            'title': 'New Book',
            'author': self.author.id,
            'genre': 'Science',
            'isbn': '9876543210987',
            'published_year': 2023,
            'total_copies': 3,
            'available_copies': 3
        }
        response = self.client.post('/api/books/', data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Book.objects.count(), 2)

    def test_retrieve_book(self):
        response = self.client.get(f'/api/books/{self.book.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'Test Book')

    def test_update_book(self):
        data = {'title': 'Updated Book'}
        response = self.client.patch(f'/api/books/{self.book.id}/', data)
        self.assertEqual(response.status_code, 200)
        self.book.refresh_from_db()
        self.assertEqual(self.book.title, 'Updated Book')

    def test_delete_book(self):
        response = self.client.delete(f'/api/books/{self.book.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Book.objects.count(), 0)

    def test_negative_copies(self):
        data = {
            'title': 'Bad Book',
            'author': self.author.id,
            'genre': 'Fiction',
            'isbn': '9876543210987',
            'published_year': 2023,
            'total_copies': -1,
            'available_copies': -1
        }
        response = self.client.post('/api/books/', data)
        self.assertEqual(response.status_code, 400)