from flask import Flask, request, jsonify
from flask_cors import CORS
import pdfplumber
import nltk
from nltk.corpus import stopwords
from sklearn.metrics.pairwise import cosine_similarity
import openai
import os
import re
import numpy as np
from sentence_transformers import SentenceTransformer

# ✅ Initialize Flask App & CORS
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

# ✅ Load NLTK Stopwords
nltk.download("stopwords")
STOPWORDS = set(stopwords.words("english"))

# ✅ Load Sentence Transformer Model for Text Similarity
model = SentenceTransformer("all-MiniLM-L6-v2")

# ✅ Securely Get OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ✅ Home Route (Check If API Is Running)
@app.route("/", methods=["GET"])
def home():
    return "Flask Backend Running!"

# ✅ Extract text from PDFs
def extract_text_from_pdf(file):
    text = ""
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        return f"Error extracting text: {str(e)}"
    return text.strip() if text else "No text found in PDF."

# ✅ Preprocess text (Remove Stopwords & Special Characters)
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    words = text.split()
    return " ".join([word for word in words if word not in STOPWORDS])

# ✅ Improved Skill Matching (Recognizes Related Skills)
skills_mapping = {
    "cloud": ["aws", "azure", "gcp", "cloud computing"],
    "api": ["rest api", "graphql", "web services"],
    "database": ["mongodb", "sql", "postgresql"],
    "frontend": ["react", "angular", "vue"],
    "backend": ["flask", "django", "nodejs"],
}

def extract_skills(text):
    skills_list = ["python", "java", "javascript", "react", "flask", "mongodb", "sql", "api",
                   "aws", "docker", "kubernetes", "graphql", "machine learning", "data science"]
    
    words = set(text.lower().split())
    matched_skills = set()

    for skill in skills_list:
        if skill in words:
            matched_skills.add(skill)
        for key, synonyms in skills_mapping.items():
            if skill in synonyms and key in words:
                matched_skills.add(skill)

    return matched_skills

# ✅ Calculate Skill Match Score (Prevents Division by Zero)
def calculate_skill_match(resume_text, job_desc):
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_desc)

    matched_skills = resume_skills.intersection(job_skills)
    missing_skills = list(job_skills - resume_skills)

    if len(job_skills) == 0:  
        return 100, []  

    skill_match_score = (len(matched_skills) / len(job_skills)) * 100
    return round(float(skill_match_score), 2), missing_skills

# ✅ Improved Text Similarity Using BERT Embeddings
def calculate_text_similarity(resume_text, job_desc):
    embeddings = model.encode([resume_text, job_desc])
    similarity_score = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    return round(float(similarity_score * 100), 2)

# ✅ Improved Education Match
def calculate_education_match(resume_text, job_desc):
    degrees = ["bachelor", "master", "phd", "b.s.", "m.s.", "btech", "mtech"]
    
    resume_degrees = [deg for deg in degrees if deg in resume_text.lower()]
    job_degrees = [deg for deg in degrees if deg in job_desc.lower()]

    if not job_degrees:
        return 100  # No degree requirement = full match

    return 100 if set(resume_degrees) & set(job_degrees) else 0

# ✅ AI-Enhanced Resume Improvement (Fixed OpenAI API)
def improve_resume(resume_text, job_desc):
    if not OPENAI_API_KEY:
        return "⚠ ERROR: OpenAI API Key is missing!"

    try:
        openai.api_key = OPENAI_API_KEY
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI assistant that improves resumes to match job descriptions."},
                {"role": "user", "content": f"Improve the following resume to better match this job description:\n\nResume:\n{resume_text}\n\nJob Description:\n{job_desc}\n\nEnhanced Resume:"}
            ]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠ OpenAI Error: {str(e)}"

# ✅ Upload API (Fixes JSON Errors)
@app.route("/upload", methods=["POST"])
def upload_resume():
    try:
        if "resume" not in request.files or "job_description" not in request.form:
            return jsonify({"error": "No file or job description provided"}), 400

        file = request.files["resume"]
        job_desc = request.form["job_description"]

        # Extract & Preprocess Text
        resume_text = extract_text_from_pdf(file)
        preprocessed_resume = preprocess_text(resume_text)
        preprocessed_job_desc = preprocess_text(job_desc)

        # Compute Scores
        similarity_score = calculate_text_similarity(preprocessed_resume, preprocessed_job_desc)
        skill_match_score, missing_skills = calculate_skill_match(preprocessed_resume, preprocessed_job_desc)
        education_match_score = calculate_education_match(preprocessed_resume, preprocessed_job_desc)
        overall_match = round(float((similarity_score + skill_match_score + education_match_score) / 3), 2)

        # AI-Enhanced Resume
        improved_resume_text = improve_resume(resume_text, job_desc)

        # Final JSON Response
        match_result = {
            "overall_score": overall_match,
            "skill_match": skill_match_score,
            "education_match": education_match_score,
            "text_similarity": similarity_score,
            "missing_skills": missing_skills,
            "improved_text": improved_resume_text
        }

        return jsonify({"match_result": match_result})

    except Exception as e:
        print(f"🚨 Error Processing Resume: {e}")
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500

# ✅ Run Flask Server
if __name__ == "__main__":
    app.run(debug=True)
