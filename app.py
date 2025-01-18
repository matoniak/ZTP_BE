import enum
import os
from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)  # Włącz CORS na początku

# Ustawienie ścieżki do bazy danych (ABSOLUTNIE KLUCZOWE!)
db_path = os.path.join(app.root_path, 'bookings.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class PricingPlansEnum(enum.Enum):
    BASIC = "BASIC"
    PLUS = "PLUS"
    ULTIMATE = "ULTIMATE"

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_

class RoomBooking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    pricing_plans = db.Column(db.Enum(PricingPlansEnum), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'surname': self.surname,
            'email': self.email,
            'startDate': self.start_date.isoformat() if self.start_date else None, # Dodano obsługę None
            'endDate': self.end_date.isoformat() if self.end_date else None,     # Dodano obsługę None
            'pricingPlans': self.pricing_plans.value if self.pricing_plans else None
        }

# Utworzenie bazy danych TYLKO JEŚLI NIE ISTNIEJE
with app.app_context(): # Przeniesiono do bloku with app_context
    if not os.path.exists(db_path):
        db.create_all()
        print(f"Utworzono nową bazę danych: {db_path}")

@app.route('/api/bookings', methods=['GET', 'POST', 'PUT', 'DELETE'])
def bookings():
    if request.method == 'POST':
        try:
            data = request.get_json()
            print(f"Otrzymane dane POST: {data}") # Logowanie otrzymanych danych
            start_date = datetime.fromisoformat(data['startDate'].replace('Z', '+00:00')).date()
            end_date = datetime.fromisoformat(data['endDate'].replace('Z', '+00:00')).date()

            pricing_plans_value = data.get('pricingPlans')
            pricing_plan = PricingPlansEnum(pricing_plans_value) if pricing_plans_value and PricingPlansEnum.has_value(pricing_plans_value) else None

            new_booking = RoomBooking(
                name=data['name'],
                surname=data['surname'],
                email=data['email'],
                start_date=start_date,
                end_date=end_date,
                pricing_plans=pricing_plan
            )
            db.session.add(new_booking)
            db.session.commit()
            print("Dodano rezerwację:", new_booking.to_dict())
            return jsonify(new_booking.to_dict()), 201

        except (ValueError, KeyError, TypeError) as e:
            db.session.rollback()
            print(f"Błąd podczas dodawania rezerwacji: {e}") # Bardziej szczegółowe logowanie błędów
            return jsonify({"error": f"Nieprawidłowe dane: {str(e)}"}), 400

    elif request.method == 'GET': # Dodano obsługę GET
        bookings = RoomBooking.query.all()
        booking_list = [booking.to_dict() for booking in bookings]
        return jsonify(booking_list), 200

    elif request.method == 'PUT': # Dodano obsługę PUT (przykład)
        try:
            data = request.get_json()
            booking_id = data.get('id')
            booking = RoomBooking.query.get(booking_id)

            if booking:
                # Aktualizuj pola rezerwacji na podstawie danych z request.get_json()
                booking.name = data.get('name', booking.name) # Przykład aktualizacji imienia
                # ... aktualizuj inne pola ...
                db.session.commit()
                return jsonify(booking.to_dict()), 200
            else:
                return jsonify({"error": "Rezerwacja nie znaleziona"}), 404

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    elif request.method == 'DELETE': # Dodano obsługę DELETE (przykład)
        try:
            booking_id = request.args.get('id') # Pobierz ID z query parameters
            booking = RoomBooking.query.get(booking_id)
            if booking:
                db.session.delete(booking)
                db.session.commit()
                return jsonify({"message": "Rezerwacja usunięta"}), 200
            else:
                return jsonify({"error": "Rezerwacja nie znaleziona"}), 404
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Nieobsługiwana metoda"}), 405 # Zwracaj 405 Method Not Allowed

if __name__ == '__main__':
    with app.app_context(): # Dodano app_context
        db.create_all() # przeniesione tutaj
    app.run(debug=True, host='0.0.0.0', port=5000) # Jawne ustawienie hosta i portu