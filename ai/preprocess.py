import os
import joblib
import numpy as np
import pandas as pd

from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split

from config.settings import (
    DATASET_PATH,
    SCALER_PATH,
    ENCODER_PATH,
)


class DataPreprocessor:

    def __init__(self):
        self.label_encoder = LabelEncoder()
        self.scaler = StandardScaler()
        self.feature_names = []
        self.target_name = "disease"

    # ==========================================================
    # DATASET
    # ==========================================================

    def load_dataset(self):

        if os.path.exists(DATASET_PATH):
            df = pd.read_csv(DATASET_PATH)
            print(f"Dataset loaded ({len(df)} rows)")
            return df

        print("Dataset not found.")
        return self.create_sample_dataset()

    def create_sample_dataset(self):

        os.makedirs(os.path.dirname(DATASET_PATH), exist_ok=True)

        data = {
            "fever": np.random.randint(0, 2, 200),
            "cough": np.random.randint(0, 2, 200),
            "headache": np.random.randint(0, 2, 200),
            "fatigue": np.random.randint(0, 2, 200),
            "nausea": np.random.randint(0, 2, 200),
            "chest_pain": np.random.randint(0, 2, 200),
            "shortness_of_breath": np.random.randint(0, 2, 200),
            "joint_pain": np.random.randint(0, 2, 200),
            "skin_rash": np.random.randint(0, 2, 200),
        }

        df = pd.DataFrame(data)

        diseases = []

        for _, row in df.iterrows():

            score = row.sum()

            if score >= 7:
                diseases.append(
                    np.random.choice(["COVID-19", "Pneumonia"])
                )

            elif score >= 5:
                diseases.append(
                    np.random.choice(["Flu", "Gastroenteritis"])
                )

            elif score >= 3:
                diseases.append(
                    np.random.choice(
                        [
                            "Common Cold",
                            "Migraine",
                            "Allergy",
                        ]
                    )
                )

            else:
                diseases.append(
                    np.random.choice(
                        [
                            "Asthma",
                            "Skin Infection",
                            "Arthritis",
                        ]
                    )
                )

        df["disease"] = diseases

        df.to_csv(DATASET_PATH, index=False)

        print("Sample dataset created.")

        return df

    # ==========================================================
    # PREPROCESS
    # ==========================================================

    def preprocess_data(self, df):

        if self.target_name not in df.columns:
            raise Exception(
                "Dataset must contain 'disease' column."
            )

        X = df.drop(columns=[self.target_name])
        y = df[self.target_name]

        self.feature_names = list(X.columns)

        X_scaled = self.scaler.fit_transform(X)

        y_encoded = self.label_encoder.fit_transform(y)

        return X_scaled, y_encoded, X, y

    # ==========================================================
    # TRAIN TEST SPLIT
    # ==========================================================

    def split_data(
        self,
        X,
        y,
        test_size=0.2,
        random_state=42,
    ):

        return train_test_split(
            X,
            y,
            test_size=test_size,
            random_state=random_state,
        )

    # ==========================================================
    # SINGLE INPUT
    # ==========================================================

    def preprocess_single_input(self, symptoms):

        values = []

        for feature in self.feature_names:
            values.append(symptoms.get(feature, 0))

        return self.scaler.transform([values])

    # ==========================================================
    # SAVE
    # ==========================================================

    def save_preprocessors(self):

        os.makedirs(os.path.dirname(SCALER_PATH), exist_ok=True)

        joblib.dump(self.scaler, SCALER_PATH)
        joblib.dump(self.label_encoder, ENCODER_PATH)

        feature_path = os.path.join(
            os.path.dirname(SCALER_PATH),
            "features.pkl",
        )

        joblib.dump(self.feature_names, feature_path)

        print("Preprocessors saved.")

    # ==========================================================
    # LOAD
    # ==========================================================

    def load_preprocessors(self):

        if not os.path.exists(SCALER_PATH):
            raise FileNotFoundError("Scaler not found.")

        if not os.path.exists(ENCODER_PATH):
            raise FileNotFoundError("Encoder not found.")

        self.scaler = joblib.load(SCALER_PATH)
        self.label_encoder = joblib.load(ENCODER_PATH)

        feature_path = os.path.join(
            os.path.dirname(SCALER_PATH),
            "features.pkl",
        )

        if os.path.exists(feature_path):
            self.feature_names = joblib.load(feature_path)

        print("Preprocessors loaded.")