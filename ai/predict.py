import os
import numpy as np

from config.settings import MODEL_PATH
from ai.train_model import ModelTrainer
from ai.preprocess import DataPreprocessor


class DiseasePredictor:

    def __init__(self):

        self.model = None
        self.preprocessor = DataPreprocessor()
        self.trainer = ModelTrainer()

    # ==========================================================
    # LOAD MODEL
    # ==========================================================

    def load_model(self):

        try:

            if not os.path.exists(MODEL_PATH):
                return False

            self.model = self.trainer.load_model()

            if self.model is None:
                return False

            self.preprocessor.load_preprocessors()

            return True

        except Exception as e:

            print("Model loading error:", e)

            return False

    # ==========================================================
    # TRAIN MODEL
    # ==========================================================

    def train_and_load_model(self):

        print("Training AI model...")

        self.trainer.load_and_prepare_data()
        self.trainer.train_model()
        self.trainer.save_model()
        self.trainer.evaluate_model()

        return self.load_model()

    # ==========================================================
    # PREDICT
    # ==========================================================

    def predict_disease(self, symptoms_dict):

        try:

            if self.model is None:

                if not self.load_model():

                    print("No trained model found.")
                    print("Training a new model...")

                    if not self.train_and_load_model():
                        return None

            input_data = self.preprocessor.preprocess_single_input(
                symptoms_dict
            )

            prediction = self.model.predict(input_data)

            disease = self.preprocessor.label_encoder.inverse_transform(
                prediction
            )[0]

            confidence = 0.0
            probabilities = {}

            if hasattr(self.model, "predict_proba"):

                probs = self.model.predict_proba(input_data)[0]

                confidence = float(np.max(probs))

                for index, disease_name in enumerate(
                    self.preprocessor.label_encoder.classes_
                ):
                    probabilities[disease_name] = float(probs[index])

            return {
                "disease": disease,
                "confidence": confidence,
                "probabilities": probabilities,
            }

        except Exception as e:

            print("Prediction Error:", e)

            return None

    # ==========================================================
    # FEATURES
    # ==========================================================

    def get_symptoms_required(self):

        if not self.preprocessor.feature_names:

            try:
                self.preprocessor.load_preprocessors()
            except Exception:
                pass

        return self.preprocessor.feature_names