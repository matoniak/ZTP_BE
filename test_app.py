import unittest
from app import app, db, RoomBooking
from datetime import datetime
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class AppTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Konfiguracja wykonywana raz przed wszystkimi testami."""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' 
        cls.client = app.test_client()

    def setUp(self):
        """Konfiguracja wykonywana przed każdym testem."""
        with app.app_context():
            db.create_all()

    def tearDown(self):
        """Czyszczenie wykonywane po każdym teście."""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_get_empty_bookings(self):
        """Test pobierania listy rezerwacji (brak danych)."""
        response = self.client.get('/api/bookings')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

    def test_post_booking(self):
        """Test tworzenia nowej rezerwacji."""
        data = {
            "name": "Piotr",
            "surname": "Karkoszka",
            "email": "piotr.karkoszka@example.com",
            "startDate": "2025-01-18T00:00:00Z",
            "endDate": "2025-01-20T00:00:00Z",
            "pricingPlans": "BASIC"
        }
        response = self.client.post('/api/bookings', json=data)
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.get_json())  # Sprawdzenie, czy odpowiedź zawiera id

    def test_get_bookings_with_data(self):
        """Test pobierania listy rezerwacji (z danymi)."""
        # Najpierw dodaj rezerwację
        data = {
            "name": "Piotr",
            "surname": "Karkoszka",
            "email": "piotr.karkoszka@example.com",
            "startDate": "2025-01-18T00:00:00Z",
            "endDate": "2025-01-20T00:00:00Z",
            "pricingPlans": "BASIC"
        }
        self.client.post('/api/bookings', json=data)

        # Pobierz rezerwacje
        response = self.client.get('/api/bookings')
        self.assertEqual(response.status_code, 200)
        bookings = response.get_json()
        self.assertEqual(len(bookings), 1)  # Powinna być jedna rezerwacja
        self.assertEqual(bookings[0]['name'], "Piotr")

    def test_put_booking(self):
        """Test aktualizacji istniejącej rezerwacji."""
        # Najpierw dodaj rezerwację
        data = {
            "name": "Piotr",
            "surname": "Karkoszka",
            "email": "piotr.karkoszka@example.com",
            "startDate": "2025-01-18T00:00:00Z",
            "endDate": "2025-01-20T00:00:00Z",
            "pricingPlans": "BASIC"
        }
        response = self.client.post('/api/bookings', json=data)
        booking_id = response.get_json()["id"]

        # Zaktualizuj rezerwację
        update_data = {
            "id": booking_id,
            "name": "Piotr",
            "surname": "Karkoszka",
            "email": "piotr.updated@example.com",
            "startDate": "2025-01-19T00:00:00Z",
            "endDate": "2025-01-21T00:00:00Z",
            "pricingPlans": "PLUS"
        }
        response = self.client.put('/api/bookings', json=update_data)
        self.assertEqual(response.status_code, 200)
        booking = response.get_json()
        self.assertEqual(booking['email'], "piotr.updated@example.com")

    def test_delete_booking(self):
        """Test usunięcia istniejącej rezerwacji."""
        # Najpierw dodaj rezerwację
        data = {
            "name": "Piotr",
            "surname": "Karkoszka",
            "email": "piotr.karkoszka@example.com",
            "startDate": "2025-01-18T00:00:00Z",
            "endDate": "2025-01-20T00:00:00Z",
            "pricingPlans": "BASIC"
        }
        response = self.client.post('/api/bookings', json=data)
        booking_id = response.get_json()["id"]

        # Usuń rezerwację
        response = self.client.delete(f'/api/bookings?id={booking_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.get_json())
        self.assertEqual(response.get_json()['message'], 'Booking deleted')

        # Upewnij się, że rezerwacja została usunięta
        response = self.client.get('/api/bookings')
        self.assertEqual(len(response.get_json()), 0)


if __name__ == '__main__':
    unittest.main()
