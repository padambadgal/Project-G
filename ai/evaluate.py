# ai/evaluate.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, roc_curve, auc
import numpy as np

class ModelEvaluator:
    def __init__(self, model, preprocessor):
        self.model = model
        self.preprocessor = preprocessor
    
    def plot_confusion_matrix(self, X_test, y_test):
        """Plot confusion matrix"""
        y_pred = self.model.predict(X_test)
        cm = confusion_matrix(y_test, y_pred)
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.title('Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        plt.savefig('confusion_matrix.png')
        plt.show()
    
    def plot_feature_importance(self, feature_names):
        """Plot feature importance"""
        importance = self.model.feature_importances_
        
        plt.figure(figsize=(10, 6))
        plt.barh(feature_names, importance)
        plt.xlabel('Feature Importance')
        plt.title('Feature Importance for Disease Prediction')
        plt.tight_layout()
        plt.savefig('feature_importance.png')
        plt.show()
    
    def evaluate_model_performance(self, X_test, y_test):
        """Evaluate model performance with various metrics"""
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        
        y_pred = self.model.predict(X_test)
        
        metrics = {
            'Accuracy': accuracy_score(y_test, y_pred),
            'Precision (weighted)': precision_score(y_test, y_pred, average='weighted'),
            'Recall (weighted)': recall_score(y_test, y_pred, average='weighted'),
            'F1 Score (weighted)': f1_score(y_test, y_pred, average='weighted')
        }
        
        return metrics