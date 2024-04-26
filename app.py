from flask import Flask, jsonify, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_swagger_ui import get_swaggerui_blueprint
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./watering_system.db'
db = SQLAlchemy(app)

# Swagger UI
SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/static/swagger.json'  # Our API url (can of course be a local resource)

swagger_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Watering System API"
    }
)
app.register_blueprint(swagger_blueprint, url_prefix=SWAGGER_URL)

# Models
class Sensor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    address = db.Column(db.String(100))
    bus = db.Column(db.Integer)

class Valve(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    pin = db.Column(db.Integer)

class PlantBed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    valve_id = db.Column(db.Integer, db.ForeignKey('valve.id'))
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensor.id'))
    active = db.Column(db.Boolean, default=True)

class Reading(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensor.id'), nullable=False)

# Routes
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

# Route to serve the JavaScript file
@app.route('/app.js')
def app_js():
    return send_from_directory('static', 'app.js')

@app.route('/api/sensor', methods=['GET'])
def get_sensors():
    sensors = Sensor.query.all()
    return jsonify([{'id': sensor.id, 'name': sensor.name, 'address': sensor.address, 'bus': sensor.bus} for sensor in sensors])

@app.route('/api/sensor', methods=['POST'])
def create_sensor():
    data = request.json
    sensor = Sensor(name=data['name'], address=data['address'], bus=data['bus'])
    db.session.add(sensor)
    db.session.commit()
    return jsonify({'id': sensor.id}), 201

@app.route('/api/sensor/<int:sensor_id>', methods=['PUT'])
def update_sensor(sensor_id):
    data = request.json
    sensor = Sensor.query.get_or_404(sensor_id)
    sensor.name = data['name']
    sensor.address = data['address']
    sensor.bus = data['bus']
    db.session.commit()
    return jsonify({'message': 'Sensor updated successfully'})

@app.route('/api/sensor/<int:sensor_id>', methods=['DELETE'])
def delete_sensor(sensor_id):
    sensor = Sensor.query.get_or_404(sensor_id)
    db.session.delete(sensor)
    db.session.commit()
    return jsonify({'message': 'Sensor deleted successfully'})

@app.route('/api/valve', methods=['GET'])
def get_valves():
    valves = Valve.query.all()
    return jsonify([{'id': valve.id, 'name': valve.name, 'pin': valve.pin} for valve in valves])

@app.route('/api/valve', methods=['POST'])
def create_valve():
    data = request.json
    valve = Valve(name=data['name'], pin=data['pin'])
    db.session.add(valve)
    db.session.commit()
    return jsonify({'id': valve.id}), 201

@app.route('/api/valve/<int:valve_id>', methods=['PUT'])
def update_valve(valve_id):
    data = request.json
    valve = Valve.query.get_or_404(valve_id)
    valve.name = data['name']
    valve.pin = data['pin']
    db.session.commit()
    return jsonify({'message': 'Valve updated successfully'})

@app.route('/api/valve/<int:valve_id>', methods=['DELETE'])
def delete_valve(valve_id):
    valve = Valve.query.get_or_404(valve_id)
    db.session.delete(valve)
    db.session.commit()
    return jsonify({'message': 'Valve deleted successfully'})

@app.route('/api/plantbed', methods=['GET'])
def get_plantbeds():
    plantbeds = PlantBed.query.all()
    return jsonify([{'id': plantbed.id, 'name': plantbed.name, 'valve_id': plantbed.valve_id, 'sensor_id': plantbed.sensor_id, 'active': plantbed.active} for plantbed in plantbeds])

@app.route('/api/plantbed', methods=['POST'])
def create_plantbed():
    data = request.json
    plantbed = PlantBed(name=data['name'], valve_id=data['valve_id'], sensor_id=data['sensor_id'], active=data['active'])
    db.session.add(plantbed)
    db.session.commit()
    return jsonify({'id': plantbed.id}), 201

@app.route('/api/plantbed/<int:plantbed_id>', methods=['PUT'])
def update_plantbed(plantbed_id):
    data = request.json
    plantbed = PlantBed.query.get_or_404(plantbed_id)
    plantbed.name = data['name']
    plantbed.valve_id = data['valve_id']
    plantbed.sensor_id = data['sensor_id']
    plantbed.active = data['active']
    db.session.commit()
    return jsonify({'message': 'PlantBed updated successfully'})

@app.route('/api/plantbed/<int:plantbed_id>', methods=['DELETE'])
def delete_plantbed(plantbed_id):
    plantbed = PlantBed.query.get_or_404(plantbed_id)
    db.session.delete(plantbed)
    db.session.commit()
    return jsonify({'message': 'PlantBed deleted successfully'})

@app.route('/api/plantbed/<int:plantbed_id>/activate', methods=['PUT'])
def activate_plantbed(plantbed_id):
    plantbed = PlantBed.query.get_or_404(plantbed_id)
    plantbed.active = True
    db.session.commit()
    return jsonify({'message': 'PlantBed activated successfully'})

@app.route('/api/plantbed/<int:plantbed_id>/deactivate', methods=['PUT'])
def deactivate_plantbed(plantbed_id):
    plantbed = PlantBed.query.get_or_404(plantbed_id)
    plantbed.active = False
    db.session.commit()
    return jsonify({'message': 'PlantBed deactivated successfully'})

@app.route('/api/readings', methods=['GET'])
def get_readings():
    from_timestamp = request.args.get('from')
    to_timestamp = request.args.get('to')
    
    try:
        from_datetime = datetime.strptime(from_timestamp, '%Y-%m-%d %H:%M:%S')
        to_datetime = datetime.strptime(to_timestamp, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return jsonify({'error': 'Invalid timestamp format. Please use format: YYYY-MM-DD HH:MM:SS'}), 400
    
    readings = Reading.query.filter(Reading.timestamp.between(from_datetime, to_datetime)).all()
    
    result = []
    for reading in readings:
        result.append({
            'id': reading.id,
            'timestamp': reading.timestamp,
            'temperature': reading.temperature,
            'humidity': reading.humidity,
            'sensor_id': reading.sensor_id
        })
    
    return jsonify(result)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
