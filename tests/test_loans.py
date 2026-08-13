from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from apps.books.models import Book, Author
from apps.loans.models import Loan

User = get_user_model()

class LoanAPITest(TestCase):
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
        self.loan = Loan.objects.create(
            user=self.user,
            book=self.book,
            due_date=timezone.now() + timedelta(days=7),
            returned=False
        )

    def test_list_loans(self):
        response = self.client.get('/api/loans/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_create_loan(self):
        self.book2 = Book.objects.create(
            title='Another Book',
            author=self.author,
            genre='Fiction',
            isbn='1234567890124',
            published_year=2024,
            total_copies=3,
            available_copies=3
        )
        data = {
            'book': self.book2.id,
            'due_date': (timezone.now() + timedelta(days=7)).isoformat()
        }
        response = self.client.post('/api/loans/', data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Loan.objects.count(), 2)
        self.book2.refresh_from_db()
        self.assertEqual(self.book2.available_copies, 2)

    def test_return_book(self):
        response = self.client.delete(f'/api/loans/{self.loan.id}/')
        self.assertEqual(response.status_code, 200)
        self.loan.refresh_from_db()
        self.assertTrue(self.loan.returned)
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 5)

    def test_borrow_unavailable_book(self):
        self.book.available_copies = 0
        self.book.save()
        data = {'book': self.book.id, 'due_date': (timezone.now() + timedelta(days=14)).isoformat()}
        response = self.client.post('/api/loans/', data)
        self.assertEqual(response.status_code, 400)

    def test_return_already_returned(self):
        loan = Loan.objects.create(user=self.user, book=self.book, due_date=timezone.now() + timedelta(days=14),
                                   returned=True)
        response = self.client.delete(f'/api/loans/{loan.id}/')
        self.assertEqual(response.status_code, 400)

    def test_view_other_user_loan(self):
        other_user = User.objects.create_user(email='other@test.com', password='test')
        loan = Loan.objects.create(user=other_user, book=self.book, due_date=timezone.now() + timedelta(days=14))
        response = self.client.get(f'/api/loans/{loan.id}/')
        self.assertEqual(response.status_code, 404)