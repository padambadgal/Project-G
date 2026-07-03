# config/settings.py
import os

# Database settings
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'hospital.db')

# AI Model settings
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'disease_model.pkl')
SCALER_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'scaler.pkl')
ENCODER_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'label_encoder.pkl')

# Dataset path
DATASET_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'datasets', 'disease_dataset.csv')

# App settings
APP_NAME = "AI Hospital Disease Prediction System"
VERSION = "1.0.0"