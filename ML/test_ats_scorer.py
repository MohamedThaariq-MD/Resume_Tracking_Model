import sys
import os

# Ensure we can import from the ML directory
sys.path.append(os.path.join(os.path.dirname(__file__)))

from ats_scorer import ats_scorer_instance

def main():
    resume_text = "Experienced sales professional with a track record of exceeding quotas. Skilled in CRM, negotiation, and lead generation."
    jd_text = "We are looking for a software engineer with python, java, sql, and react skills. 5 years experience."
    resume_skills = ["crm", "negotiation", "lead generation"]
    jd_skills = ["python", "java", "sql", "react"]
    resume_exp = 5
    resume_edu = ["High School"]
    
    score = ats_scorer_instance.calculate_score(resume_text, jd_text, resume_skills, jd_skills, resume_exp, resume_edu)
    print(f"Calculated ATS Score: {score}")

    # Let's also debug the individual components
    # 1. TF-IDF Cosine Similarity for pure keyword match (max 35 points)
    tfidf_matrix = ats_scorer_instance.vectorizer.transform([jd_text, resume_text])
    tf_idf_sim = (tfidf_matrix * tfidf_matrix.T).toarray()[0, 1]
    score_tfidf = min((tf_idf_sim ** 0.5) * 100, 35.0) 
    print(f"TF-IDF Score (max 35): {score_tfidf}")
    
    # 2. Skill Match (max 35 points)
    score_skills = (len(set(jd_skills).intersection(set(resume_skills))) / len(jd_skills)) * 35.0
    print(f"Skills Score (max 35): {score_skills}")
    
    # 3. Education Weight (max 10 points)
    score_edu = 10.0
    print(f"Education Score (max 10): {score_edu}")
    
    # 4. Experience Scoring (max 20 points)
    score_exp = min(resume_exp / 3.0 * 20.0, 20.0)
    print(f"Experience Score (max 20): {score_exp}")
    
    # Base sum
    final_ats_score = score_tfidf + score_skills + score_edu + score_exp
    print(f"Base Sum before modifier: {final_ats_score}")

    # 5. Logistic Regression Adjustment
    res_vec = ats_scorer_instance.vectorizer.transform([resume_text])
    prob = ats_scorer_instance.model.predict_proba(res_vec)[0][1] 
    lr_bonus = (prob * 10.0) - 5.0
    print(f"LR Modifier predict_proba[1]: {prob}")
    print(f"LR Bonus applied: {lr_bonus}")

    print(f"Final calculation: {final_ats_score} + {lr_bonus} = {final_ats_score + lr_bonus:.2f}")

if __name__ == "__main__":
    main()
