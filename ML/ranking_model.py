import xgboost as xgb
from sklearn.ensemble import RandomForestRegressor
import numpy as np
import logging
import warnings

warnings.filterwarnings('ignore')

import os
import joblib

class ResumeRankingModel:
    """
    Uses XGBoost and Random Forest logic to combine disparate features 
    (Semantic Similarity, ATS Score, Experience Gap, Skill Match)
    into a powerful, unified rank prediction.
    """
    def __init__(self):
        self.is_trained = False
        
        models_dir = os.path.join(os.path.dirname(__file__), "models")
        xgb_path = os.path.join(models_dir, "xgb_model.joblib")
        rf_path = os.path.join(models_dir, "rf_model.joblib")
        
        try:
            if os.path.exists(xgb_path) and os.path.exists(rf_path):
                self.xgb_model = joblib.load(xgb_path)
                self.rf_model = joblib.load(rf_path)
                self.is_trained = True
                print("ResumeRankingModel: Loaded pre-trained models successfully.")
            else:
                raise FileNotFoundError("Models not found.")
        except Exception as e:
            print(f"ResumeRankingModel: Falling back to mock training. Error: {e}")
            self.xgb_model = xgb.XGBRegressor(
                n_estimators=100, 
                learning_rate=0.1, 
                max_depth=5, 
                random_state=42
            )
            self.rf_model = RandomForestRegressor(
                n_estimators=100,
                max_depth=5,
                random_state=42
            )
            # Simulate training with dummy data
            self._mock_train()

    def _mock_train(self):
        """Simulate training the ensemble models so they can predict."""
        # Features: [Semantic_Sim (0-1), ATS_Score (0-100), Exp_Years, Skill_Match_Count]
        X = np.array([
            [0.9, 95.0, 5, 10], # Perfect candidate
            [0.8, 80.0, 3, 7],  # Good candidate
            [0.5, 40.0, 1, 3],  # Poor candidate
            [0.1, 10.0, 0, 0]   # Unrelated
        ])
        
        # Labels: Ranking Score (0 to 100)
        y = np.array([98.0, 85.0, 45.0, 5.0])
        
        self.xgb_model.fit(X, y)
        self.rf_model.fit(X, y)
        self.is_trained = True

    def calculate_rank(self, semantic_similarity, ats_score, experience_years, skill_match_count):
        """
        Combines model predictions into a final score representing Ranking fitness.
        """
        # Ensure inputs are shaped correctly for single prediction
        features = np.array([[
            float(semantic_similarity), 
            float(ats_score), 
            float(experience_years), 
            float(skill_match_count)
        ]])
        
        xgb_pred = self.xgb_model.predict(features)[0]
        rf_pred = self.rf_model.predict(features)[0]
        
        # Ensemble Average
        final_rank = (xgb_pred + rf_pred) / 2.0
        
        # Cap output between 0 and 100
        return round(float(np.clip(final_rank, 0.0, 100.0)), 2)

# Global Instance
ranker_instance = ResumeRankingModel()
