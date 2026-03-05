import os
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import xgboost as xgb
from sklearn.ensemble import RandomForestRegressor
import warnings

warnings.filterwarnings('ignore')

# Directory for storing models
MODELS_DIR = "models"
os.makedirs(MODELS_DIR, exist_ok=True)

def train_ats_models():
    print("Training ATS Models (TF-IDF & Logistic Regression)...")
    # Synthetic dataset for ATS Scoring (Expanded to 50 items for more robustness)
    corpus = [
        # Tech roles - Good fit (1s)
        "Experienced software engineer with strong skills in python, java, sql, and react. 5 years of experience building scalable applications.",
        "Full stack developer. 4 years experience. proficient in javascript, react, node.js, html, css, and python.",
        "Backend engineer with deep knowledge of python, django, rest apis, postgresql, and aws. 6 years hands-on experience.",
        "Data scientist with a background in machine learning, deep learning, nlp, and python.",
        "Machine learning researcher. Expert in python, tensorflow, pytorch, computer vision. 3 years experience.",
        "Frontend developer. React, Vue, javascript, typescript, css, sass. 2 years experience.",
        "Cloud architect with 8 years experience. aws, azure, python, bash, kubernetes, docker.",
        "Senior java developer. Spring boot, microservices, oracle, java. 7 years experience.",
        "DevOps engineer. CI/CD, jenkins, gitlab, terraform, ansible, linux, python. 4 years of experience.",
        "Mobile developer. iOS, swift, objective-c, react native. 3 years experience.",
        "Android developer. Kotlin, java, android studio, mobile UI. 5 years experience.",
        "Data engineer. sql, spark, hadoop, python, etl, data warehousing. 6 years experience.",
        "Cybersecurity analyst. network security, penetration testing, ethical hacking, python. 4 years experience.",
        "Game developer. unity, c#, c++, 3d modeling. 3 years of game programming.",
        "Blockchain developer. solidity, ethereum, smart contracts, web3, javascript. 2 years experience.",
        "Software architect. System design, microservices, cloud native, aws, java, golang. 10 years experience.",
        "QA engineer. Selenium, cypress, automated testing, python, java, api testing. 4 years experience.",
        "UI/UX designer with some frontend coding. figma, adobe xd, html, css, javascript. 5 years experience.",
        "Product manager. agile, scrum, jira, technical roadmaps, software development lifecycle. 6 years experience.",
        "Site Reliability Engineer (SRE). go, python, kubernetes, prometheus, grafana. 5 years experience.",
        "Tech lead. managing teams, architectural decisions, java, spring, aws. 8 years experience.",
        "Database administrator. oracle, postgresql, mysql, performance tuning, backups. 7 years experience.",
        "AI engineer. openai, prompt engineering, llm, langchain, python, vector databases. 2 years experience.",
        "Embedded software engineer. c, c++, rtos, microcontrollers, embedded systems. 5 years experience.",
        "Systems engineer. linux, shell scripting, networking, hardware troubleshooting. 6 years experience.",
        
        # Non-Tech / Poorly Formatted / Unrelated roles - Bad fit (0s)
        "Professional chef with 10 years of experience in fine dining and Italian cuisine.",
        "Dedicated high school biology teacher with 5 years of experience planning lessons and grading.",
        "Customer service representative. Strong communication skills. 2 years experience answering calls.",
        "Construction worker. Experience with heavy machinery, framing, and roofing.",
        "Retail manager with 4 years of experience optimizing store operations and leading teams.",
        "Graphic designer. Expert in adobe illustrator, photoshop, figma. 3 years experience.",
        "Freelance writer and editor. Experienced in copywriting, seo, and content marketing.",
        "Accountant. 5 years experience in tax preparation, bookkeeping, and excel.",
        "Sales executive. B2B sales, cold calling, lead generation, salesforce. 6 years experience.",
        "Registered nurse. Patient care, medical records, CPR certified. 4 years experience in hospital.",
        "Uber driver. safe driving, customer service, navigating. 2 years experience.",
        "Delivery driver. Logistics, route planning, time management. 3 years experience.",
        "Fitness trainer. Personal training, nutrition, workout plans. 5 years experience.",
        "Real estate agent. property sales, negotiations, market analysis. 4 years experience.",
        "Event planner. coordinating events, vendor management, budgeting. 6 years experience.",
        "Cashier. handling transactions, customer support, point of sale systems. 1 year experience.",
        "Plumber. pipe installation, repair, maintenance. 8 years experience.",
        "Electrician. wiring, troubleshooting, electrical codes. 7 years experience.",
        "Mechanic. auto repair, engine diagnostics, maintenance. 10 years experience.",
        "Janitor. cleaning, maintenance, sanitation protocols. 3 years experience.",
        "Musician. playing guitar, performing, composing. 5 years experience.",
        "Actor. stage performance, memorization, acting techniques. 4 years experience.",
        "Photographer. portrait photography, lighting, photo editing. 5 years experience.",
        "Barista. coffee making, espresso machines, customer interaction. 2 years experience.",
        "Flight attendant. passenger safety, communication, in-flight service. 3 years experience."
    ]
    
    # 1 for Tech/Good fit, 0 for Unrelated
    labels = [1]*25 + [0]*25
    
    # 1. Train TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(stop_words='english', max_features=1500)
    X = vectorizer.fit_transform(corpus)
    
    # Save Vectorizer
    vectorizer_path = os.path.join(MODELS_DIR, "tfidf_vectorizer.joblib")
    joblib.dump(vectorizer, vectorizer_path)
    print(f"Saved TF-IDF Vectorizer to {vectorizer_path}")
    
    # 2. Train Logistic Regression
    lr_model = LogisticRegression(random_state=42, max_iter=200)
    lr_model.fit(X, labels)
    
    # Save Logistic Regression model
    lr_path = os.path.join(MODELS_DIR, "lr_model.joblib")
    joblib.dump(lr_model, lr_path)
    print(f"Saved Logistic Regression Model to {lr_path}\n")


def train_ranking_models():
    print("Training Ranking Models (XGBoost & Random Forest)...")
    
    # Synthetic dataset for Ranking Model
    # Features: [Semantic_Sim (0.0-1.0), ATS_Score (0.0-100.0), Exp_Years_Delta, Skill_Match_Count]
    X_list = [
        # Generally normal patterns
        [0.98, 99.0, 5, 15], [0.95, 95.0, 3, 12], [0.90, 92.0, 4, 11], [0.92, 90.0, 2, 10], [0.88, 88.0, 1, 9],
        [0.85, 85.0, 0, 8],  [0.82, 82.0, -1, 7], [0.80, 80.0, 0, 7],  [0.78, 78.0, 2, 6],  [0.75, 75.0, -1, 6],
        [0.72, 72.0, -2, 5], [0.70, 70.0, 1, 5],  [0.68, 68.0, 0, 5],  [0.65, 65.0, 3, 4],  [0.62, 62.0, -2, 4],
        [0.60, 60.0, -3, 3], [0.58, 58.0, -4, 3], [0.55, 55.0, 0, 3],  [0.52, 52.0, -1, 2], [0.50, 50.0, 1, 2],
        [0.48, 45.0, 0, 2],  [0.45, 40.0, -3, 1], [0.42, 38.0, -2, 1], [0.40, 35.0, 0, 1],  [0.35, 30.0, -5, 0],
        [0.30, 25.0, -4, 0], [0.25, 20.0, 0, 0],  [0.20, 15.0, -6, 0], [0.15, 10.0, 0, 0],  [0.10, 5.0, -8, 0],
        
        # Edge cases & interesting configurations
        [0.95, 60.0, 10, 5],   # High semantic match, high exp, but low overall ATS score and missing skills
        [0.40, 90.0, -2, 12],  # Keyword stuffed: low semantic sim but high skill count and high ATS score
        [0.80, 50.0, -5, 8],   # Decent fit but severely under-experienced
        [0.20, 15.0, 15, 0],   # Huge amount of experience but completely irrelevant to JD
        [0.90, 85.0, 0, 5],    # Requires few skills, meets them perfectly
        [0.85, 95.0, -1, 14],  # Almost perfect, slight exp lack but hits almost all skills
        [0.50, 40.0, 5, 2],    # Lots of exp, poor match
        [0.70, 75.0, -2, 6],   # Decent match, slightly under experienced
        [0.99, 100.0, 2, 20],  # Perfect exceptional candidate
        [0.01, 0.0, -10, 0]    # Completely irrelevant profile
    ]
    X = np.array(X_list)
    
    # Labels: Final Ranking Score (0 to 100)
    y_list = [
        99.0, 95.0, 93.0, 91.0, 89.0,
        86.0, 81.0, 80.0, 79.0, 74.0,
        70.0, 71.0, 68.0, 67.0, 60.0,
        55.0, 52.0, 54.0, 50.0, 51.0,
        45.0, 38.0, 36.0, 35.0, 25.0,
        22.0, 20.0, 15.0, 10.0, 5.0,
        
        # Edge cases specific labellings
        65.0, # Good semantics, missing skills (High level conceptual fit)
        60.0, # Keyword stuffing (Penalized for low semantic similarity despite skills)
        65.0, # Severely under-experienced but capable
        12.0, # Lots of exp, irrelevant (Don't rank high)
        88.0, # Requires few skills (Rank highly)
        90.0, # Almost perfect, slight exp lack (Rank highly)
        45.0, # Lots of exp, poor match
        70.0, # Decent match, slightly under
        100.0,# Perfect
        0.0   # Garbage
    ]
    y = np.array(y_list)
    
    # 1. Train XGBoost
    xgb_model = xgb.XGBRegressor(
        n_estimators=150, 
        learning_rate=0.05, 
        max_depth=6, 
        random_state=42
    )
    xgb_model.fit(X, y)
    
    xgb_path = os.path.join(MODELS_DIR, "xgb_model.joblib")
    joblib.dump(xgb_model, xgb_path)
    print(f"Saved XGBoost Model to {xgb_path}")
    
    # 2. Train Random Forest
    rf_model = RandomForestRegressor(
        n_estimators=150,
        max_depth=6,
        random_state=42
    )
    rf_model.fit(X, y)
    
    rf_path = os.path.join(MODELS_DIR, "rf_model.joblib")
    joblib.dump(rf_model, rf_path)
    print(f"Saved Random Forest Model to {rf_path}\n")

if __name__ == "__main__":
    print("Starting Model Training Pipeline...")
    train_ats_models()
    train_ranking_models()
    print("All models trained and saved successfully.")
