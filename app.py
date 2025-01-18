import enum
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookings.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Zalecane wyłączenie
db = SQLAlchemy(app)
CORS(app)

# WAŻNE: ZASTĄP TE WARTOŚCI PRAWDZIWYMI WARTOŚCIAMI Z TWOJEGO FRONTENDU!
class PricingPlansEnum(enum.Enum):
    BASIC = "BASIC"      # Przykład - ZASTĄP!
    PLUS = "PLUS"       # Przykład - ZASTĄP!
    ULTIMATE = "ULTIMATE" # Przykład - ZASTĄP!
    # ... dodaj inne wartości, jeśli istnieją w frontendzie

class RoomBooking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)  # Dodane pole email
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    pricing_plans = db.Column(db.Enum(PricingPlansEnum))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'surname': self.surname,
            'email': self.email,
            'startDate': self.start_date.isoformat(),
            'endDate': self.end_date.isoformat(),
            'pricingPlans': self.pricing_plans.value if self.pricing_plans else None
        }

# Utworzenie bazy danych TYLKO JEŚLI NIE ISTNIEJE
if not os.path.exists('bookings.db'):
    with app.app_context():
        db.create_all()
    print("Utworzono nową bazę danych: bookings.db") # Dodany komunikat

@app.route('/api/bookings', methods=['GET', 'POST', 'PUT', 'DELETE'])
def bookings():
    # ... (endpointy bez zmian, z logami debugowania)
    if request.method == 'POST':
        data = request.get_json()
        print("Otrzymane dane POST:", data)
        try:
            start_date_str = data['startDate']
            end_date_str = data['endDate']

            # Parsowanie daty ISO 8601 z obsługą strefy czasowej 'Z'
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00')).date()
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00')).date()

            pricing_plans = PricingPlansEnum(data['pricingPlans']) if data.get('pricingPlans') else None

            new_booking = RoomBooking(name=data['name'], surname=data['surname'], email=data['email'], start_date=start_date, end_date=end_date, pricing_plans=pricing_plans)
            print("Obiekt do zapisu:", new_booking.to_dict())
            db.session.add(new_booking)
            db.session.flush()
            db.session.commit()
            print("Zapisano do bazy danych!")
            return jsonify(new_booking.to_dict()), 201
        except (ValueError, KeyError, TypeError, Exception) as e:
            db.session.rollback()
            print(f"Błąd POST (zapis/parsowanie): {e}")
            return jsonify({"error": f"Invalid data - Sprawdź format daty (YYYY-MM-DDT00:00:00.000Z) i pricingPlans. Szczegóły: {str(e)}"}), 400

    elif request.method == 'PUT':
        # ... (analogicznie do POST - dodaj logi i obsługę wyjątków)
        pass # dodane pass by nie wyskakiwał błąd
    elif request.method == 'DELETE':
        # ... (bez zmian)
        pass # dodane pass by nie wyskakiwał błąd

# Uruchomienie aplikacji
if __name__ == '__main__':
    app.run(debug=True)