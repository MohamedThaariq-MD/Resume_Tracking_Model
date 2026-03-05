import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import logging
import warnings

warnings.filterwarnings('ignore')

import os
import joblib

class ATSScorer:
    """
    Combines TF-IDF and Logistic Regression to compute an advanced ATS Score
    based on keyword presence, skill matching, and education weight.
    """
    def __init__(self):
        self.is_trained = False
        models_dir = os.path.join(os.path.dirname(__file__), "models")
        vectorizer_path = os.path.join(models_dir, "tfidf_vectorizer.joblib")
        lr_path = os.path.join(models_dir, "lr_model.joblib")
        
        try:
            if os.path.exists(vectorizer_path) and os.path.exists(lr_path):
                self.vectorizer = joblib.load(vectorizer_path)
                self.model = joblib.load(lr_path)
                self.is_trained = True
                print("ATSScorer: Loaded pre-trained models successfully.")
            else:
                raise FileNotFoundError("Models not found.")
        except Exception as e:
            print(f"ATSScorer: Falling back to mock training. Error: {e}")
            self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
            self.model = LogisticRegression()
            self._mock_train()

    def _mock_train(self):
        """Simulates training the LR model and vectorizer so it can predict."""
        dummy_corpus = [
            "We are looking for a software engineer with python, java, sql, and react skills. 5 years experience.",
            "Seeking a data scientist with machine learning, deep learning, nlp, and python.",
            "Frontend developer required with react, javascript, html, css.",
            "Backend engineer needed: node.js, aws, docker, kubernetes, fastApi.",
            "Chef with 10 years experience in italian cuisine",
            "Teacher looking for a biology teaching role"
        ]
        # 1 means good resume, 0 means bad resume (dummy labels)
        dummy_labels = [1, 1, 1, 1, 0, 0] 
        
        X = self.vectorizer.fit_transform(dummy_corpus)
        self.model.fit(X, dummy_labels)
        self.is_trained = True

    def calculate_score(self, resume_text, jd_text, resume_skills, jd_skills, resume_exp, resume_edu):
        """
        Calculates the ATS Score out of 100.
        """
        if not resume_text or not jd_text:
            return 0.0
            
        # 1. TF-IDF Cosine Similarity for pure keyword match (max 35 points)
        tfidf_matrix = self.vectorizer.transform([jd_text, resume_text])
        # Calculate dot product of vectors and apply a slight square root curve to be more forgiving
        tf_idf_sim = (tfidf_matrix * tfidf_matrix.T).toarray()[0, 1]
        score_tfidf = min((tf_idf_sim ** 0.5) * 100, 35.0) 
        
        # 2. Skill Match (max 35 points)
        jd_skills_set = set([s.lower() for s in jd_skills])
        res_skills_set = set([s.lower() for s in resume_skills])
        
        match_count = len(jd_skills_set.intersection(res_skills_set))
        if len(jd_skills_set) > 0:
            score_skills = (match_count / len(jd_skills_set)) * 35.0
        else:
            score_skills = 35.0 # No skills required
            
        # 3. Education Weight (max 10 points)
        score_edu = 0.0
        if len(resume_edu) > 0:
            score_edu = 10.0 # Any degree gives 10
            
        # 4. Experience Scoring (max 20 points)
        # Assuming typical JD asks for some experience. For now, max out if > 3 years
        score_exp = min(resume_exp / 3.0 * 20.0, 20.0) 
        
        # 5. Logistic Regression Adjustment (Max +/- 5 points)
        # Using the model to predict probability as a slight feature modifier instead of a heavy multiplier
        try:
            res_vec = self.vectorizer.transform([resume_text])
            prob = self.model.predict_proba(res_vec)[0][1] # Probability of class 1
            # Scale from [0, 1] to [-5, +5] impact
            lr_bonus = (prob * 10.0) - 5.0
        except Exception:
            lr_bonus = 0.0 # Fallback
            
        # Final weighted score
        final_ats_score = score_tfidf + score_skills + score_edu + score_exp + lr_bonus
        
        # Ensure it stays within 0 to 100
        return round(max(0.0, min(final_ats_score, 100.0)), 2)

    def calculate_standalone_ats_score(self, resume_text, resume_skills, resume_exp, resume_edu):
        """
        Calculates a standalone ATS Score (out of 100) based purely on resume formatting,
        length, and presence of standard sections, without comparing to a JD.
        """
        if not resume_text:
            return 0.0
            
        score = 0.0
        
        # 1. Text Length / Detail (max 30 points)
        # A good resume should have a reasonable amount of text (approx 300 - 1000 words)
        word_count = len(resume_text.split())
        if word_count > 300:
            score += 30.0
        elif word_count > 150:
            score += 20.0
        elif word_count > 50:
            score += 10.0
            
        # 2. Skills Presence (max 30 points)
        # Just having recognized skills is good
        skill_count = len(resume_skills)
        if skill_count > 12:
            score += 30.0
        elif skill_count > 6:
            score += 20.0
        elif skill_count > 2:
            score += 10.0
            
        # 3. Experience (max 20 points)
        if resume_exp > 5:
            score += 20.0
        elif resume_exp > 2:
            score += 15.0
        elif resume_exp > 0:
            score += 10.0
            
        # 4. Education (max 10 points)
        if len(resume_edu) > 0:
            score += 10.0
            
        # 5. ML Adjustment (max 10 points)
        # Using the base model to predict if it "looks" like a good resume
        try:
            res_vec = self.vectorizer.transform([resume_text])
            prob = self.model.predict_proba(res_vec)[0][1] 
            lr_bonus = prob * 10.0
            score += lr_bonus
        except Exception:
            pass
            
        return round(max(0.0, min(score, 100.0)), 2)

# Global instance
ats_scorer_instance = ATSScorer()
