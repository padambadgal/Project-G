# ai/predict.py
import numpy as np
from config.settings import MODEL_PATH, SCALER_PATH, ENCODER_PATH
from ai.train_model import ModelTrainer
from ai.preprocess import DataPreprocessor

class DiseasePredictor:
    def __init__(self):
        self.model = None
        self.preprocessor = DataPreprocessor()
        self.trainer = ModelTrainer()
    
    def load_model(self):
        """Load the trained model and preprocessors"""
        self.model = self.trainer.load_model()
        if self.model:
            self.preprocessor.load_preprocessors()
            return True
        return False
    
    def train_and_load_model(self):
        """Train the model and load it"""
        self.trainer.load_and_prepare_data()
        self.trainer.train_model()
        self.trainer.save_model()
        self.trainer.evaluate_model()
        return self.load_model()
    
    def predict_disease(self, symptoms_dict):
        """Predict disease based on symptoms"""
        try:
            # Preprocess input
            input_scaled = self.preprocessor.preprocess_single_input(symptoms_dict)
            
            # Predict
            prediction = self.model.predict(input_scaled)
            probabilities = self.model.predict_proba(input_scaled)
            
            # Get disease name
            disease = self.preprocessor.label_encoder.inverse_transform(prediction)[0]
            
            # Get confidence
            confidence = np.max(probabilities)
            
            # Get probability for each disease
            disease_probabilities = {}
            for i, disease_name in enumerate(self.preprocessor.label_encoder.classes_):
                disease_probabilities[disease_name] = probabilities[0][i]
            
            return {
                'disease': disease,
                'confidence': confidence,
                'probabilities': disease_probabilities
            }
        except Exception as e:
            print(f"Prediction error: {e}")
            return None
    
    def get_symptoms_required(self):
        """Get list of required symptoms for prediction"""
        return self.preprocessor.feature_names