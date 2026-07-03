# ai/preprocess.py
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
import joblib
from config.settings import DATASET_PATH, SCALER_PATH, ENCODER_PATH

class DataPreprocessor:
    def __init__(self):
        self.label_encoder = LabelEncoder()
        self.scaler = StandardScaler()
        self.feature_names = None
        self.target_name = 'disease'
    
    def load_dataset(self):
        """Load the disease dataset"""
        try:
            df = pd.read_csv(DATASET_PATH)
            print(f"Dataset loaded successfully with {len(df)} records")
            return df
        except FileNotFoundError:
            print("Dataset not found. Creating sample dataset...")
            return self.create_sample_dataset()
    
    def create_sample_dataset(self):
        """Create a sample disease dataset for demonstration"""
        # Sample symptom-disease mapping
        data = {
            'fever': np.random.randint(0, 2, 200),
            'cough': np.random.randint(0, 2, 200),
            'headache': np.random.randint(0, 2, 200),
            'fatigue': np.random.randint(0, 2, 200),
            'nausea': np.random.randint(0, 2, 200),
            'chest_pain': np.random.randint(0, 2, 200),
            'shortness_of_breath': np.random.randint(0, 2, 200),
            'joint_pain': np.random.randint(0, 2, 200),
            'skin_rash': np.random.randint(0, 2, 200),
            'disease': []
        }
        
        # Generate disease labels based on symptom combinations
        diseases = ['Flu', 'Common Cold', 'COVID-19', 'Pneumonia', 'Allergy', 
                   'Asthma', 'Arthritis', 'Skin Infection', 'Migraine', 'Gastroenteritis']
        
        for i in range(200):
            # Create meaningful patterns
            symptoms = [data[key][i] for key in data.keys() if key != 'disease']
            if sum(symptoms) >= 7:
                data['disease'].append(np.random.choice(['COVID-19', 'Pneumonia']))
            elif sum(symptoms) >= 5:
                data['disease'].append(np.random.choice(['Flu', 'Gastroenteritis']))
            elif sum(symptoms) >= 3:
                data['disease'].append(np.random.choice(['Common Cold', 'Allergy', 'Migraine']))
            else:
                data['disease'].append(np.random.choice(['Allergy', 'Asthma', 'Arthritis', 'Skin Infection']))
        
        df = pd.DataFrame(data)
        df.to_csv(DATASET_PATH, index=False)
        print(f"Sample dataset created with {len(df)} records")
        return df
    
    def preprocess_data(self, df):
        """Preprocess the dataset"""
        # Separate features and target
        X = df.drop(self.target_name, axis=1)
        y = df[self.target_name]
        
        # Save feature names
        self.feature_names = X.columns.tolist()
        
        # Encode target
        y_encoded = self.label_encoder.fit_transform(y)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        return X_scaled, y_encoded, X, y
    
    def split_data(self, X, y, test_size=0.2, random_state=42):
        """Split data into train and test sets"""
        return train_test_split(X, y, test_size=test_size, random_state=random_state)
    
    def preprocess_single_input(self, symptoms_dict):
        """Preprocess a single input for prediction"""
        # Convert symptoms to array
        symptom_values = []
        for feature in self.feature_names:
            symptom_values.append(symptoms_dict.get(feature, 0))
        
        # Scale the input
        input_scaled = self.scaler.transform([symptom_values])
        return input_scaled
    
    def save_preprocessors(self):
        """Save the scaler and label encoder"""
        joblib.dump(self.scaler, SCALER_PATH)
        joblib.dump(self.label_encoder, ENCODER_PATH)
        print("Preprocessors saved successfully")
    
    def load_preprocessors(self):
        """Load the scaler and label encoder"""
        self.scaler = joblib.load(SCALER_PATH)
        self.label_encoder = joblib.load(ENCODER_PATH)
        print("Preprocessors loaded successfully")