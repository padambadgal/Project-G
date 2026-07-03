# ai/train_model.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os
from config.settings import MODEL_PATH
from ai.preprocess import DataPreprocessor

class ModelTrainer:
    def __init__(self):
        self.preprocessor = DataPreprocessor()
        self.model = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
    
    def load_and_prepare_data(self):
        """Load and prepare data for training"""
        # Load dataset
        df = self.preprocessor.load_dataset()
        
        # Preprocess
        X_scaled, y_encoded, X, y = self.preprocessor.preprocess_data(df)
        
        # Split data
        self.X_train, self.X_test, self.y_train, self.y_test = self.preprocessor.split_data(
            X_scaled, y_encoded
        )
        
        print(f"Training set size: {len(self.X_train)}")
        print(f"Test set size: {len(self.X_test)}")
        
        return self.X_train, self.X_test, self.y_train, self.y_test
    
    def train_model(self, n_estimators=100, max_depth=10, random_state=42):
        """Train the Random Forest model"""
        if self.X_train is None:
            self.load_and_prepare_data()
        
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state
        )
        
        self.model.fit(self.X_train, self.y_train)
        print("Model trained successfully")
        
        return self.model
    
    def evaluate_model(self):
        """Evaluate the trained model"""
        if self.model is None:
            print("Model not trained yet!")
            return None
        
        # Predictions
        y_pred = self.model.predict(self.X_test)
        
        # Accuracy
        accuracy = accuracy_score(self.y_test, y_pred)
        print(f"Model Accuracy: {accuracy:.2%}")
        
        # Classification Report
        print("\nClassification Report:")
        print(classification_report(self.y_test, y_pred, target_names=self.preprocessor.label_encoder.classes_))
        
        return accuracy
    
    def save_model(self):
        """Save the trained model"""
        if self.model is None:
            print("No model to save!")
            return False
        
        # Save model
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        joblib.dump(self.model, MODEL_PATH)
        print(f"Model saved to {MODEL_PATH}")
        
        # Save preprocessors
        self.preprocessor.save_preprocessors()
        
        return True
    
    def load_model(self):
        """Load a saved model"""
        try:
            self.model = joblib.load(MODEL_PATH)
            self.preprocessor.load_preprocessors()
            print("Model loaded successfully")
            return self.model
        except FileNotFoundError:
            print("Model file not found. Please train the model first.")
            return None