from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import json
import tempfile
import shutil

from parser import extract_text_from_file, extract_skills, extract_experience, extract_education
from ats_scorer import ats_scorer_instance
from ranking_model import ranker_instance
from vector_store import store, compute_similarity
from llm_service import generate_resume_suggestions, answer_technical_question
from resume_generator import resume_generator_instance
from document_editor import magic_edit_docx

app = FastAPI(title="Resume Tracking ML Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class JDAnalyzeRequest(BaseModel):
    title: str
    description: str
    required_skills: list[str]

class LLMAnalyzeRequest(BaseModel):
    jd_text: str
    resume_text: str

class LLMChatRequest(BaseModel):
    resume_text: str
    question: str

class LLMGenerateRequest(BaseModel):
    jd_text: str
    resume_text: str

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "ML Service"}

@app.post("/analyze_resume")
async def analyze_resume(file: UploadFile = File(...)):
    if not file.filename.endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")
        
    try:
        text = extract_text_from_file(file.file, file.filename)
        skills = extract_skills(text)
        experience = extract_experience(text)
        education = extract_education(text)
        
        return {
            "filename": file.filename,
            "extracted_skills": skills,
            "experience_years": experience,
            "education": education,
            "text_length": len(text),
            "raw_text": text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/calculate_ats")
async def calculate_ats(req: str = Form(...), resume_text: str = Form(...)):
    req_data = json.loads(req)
    # 1. Parse Resume Details Again (or rely on frontend to pass them, assuming pass raw text here)
    resume_skills = extract_skills(resume_text)
    resume_exp = extract_experience(resume_text)
    resume_edu = extract_education(resume_text)
    
    jd_skills = req_data.get("required_skills", [])
    if not jd_skills:
        jd_skills = extract_skills(req_data.get("description", ""))

    jd_text = req_data.get("title", "") + " " + req_data.get("description", "") + " " + " ".join(jd_skills)
    
    # 2. Advanced Transformer Similarity (Sentence-BERT / RoBERTa)
    semantic_sim = compute_similarity(jd_text, resume_text)
    
    # 3. TF-IDF + Logistic Regression JD Match Score
    match_score = ats_scorer_instance.calculate_score(
        resume_text=resume_text, 
        jd_text=jd_text, 
        resume_skills=resume_skills, 
        jd_skills=jd_skills, 
        resume_exp=resume_exp, 
        resume_edu=resume_edu
    )
    
    # 3.5 Standalone ATS Score (pure resume format/length/skills)
    standalone_ats = ats_scorer_instance.calculate_standalone_ats_score(
        resume_text=resume_text,
        resume_skills=resume_skills,
        resume_exp=resume_exp,
        resume_edu=resume_edu
    )
    
    # If no JD was provided, match_score will be 0.0. The frontend will only show ATS score.
    
    # 4. XGBoost / Random Forest Ensemble Ranking
    # Assuming JD experience requirement defaults to 3 if not parseable (mocking for now)
    jd_exp_req = 3
    exp_gap = resume_exp - jd_exp_req 
    
    jd_skills_set = set([s.lower() for s in jd_skills])
    resume_skills_set = set([s.lower() for s in resume_skills])
    skill_match_count = len(jd_skills_set.intersection(resume_skills_set))
    missing_skills = list(jd_skills_set - resume_skills_set)
    matching_skills = list(jd_skills_set.intersection(resume_skills_set))

    final_rank = ranker_instance.calculate_rank(
        semantic_similarity=semantic_sim,
        ats_score=match_score, # use match score for ranking
        experience_years=exp_gap,
        skill_match_count=skill_match_count
    )

    return {
        "ats_score": float(standalone_ats),
        "match_score": float(match_score),
        "semantic_similarity_score": round(float(semantic_sim * 100), 2),
        "final_ranking_score": float(final_rank),
        "skill_match": skill_match_count,
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "experience_parsed": resume_exp,
        "education_parsed": resume_edu
    }

@app.post("/llm/analyze")
async def llm_analyze(req: LLMAnalyzeRequest):
    try:
        suggestions = generate_resume_suggestions(req.resume_text, req.jd_text)
        return {"suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/llm/chat")
async def llm_chat(req: LLMChatRequest):
    try:
        answer = answer_technical_question(req.resume_text, req.question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/llm/generate_resume")
async def llm_generate_resume(req: LLMGenerateRequest):
    try:
        generated_resume = resume_generator_instance.generate_ats_resume(
            resume_text=req.resume_text, 
            jd_text=req.jd_text
        )
        return {"generated_resume": generated_resume}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/llm/magic_edit")
async def llm_magic_edit(file: UploadFile = File(...), resume_text: str = Form(...), missing_skills: str = Form(...)):
    if not file.filename.endswith(".docx"):
         raise HTTPException(status_code=400, detail="Only DOCX files are supported for Magic Edit.")
         
    try:
        skills_list = json.loads(missing_skills)
        
        # Save uploaded file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_input:
            shutil.copyfileobj(file.file, temp_input)
            temp_input_path = temp_input.name
            
        temp_output_path = temp_input_path.replace(".docx", "_edited.docx")
        
        # Process the DOCX
        success = magic_edit_docx(temp_input_path, temp_output_path, resume_text, skills_list)
        
        if success and os.path.exists(temp_output_path):
             return FileResponse(path=temp_output_path, filename=f"Magic_{file.filename}", media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        else:
             raise HTTPException(status_code=500, detail="Failed to apply magic edits to the document.")
             
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup input temp file. Output file is cleaned up by FastAPI FileResponse or OS automatically later
        if os.path.exists(temp_input_path):
             try: os.remove(temp_input_path)
             except: pass
