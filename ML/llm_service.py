import os
from google import genai
from dotenv import load_dotenv

# Load environment variables
backend_env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Backend API', '.env')
load_dotenv(backend_env_path)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY not found in .env")

# Use gemini-2.0-flash
MODEL_NAME = 'gemini-2.0-flash'

def get_llm_client():
    if not GEMINI_API_KEY:
        return None
    return genai.Client(api_key=GEMINI_API_KEY)

def generate_resume_suggestions(resume_text: str, jd_text: str) -> str:
    """
    Analyzes the resume against the job description and provides actionable suggestions.
    """
    if not GEMINI_API_KEY:
        return "LLM API Key not configured."

    client = get_llm_client()
    if not client:
        return "LLM Client failed to initialize."
        
    prompt = f"""
You are an expert technical recruiter and ATS optimization specialist.
Analyze the following resume against the provided Job Description.

Job Description:
{jd_text}

Resume:
{resume_text}

Provide concise, actionable suggestions on how the candidate can improve their resume to better match the job description. 
Focus on:
1. Missing keywords or skills to add (if they possess them)
2. Impact formatting (e.g., adding metrics to bullet points)
3. Structural improvements
Keep your response short, formatted in markdown, and highly professional. Do not write a cover letter or rewrite the resume for them.
"""
    
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"Error generating suggestions: {e}")
        return f"Error connecting to LLM service: {str(e)}"

def answer_technical_question(resume_text: str, question: str) -> str:
    """
    Answers a specific user question about the candidate's resume based on the extracted text.
    """
    if not GEMINI_API_KEY:
        return "LLM API Key not configured."

    client = get_llm_client()
    if not client:
        return "LLM Client failed to initialize."
        
    prompt = f"""
You are an AI assistant helping a recruiter review a resume.
Answer the following question based ONLY on the provided resume text. If the resume does not contain the answer, say "The resume does not specify this information."

Resume Text:
{resume_text}

Question:
{question}
"""
    
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"Error answering question: {e}")
        return f"Error connecting to LLM service: {str(e)}"
