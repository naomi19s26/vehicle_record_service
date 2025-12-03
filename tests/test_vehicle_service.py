import pytest
import json
from sqlalchemy import inspect

@pytest.fixture
def app():
    from src.app import app

    original_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
    original_testing = app.config.get('TESTING')
    
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    from src import db

    with app.app_context():
        db.drop_all()
        db.create_all()
        
        yield app
    
        db.session.remove()
        if app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///:memory:':
            db.drop_all()
    
        app.config['SQLALCHEMY_DATABASE_URI'] = original_uri
        app.config['TESTING'] = original_testing

@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_vehicle_data():
    return {
        "vin": "1hgcm82633a004352",
        "manufacturer_name": "Honda",
        "description": "Civic LX",
        "horse_power": 158,
        "model_name": "Civic",
        "model_year": 2020,
        "purchase_price": 22000.00,
        "fuel_type": "Gasoline"
    }

@pytest.fixture
def created_vehicle(client, sample_vehicle_data):
    response = client.post(
        "/vehicle",
        data=json.dumps(sample_vehicle_data),
        content_type='application/json'
    )
    return response.get_json()

def test_create_vehicle_success(client, sample_vehicle_data):
    response = client.post(
        "/vehicle",
        data=json.dumps(sample_vehicle_data),
        content_type='application/json'
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.get_json()}")
    
    assert response.status_code == 201
    data = response.get_json()
    assert data["vin"] == "1hgcm82633a004352"
    assert data["manufacturer_name"] == "Honda"
    assert data["model_name"] == "Civic"

def test_create_vehicle_missing_required_field(client, sample_vehicle_data):
    data = sample_vehicle_data.copy()
    del data["vin"]
    
    response = client.post(
        "/vehicle",
        data=json.dumps(data),
        content_type='application/json'
    )
    
    assert response.status_code == 422
    data = response.get_json()
    assert "errors" in data
    assert any("VIN" in error for error in data["errors"])

def test_create_vehicle_invalid_vin_format(client, sample_vehicle_data):
    data = sample_vehicle_data.copy()
    data["vin"] = "123"
    
    response = client.post(
        "/vehicle",
        data=json.dumps(data),
        content_type='application/json'
    )
    
    assert response.status_code == 422
    response_data = response.get_json()
    assert "errors" in response_data

def test_create_vehicle_duplicate_vin(client, sample_vehicle_data):
    response = client.post(
        "/vehicle",
        data=json.dumps(sample_vehicle_data),
        content_type='application/json'
    )
    assert response.status_code == 201
    
    response = client.post(
        "/vehicle",
        data=json.dumps(sample_vehicle_data),
        content_type='application/json'
    )
    assert response.status_code == 409

def test_create_vehicle_invalid_json(client):
    response = client.post(
        "/vehicle",
        data="invalid json",
        content_type='application/json'
    )
    assert response.status_code == 400

def test_get_vehicle_success(client, created_vehicle):
    vin = created_vehicle["vin"]
    response = client.get(f"/vehicle/{vin}")
    
    assert response.status_code == 200
    data = response.get_json()
    assert data["vin"] == vin
    assert data["manufacturer_name"] == "Honda"

def test_get_vehicle_case_insensitive(client, created_vehicle):
    response = client.get("/vehicle/1hgcm82633a004352")
    
    assert response.status_code == 200
    data = response.get_json()
    assert data["vin"] == "1hgcm82633a004352"

def test_get_vehicle_not_found(client):
    response = client.get("/vehicle/NONEXISTENT123456")
    
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data

def test_get_all_vehicles_empty(client):
    response = client.get("/vehicle")
    
    assert response.status_code == 200
    data = response.get_json()
    assert data == []

def test_get_all_vehicles_with_data(client, created_vehicle):
    response = client.get("/vehicle")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["vin"] == "1hgcm82633a004352"


def test_update_vehicle_success(client, created_vehicle):
    vin = created_vehicle["vin"]
    update_data = {
        "description": "Updated description",
        "model_year": 2022
    }
    
    response = client.put(
        f"/vehicle/{vin}",
        data=json.dumps(update_data),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert data["description"] == "Updated description"
    assert data["model_year"] == 2022
    assert data["manufacturer_name"] == "Honda"

def test_update_vehicle_not_found(client):
    update_data = {"description": "Updated"}
    
    response = client.put(
        "/vehicle/NONEXISTENT123456",
        data=json.dumps(update_data),
        content_type='application/json'
    )
    
    assert response.status_code == 404

def test_update_vehicle_invalid_data(client, created_vehicle):
    vin = created_vehicle["vin"]
    update_data = {
        "purchase_price": -1000
    }
    
    response = client.put(
        f"/vehicle/{vin}",
        data=json.dumps(update_data),
        content_type='application/json'
    )
    
    assert response.status_code == 422
    data = response.get_json()
    assert "errors" in data

def test_update_vehicle_cannot_change_vin(client, created_vehicle):
    vin = created_vehicle["vin"]
    update_data = {
        "vin": "NEWVIN12345678901"
    }
    
    response = client.put(
        f"/vehicle/{vin}",
        data=json.dumps(update_data),
        content_type='application/json'
    )
    
    assert response.status_code == 422
    data = response.get_json()
    assert "errors" in data
    
def test_delete_vehicle_success(client, created_vehicle):
    vin = created_vehicle["vin"]
    
    response = client.delete(f"/vehicle/{vin}")
    assert response.status_code == 204
    assert response.data == b''
    
    response = client.get(f"/vehicle/{vin}")
    assert response.status_code == 404

def test_delete_vehicle_not_found(client):
    response = client.delete("/vehicle/NONEXISTENT123456")
    assert response.status_code == 404

def test_create_vehicle_invalid_fuel_type(client, sample_vehicle_data):
    data = sample_vehicle_data.copy()
    data["fuel_type"] = "InvalidFuel"
    
    response = client.post(
        "/vehicle",
        data=json.dumps(data),
        content_type='application/json'
    )
    
    assert response.status_code == 422
    response_data = response.get_json()
    assert "errors" in response_data
    assert any("fuel type" in error.lower() for error in response_data["errors"])

def test_create_vehicle_negative_price(client, sample_vehicle_data):
    data = sample_vehicle_data.copy()
    data["purchase_price"] = -1000
    
    response = client.post(
        "/vehicle",
        data=json.dumps(data),
        content_type='application/json'
    )
    
    assert response.status_code == 422

def test_create_vehicle_invalid_year(client, sample_vehicle_data):
    data = sample_vehicle_data.copy()
    data["model_year"] = 1000  
    
    response = client.post(
        "/vehicle",
        data=json.dumps(data),
        content_type='application/json'
    )
    
    assert response.status_code == 422

def test_empty_request_body(client):
    response = client.post(
        "/vehicle",
        data=json.dumps({}),
        content_type='application/json'
    )
    
    assert response.status_code == 422

def test_extra_fields_ignored(client, sample_vehicle_data):
    data = sample_vehicle_data.copy()
    data["extra_field"] = "should be ignored"
    
    response = client.post(
        "/vehicle",
        data=json.dumps(data),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    data = response.get_json()
    assert "extra_field" not in data

def test_root_route(client):
    response = client.get("/")
    
    assert response.status_code == 200
    assert b"Hello, Vehicle Service!" in response.data

def test_multiple_vehicles(client):
    vehicles = []

    for i in range(5):
        data = {
            "vin": f"1hgcm82633a00435{i}",
            "manufacturer_name": f"Manufacturer{i}",
            "model_name": f"Model{i}",
            "model_year": 2020 + i,
            "purchase_price": 20000 + (i * 1000),
            "fuel_type": "Gasoline",
            "horse_power": 150 + (i * 10)
        }
        
        response = client.post(
            "/vehicle",
            data=json.dumps(data),
            content_type='application/json'
        )
        assert response.status_code == 201
        vehicles.append(data)
        
    response = client.get("/vehicle")
    assert response.status_code == 200
    all_vehicles = response.get_json()
    
    assert len(all_vehicles) == 5
    
    for i, vehicle in enumerate(all_vehicles):
        assert vehicle["vin"] == f"1hgcm82633a00435{i}"
        assert vehicle["manufacturer_name"] == f"Manufacturer{i}"


def test_create_vehicle_null_values(client, sample_vehicle_data):
    data = sample_vehicle_data.copy()
    data["manufacturer_name"] = None
    
    response = client.post(
        "/vehicle",
        data=json.dumps(data),
        content_type='application/json'
    )
    
    assert response.status_code == 422

def test_update_vehicle_empty_body(client, created_vehicle):
    vin = created_vehicle["vin"]
    
    response = client.put(
        f"/vehicle/{vin}",
        data=json.dumps({}),
        content_type='application/json'
    )

    assert response.status_code in [200, 400, 422]

def test_get_vehicle_special_characters(client):
    response = client.get("/vehicle/1hgcm82633a00435!")
    assert response.status_code == 404