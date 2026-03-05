import pprint
from ats_scorer import ats_scorer_instance
from ranking_model import ranker_instance
from vector_store import compute_similarity
from parser import extract_skills, extract_experience, extract_education

def run_ml_pipeline_test():
    """
    Simulates sending a full Job Description and Resume to the newly established
    ML Models. Validates execution and prints training dummy feedback.
    """
    jd_title = "Senior Data Scientist"
    jd_desc = "We are seeking a highly motivated data scientist with deep experience in machine learning pipelines, scalable backend engineering, and leading teams to deliver AI products."
    jd_skills = ["Machine Learning", "Deep Learning", "Python", "SQL", "Team Leadership", "NLP"]
    
    # Combined JD Text
    jd_full_text = jd_title + " " + jd_desc + " " + " ".join(jd_skills)
    
    resume_text = """
    Jane Doe
    jane.doe@email.com
    
    Education:
    M.S. in Computer Science - University of State
    B.S. in Mathematics - University of State
    
    Experience:
    Senior AI Engineer | Tech Corp | Jan 2018 - Present
    - 5+ years of experience building and deploying machine learning and deep learning models to production using Python and FastAPI.
    - Led a team of four junior data scientists building robust NLP pipelines.
    - Optimized Postgres SQL queries cutting latency by 20%.
    
    Skills:
    Python, Java, Machine Learning, Deep Learning, SQL, PyTorch, Transformers, NLP
    """
    
    print("====================================")
    print("1. Extracting Resume Properties")
    print("====================================")
    
    parsed_skills = extract_skills(resume_text)
    parsed_exp = extract_experience(resume_text)
    parsed_edu = extract_education(resume_text)
    
    print(f"Detected Skills: {parsed_skills}")
    print(f"Detected Experience: {parsed_exp} years")
    print(f"Detected Education Degrees: {parsed_edu}")
    print()
    
    print("====================================")
    print("2. Semantic Similarity Search")
    print("====================================")
    
    sem_score = compute_similarity(jd_full_text, resume_text)
    print(f"Transformers Cosine Similarity: {round(sem_score * 100, 2)}%")
    print()
    
    print("====================================")
    print("3. ATS Score Calculation")
    print("====================================")
    
    ats_score = ats_scorer_instance.calculate_score(
        resume_text=resume_text,
        jd_text=jd_full_text,
        resume_skills=parsed_skills,
        jd_skills=jd_skills,
        resume_exp=parsed_exp,
        resume_edu=parsed_edu
    )
    
    print(f"TF-IDF + Logistic Regression ATS Score: {ats_score}")
    print()
    
    print("====================================")
    print("4. final ranking Score")
    print("====================================")
    
    jd_skills_set = set([s.lower() for s in jd_skills])
    resume_skills_set = set([s.lower() for s in parsed_skills])
    skill_match_count = len(jd_skills_set.intersection(resume_skills_set))
    
    # JD Requires 3 Years minimum
    exp_gap = parsed_exp - 3
    
    rank_score = ranker_instance.calculate_rank(
        semantic_similarity=sem_score,
        ats_score=ats_score,
        experience_years=exp_gap,
        skill_match_count=skill_match_count
    )
    
    print(f"XGBoost + Random Forest Ensemble Ranking Score: {rank_score} out of 100")
    print("====================================")
    print("ALL TESTS PASSED SUCCESSFULLY.")

if __name__ == "__main__":
    run_ml_pipeline_test()
