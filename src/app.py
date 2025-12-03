from src import create_app
from .controllers import (
    get_vehicle, get_vehicles, 
    create_vehicle, update_vehicle, 
    delete_vehicle
)

app = create_app()

@app.route("/")
def hello():
    return "Hello, Vehicle Service!"

@app.route("/vehicle", methods=['GET'])
def route_get_vehicles():
    return get_vehicles()

@app.route("/vehicle/<vin>", methods=['GET'])
def route_get_vehicle(vin):
    return get_vehicle(vin)

@app.route("/vehicle", methods=['POST'])
def route_create_vehicle():
    return create_vehicle()

@app.route("/vehicle/<vin>", methods=['PUT'])
def route_update_vehicle(vin):
    return update_vehicle(vin)

@app.route("/vehicle/<vin>", methods=['DELETE'])
def route_delete_vehicle(vin):
    return delete_vehicle(vin)

if __name__ == "__main__":
    with app.app_context():
        from . import db
        db.create_all()
    app.run(debug=True)
