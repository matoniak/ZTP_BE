import enum
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookings.db'  # Zmień na preferowaną bazę danych
db = SQLAlchemy(app)
CORS(app)

# WAŻNE: To są PRZYKŁADOWE wartości. ZASTĄP je wartościami z Twojego frontendu!
class PricingPlansEnum(enum.Enum):
    STANDARD = "Standardowy"  # Przykład
    PREMIUM = "Premium"      # Przykład
    VIP = "Vip"            # Przykład
    EARLY_BIRD = "Wczesna rezerwacja" # Dodatkowy przykład

    # Jeśli w frontendzie masz np.:
    # export enum PricingPlans {
    #     BASIC = "Podstawowy",
    #     PLUS = "Rozszerzony",
    #     ULTIMATE = "Ultymatywny",
    # }
    # To tutaj MUSI być:
    # class PricingPlansEnum(enum.Enum):
    #     BASIC = "Podstawowy"
    #     PLUS = "Rozszerzony"
    #     ULTIMATE = "Ultymatywny"

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
        try:
            start_date = datetime.strptime(data['startDate'], '%Y-%m-%d').date()
            end_date = datetime.strptime(data['endDate'], '%Y-%m-%d').date()
            pricing_plans = PricingPlansEnum(data.get('pricingPlans')) if data.get('pricingPlans') else None
            new_booking = RoomBooking(name=data['name'], surname=data['surname'], start_date=start_date, end_date=end_date, pricing_plans=pricing_plans)
            db.session.add(new_booking)
            db.session.commit()
            return jsonify(new_booking.to_dict()), 201
        except (ValueError, KeyError):
            return jsonify({"error": "Invalid data"}), 400

    elif request.method == 'PUT':
        data = request.get_json()
        booking = RoomBooking.query.get(data.get('id'))
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        try:
            booking.name = data.get('name')
            booking.surname = data.get('surname')
            booking.start_date = datetime.strptime(data['startDate'], '%Y-%m-%d').date()
            booking.end_date = datetime.strptime(data['endDate'], '%Y-%m-%d').date()
            pricing_plans = PricingPlansEnum(data.get('pricingPlans')) if data.get('pricingPlans') else None
            db.session.commit()
            return jsonify(booking.to_dict()), 200
        except (ValueError, KeyError):
            return jsonify({"error": "Invalid data"}), 400

    elif request.method == 'DELETE':
        id = request.args.get('id')
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