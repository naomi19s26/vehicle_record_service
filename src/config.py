class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://vehicle_service_user:vehicle_service_password@localhost:5432/vehicle_db"

config = {
    "development": DevelopmentConfig
}
