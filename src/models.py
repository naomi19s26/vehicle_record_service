from . import db
from sqlalchemy import func, Index

class Vehicle(db.Model):
    __tablename__ = 'vehicle_db'
    
    vin = db.Column(db.String, primary_key=True) 
    manufacturer_name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    horse_power = db.Column(db.Integer, nullable=False)
    model_name = db.Column(db.String, nullable=False)
    model_year = db.Column(db.Integer, nullable=False)
    purchase_price = db.Column(db.Numeric(10, 2), nullable=False)
    fuel_type = db.Column(db.String, nullable=False)
    
    __table_args__ = (
        Index('ix_vehicle_vin_lower', func.lower(vin), unique=True),
    )
    def to_dict(self):
        return {
            "vin": self.vin,
            "manufacturer_name": self.manufacturer_name,
            "description": self.description,
            "horse_power": self.horse_power,
            "model_name": self.model_name,
            "model_year": self.model_year,
            "purchase_price": float(self.purchase_price),
            "fuel_type": self.fuel_type
        }
