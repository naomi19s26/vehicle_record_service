from flask import request, jsonify
from .models import Vehicle
from . import db
import re

def get_vehicles():
    try:
        vehicles = Vehicle.query.all()
        resulting_vehicles = [vehicle.to_dict() for vehicle in vehicles]
        return jsonify(resulting_vehicles), 200
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

def get_vehicle(vin):
    try:
        requested_vehicle = Vehicle.query.filter_by(vin=vin.lower()).first()
        if requested_vehicle:
            return jsonify(requested_vehicle.to_dict()), 200
        return jsonify({"error": "Vehicle not found"}), 404
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500
    
def create_vehicle():
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
            
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({'error': 'Invalid JSON format'}), 400
            
        if not data: 
            return jsonify({'errors': ['Request body cannot be empty']}), 422
        
        validation_errors = validate_vehicle_data(data, is_update=False)
        if validation_errors:
            return jsonify({'errors': validation_errors}), 422
        
        vin = data["vin"].lower()
        if Vehicle.query.filter_by(vin=vin).first():
            return jsonify({"error": "Vehicle with this VIN already exists"}), 409

        vehicle = Vehicle(
            vin=vin,
            manufacturer_name=data['manufacturer_name'],
            description=data.get('description'),
            horse_power=data.get('horse_power', 0), 
            model_name=data['model_name'],
            model_year=data['model_year'],
            purchase_price=float(data['purchase_price']),
            fuel_type=data['fuel_type']
        )
        
        db.session.add(vehicle)
        db.session.commit()
        return jsonify(vehicle.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500
        
def update_vehicle(vin):
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({'error': 'Invalid JSON format'}), 400
        
        requested_vehicle = Vehicle.query.filter_by(vin=vin.lower()).first()
        if not requested_vehicle:
            return jsonify({'error': f'Vehicle with VIN {vin} not found'}), 404
        
        validation_errors = validate_vehicle_data(data, is_update=True)
        if validation_errors:
            return jsonify({'errors': validation_errors}), 422

        if 'vin' in data and data['vin'].lower() != vin.lower():
            return jsonify({'error': 'Cannot change VIN'}), 422
        
        update_fields = ['manufacturer_name', 'description', 'horse_power',
                        'model_name', 'model_year', 'purchase_price', 'fuel_type']
        
        for field in update_fields:
            if field in data:
                setattr(requested_vehicle, field, data[field])
    
        db.session.commit()
        return jsonify(requested_vehicle.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500

def delete_vehicle(vin):
    try:
        requested_vehicle = Vehicle.query.filter_by(vin=vin.lower()).first()
        if not requested_vehicle:
            return jsonify({"error": "Vehicle not found"}), 404
        
        db.session.delete(requested_vehicle)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500

def validate_vehicle_data(data, is_update=False):
    errors = []
    if not is_update:
        if 'vin' not in data or not data['vin']:
            errors.append("VIN is required")
    
    if 'vin' in data and data['vin']:
        vin = data['vin'].upper().strip()
        if not re.match(r'^[A-HJ-NPR-Z0-9]{17}$', vin):
            errors.append("VIN must be exactly 17 alphanumeric characters (excluding I, O, Q)")

    if not is_update:
        required_fields = ['manufacturer_name', 'model_name', 'model_year', 
                          'purchase_price', 'fuel_type']
        for field in required_fields:
            if field not in data or data[field] is None:
                errors.append(f"{field.replace('_', ' ').title()} is required")
    
    if 'horse_power' in data and data['horse_power'] is not None:
        if not isinstance(data['horse_power'], int) or data['horse_power'] < 0:
            errors.append("Horse power must be a positive integer")
    
    if 'model_year' in data and data['model_year'] is not None:
        if not isinstance(data['model_year'], int) or data['model_year'] < 1886:
            errors.append("Model year must be a valid year")
    
    if 'purchase_price' in data and data['purchase_price'] is not None:
        try:
            price = float(data['purchase_price'])
            if price < 0:
                errors.append("Purchase price must be positive")
        except (ValueError, TypeError):
            errors.append("Purchase price must be a valid decimal number")

    valid_fuel_types = ['Gasoline', 'Diesel', 'Electric', 'Hybrid', 'Hydrogen']
    if 'fuel_type' in data and data['fuel_type']:
        if data['fuel_type'] not in valid_fuel_types:
            errors.append(f"Fuel type must be one of: {', '.join(valid_fuel_types)}")
    
    if not errors:
        return None
    return errors