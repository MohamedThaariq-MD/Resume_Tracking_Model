import PyPDF2
import docx
import spacy
import re
import logging
import warnings

# Suppress transformer warnings
warnings.filterwarnings("ignore")

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Spacy model 'en_core_web_sm' not found.")
    nlp = None

try:
    from transformers import pipeline
    # Using a lightweight NER model for skill/organization extraction to save memory
    print("Loading HuggingFace NER pipeline...")
    ner_pipeline = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")
    print("HuggingFace NER pipeline loaded successfully.")
except Exception as e:
    print(f"Transformers NER pipeline failed to load: {e}")
    ner_pipeline = None

def extract_text_from_pdf(file_obj):
    text = ""
    reader = PyPDF2.PdfReader(file_obj)
    for page in reader.pages:
        t = page.extract_text()
        if t:
            text += t + "\n"
    return text

def extract_text_from_docx(file_obj):
    doc = docx.Document(file_obj)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text
    
def extract_text_from_file(file_obj, filename):
    if filename.lower().endswith(".pdf"):
        return extract_text_from_pdf(file_obj)
    elif filename.lower().endswith(".docx"):
        return extract_text_from_docx(file_obj)
    else:
        raise ValueError("Unsupported file format")

def extract_skills(text):
    skills = set()
    
    # Comprehensive list of standard IT/Tech/Business skills
    common_skills = [
        # Languages
        "python", "java", "c++", "c", "c#", "javascript", "typescript", "ruby", "php", 
        "swift", "kotlin", "go", "golang", "rust", "scala", "r", "perl", "dart", "html", "css",
        "assembly", "bash", "shell", "powershell", "objective-c",
        # Frameworks & Libraries
        "react", "react.js", "react native", "angular", "angularjs", "vue", "vue.js", 
        "node.js", "node", "express", "express.js", "next.js", "nuxt.js", "gatsby",
        "django", "flask", "fastapi", "spring", "spring boot", "ruby on rails", 
        "laravel", "symfony", "asp.net", ".net", ".net core", "blazor",
        "tailwind", "tailwindcss", "bootstrap", "material UI", "jquery",
        "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy", "matplotlib", "seaborn",
        "flutter", "xamarin", "ionic", "cordova", "swagger", "graphql", "rest", "restful", "soap",
        "koa.js", "mvc",
        # Databases & Storage
        "sql", "mysql", "postgresql", "postgres", "sqlite", "oracle", "sql server", 
        "nosql", "mongodb", "cassandra", "redis", "elasticsearch", "dynamodb", "firebase", 
        "supabase", "mariadb", "couchdb", "neo4j", "graphql",
        # Cloud & DevOps
        "aws", "amazon web services", "azure", "gcp", "google cloud", "heroku", "digitalocean",
        "docker", "kubernetes", "k8s", "jenkins", "gitlab ci", "github actions", "travis ci", 
        "circleci", "ansible", "terraform", "puppet", "chef", "linux", "ubuntu", "centos",
        "nginx", "apache", "ci/cd",
        # Methodologies & Tools
        "git", "github", "gitlab", "bitbucket", "jira", "trello", "confluence", 
        "agile", "scrum", "kanban", "waterfall", 
        "machine learning", "deep learning", "nlp", "artificial intelligence", "ai", 
        "computer vision", "data science", "data engineering", "big data", "hadoop", "spark", "kafka",
        "frontend", "backend", "fullstack", "full-stack", "full stack", 
        "sde", "software engineering", "ui/ux", "web development", "mobile development",
        "android", "ios", "qa", "testing", "selenium", "jest", "mocha", "cypress", "junit",
        "j2ee", "linq"
    ]
    
    text_lower = text.lower()
    
    # Simple regex matching
    # We use a non-word-boundary substring search since the resume parser may concatenate things
    # like "android##ql serverexpressexpress.js" instead of putting spaces between them.
    for skill in common_skills:
        escaped_skill = re.escape(skill)
        
        # For very short skills (like "c", "r", "go", "ai", "sql"), enforce word boundaries 
        # so they don't match randomly inside other words (e.g. "django" -> "go", "react" -> "c", "r").
        if len(skill) <= 3:
            if bool(re.search(r'\b' + escaped_skill + r'\b', text_lower)):
                skills.add(skill)
        else:
            # For longer, distinct skills, a simple substring check is fine and more forgiving 
            # against messy PDF parses or concatenated strings.
            if escaped_skill in text_lower:
                skills.add(skill)
            
    return sorted(list(skills))

def extract_experience(text):
    """
    Extracts total years of experience using regex heuristics.
    """
    experience_patterns = [
        r'(\d+)\+?\s*(years?|yrs?|yoe)\s*(of\s+)?(experience|exp)?',
        r'(experience|exp).*?:.*?(\d+)\+?\s*(years?|yrs?|yoe)',
        r'(\d+)\s*yoe'
    ]
    
    max_years = 0
    for pattern in experience_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                years = int(match[0])
                if years > max_years and years < 40: # Sanity check (less than 40 years)
                    max_years = years
            except ValueError:
                continue
                
    return max_years

def extract_education(text):
    """
    Extracts degrees using Regex and spaCy.
    """
    degrees = []
    degree_patterns = [
        r'\b(bachelor|b\.?s\.?|b\.?a\.?|btech|b\.?tech|master|m\.?s\.?|m\.?a\.?|mtech|m\.?tech|ph\.?d\.?|doctorate)\b'
    ]
    
    text_lower = text.lower()
    for pattern in degree_patterns:
        matches = re.finditer(pattern, text_lower)
        for match in matches:
            degrees.append(match.group(1).upper())
            
    return list(set(degrees))
