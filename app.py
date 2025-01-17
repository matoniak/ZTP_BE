import enum
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookings.db'  # Zmień na preferowaną bazę danych
db = SQLAlchemy(app)
CORS(app)

# WAŻNE: ZASTĄP TE WARTOŚCI PRAWDZIWYMI WARTOŚCIAMI Z TWOJEGO FRONTENDU!
class PricingPlansEnum(enum.Enum):
    BASIC = "BASIC"      # Przykład - ZASTĄP!
    PLUS = "PLUS"       # Przykład - ZASTĄP!
    ULTIMATE = "ULTIMATE" # Przykład - ZASTĄP!
    # Dodaj inne wartości, jeśli istnieją w frontendzie.
    # PRZYKŁAD DOPASOWANIA:
    # Jeśli w frontendzie masz:
    # export enum PricingPlans {
    #     STANDARD = "Standardowy",
    #     PREMIUM = "Premium",
    #     VIP = "Vip",
    # }
    # To tutaj MUSI być:
    # class PricingPlansEnum(enum.Enum):
    #     STANDARD = "Standardowy"
    #     PREMIUM = "Premium"
    #     VIP = "Vip"

class RoomBooking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    pricing_plans = db.Column(db.Enum(PricingPlansEnum))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'surname': self.surname,
            'startDate': self.start_date.isoformat(),
            'endDate': self.end_date.isoformat(),
            'pricingPlans': self.pricing_plans.value if self.pricing_plans else None
        }

with app.app_context():
    db.create_all()

@app.route('/api', methods=['GET', 'POST', 'PUT', 'DELETE'])
def bookings():
    if request.method == 'GET':
        bookings = RoomBooking.query.all()
        return jsonify([booking.to_dict() for booking in bookings]), 200

    elif request.method == 'POST':
        data = request.get_json()
        print("Otrzymane dane POST:", data)
        try:
            start_date_str = data['startDate']
            end_date_str = data['endDate']

            # Parsowanie daty ISO 8601 z obsługą strefy czasowej 'Z'
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00')).date()
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00')).date()

            pricing_plans = PricingPlansEnum(data['pricingPlans']) if data.get('pricingPlans') else None # Poprawione pobieranie pricingPlans

            new_booking = RoomBooking(name=data['name'], surname=data['surname'], start_date=start_date, end_date=end_date, pricing_plans=pricing_plans)
            print("Obiekt do zapisu:", new_booking.to_dict())  # Log przed zapisem
            db.session.add(new_booking)
            db.session.flush() # Wymuszenie zapisu do bazy przed commitems
            db.session.commit()
            print("Zapisano do bazy danych!")  # Log po zapisie
            return jsonify(new_booking.to_dict()), 201
        except (ValueError, KeyError, TypeError, Exception) as e:
            db.session.rollback() # Cofnięcie transakcji w razie błędu
            print(f"Błąd POST (zapis/parsowanie): {e}")
            return jsonify({"error": f"Invalid data - Sprawdź format daty (YYYY-MM-DDT00:00:00.000Z) i pricingPlans. Szczegóły: {str(e)}"}), 400 # Dodany szczegółowy komunikat błędu

    elif request.method == 'PUT':
        data = request.get_json()
        print("Otrzymane dane PUT:", data)
        booking = RoomBooking.query.get(data.get('id'))
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        try:
            start_date_str = data['startDate']
            end_date_str = data['endDate']
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00')).date()
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00')).date()
            pricing_plans = PricingPlansEnum(data.get('pricingPlans')) if data.get('pricingPlans') else None
            booking.name = data['name']
            booking.surname = data['surname']
            booking.start_date = start_date
            booking.end_date = end_date
            booking.pricing_plans = pricing_plans
            db.session.commit()
            return jsonify(booking.to_dict()), 200
        except (ValueError, KeyError, TypeError, Exception) as e:
            print(f"Błąd PUT: {e}")
            return jsonify({"error": f"Invalid data - Sprawdź format daty (YYYY-MM-DDT00:00:00.000Z) i pricingPlans. Szczegóły: {str(e)}"}), 400

    elif request.method == 'DELETE':
        id = request.args.get('id')
        print("Otrzymane ID do usunięcia:", id)
        try:
            id = int(id)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid booking id'}), 400
        booking = RoomBooking.query.get(id)
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        db.session.delete(booking)
        db.session.commit()
        return jsonify({'message': 'Booking deleted'}), 200

if __name__ == '__main__':
    app.run(debug=True)