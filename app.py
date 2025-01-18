import enum
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookings.db'  # Zmień na preferowaną bazę danych
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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
    email = db.Column(db.String(100), nullable=False)
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


    with app.app_context():
        db.create_all()
  

@app.route('/api/bookings', methods=['GET', 'POST', 'PUT', 'DELETE'])
def bookings():
    if request.method == 'GET':
        bookings = RoomBooking.query.all()
        return jsonify([booking.to_dict() for booking in bookings]), 200

    elif request.method == 'POST':
        data = request.get_json()
        try:
            # Parsowanie daty z formatu ISO 8601
            start_date = datetime.fromisoformat(data['startDate'].replace('Z', '+00:00')).date()
            end_date = datetime.fromisoformat(data['endDate'].replace('Z', '+00:00')).date()

            pricing_plan = PricingPlansEnum(data['pricingPlans']) if data.get('pricingPlans') else None


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
            return jsonify(new_booking.to_dict()), 201
        except (ValueError, KeyError, TypeError) as e:
            db.session.rollback()
            return jsonify({"error": f"Invalid data: {str(e)}"}), 400

    elif request.method == 'PUT':
        data = request.get_json()
        booking = RoomBooking.query.get(data.get('id'))
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        try:
            # Aktualizacja danych
            start_date = datetime.fromisoformat(data['startDate'].replace('Z', '+00:00')).date()
            end_date = datetime.fromisoformat(data['endDate'].replace('Z', '+00:00')).date()
            pricing_plan = PricingPlansEnum(data['pricingPlans']) if data.get('pricingPlans') else None

            booking.name = data['name']
            booking.surname = data['surname']
            booking.email = data['email']
            booking.start_date = start_date
            booking.end_date = end_date
            booking.pricing_plans = pricing_plan

            db.session.commit()
            return jsonify(booking.to_dict()), 200
        except (ValueError, KeyError, TypeError) as e:
            return jsonify({"error": f"Invalid data: {str(e)}"}), 400

    elif request.method == 'DELETE':
        booking_id = request.args.get('id')
        try:
            booking_id = int(booking_id)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid booking ID'}), 400
        booking = RoomBooking.query.get(booking_id)
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        db.session.delete(booking)
        db.session.commit()
        return jsonify({'message': 'Booking deleted'}), 200

# Uruchomienie aplikacji
if __name__ == '__main__':
    app.run(debug=True)

print(app.url_map)