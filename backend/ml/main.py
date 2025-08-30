from fastapi import FastAPI, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import spacy
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import pipeline
import PyPDF2
import docx
import io
import re

from schemas import (
    ResumeMatchRequest, ResumeMatchResponse, ResumeEnhanceRequest,
    ResumeEnhanceResponse, SkillExtractionResponse, MessageResponse
)
from config import settings

app = FastAPI(
    title="Auto Job Apply - ML Service",
    description="Machine Learning service for resume parsing and job matching",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load ML models
nlp = spacy.load("en_core_web_sm")
vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)

# Initialize HuggingFace pipeline for text generation
try:
    text_generator = pipeline("text-generation", model="gpt2", max_length=100)
except Exception:
    text_generator = None


class MLService:
    @staticmethod
    def extract_text_from_pdf(file_content: bytes) -> str:
        """Extract text from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to extract text from PDF: {str(e)}"
            )
    
    @staticmethod
    def extract_text_from_docx(file_content: bytes) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(io.BytesIO(file_content))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to extract text from DOCX: {str(e)}"
            )
    
    @staticmethod
    def extract_skills(text: str) -> List[str]:
        """Extract skills from text using spaCy NLP"""
        doc = nlp(text.lower())
        
        # Common technical skills patterns
        skill_patterns = [
            r'\b(?:python|java|javascript|typescript|c\+\+|c#|php|ruby|go|rust|swift|kotlin)\b',
            r'\b(?:react|angular|vue|node\.?js|express|django|flask|spring|laravel)\b',
            r'\b(?:mysql|postgresql|mongodb|redis|elasticsearch|cassandra)\b',
            r'\b(?:aws|azure|gcp|docker|kubernetes|jenkins|git|github|gitlab)\b',
            r'\b(?:html|css|sass|less|bootstrap|tailwind)\b',
            r'\b(?:machine learning|deep learning|ai|nlp|computer vision)\b',
            r'\b(?:tensorflow|pytorch|scikit-learn|pandas|numpy)\b',
        ]
        
        skills = set()
        
        # Extract using regex patterns
        for pattern in skill_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            skills.update(matches)
        
        # Extract using spaCy entities and noun phrases
        for ent in doc.ents:
            if ent.label_ in ["ORG", "PRODUCT", "LANGUAGE"]:
                skills.add(ent.text.lower())
        
        # Extract noun phrases that might be skills
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) <= 3:  # Short phrases
                skills.add(chunk.text.lower())
        
        # Filter and clean skills
        cleaned_skills = []
        for skill in skills:
            skill = skill.strip().title()
            if len(skill) > 2 and skill.isalpha() or '.' in skill or '+' in skill or '#' in skill:
                cleaned_skills.append(skill)
        
        return list(set(cleaned_skills))[:20]  # Return top 20 unique skills
    
    @staticmethod
    def calculate_match_score(resume_text: str, job_description: str) -> Dict[str, Any]:
        """Calculate job match score using cosine similarity"""
        try:
            # Preprocess texts
            resume_clean = MLService._preprocess_text(resume_text)
            job_clean = MLService._preprocess_text(job_description)
            
            # Vectorize texts
            texts = [resume_clean, job_clean]
            tfidf_matrix = vectorizer.fit_transform(texts)
            
            # Calculate cosine similarity
            similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            match_score = float(similarity_matrix[0][0]) * 100
            
            # Extract skills from both texts
            resume_skills = set(skill.lower() for skill in MLService.extract_skills(resume_text))
            job_skills = set(skill.lower() for skill in MLService.extract_skills(job_description))
            
            # Find missing skills
            missing_skills = list(job_skills - resume_skills)
            
            # Find common skills
            common_skills = list(resume_skills & job_skills)
            
            return {
                "match_score": round(match_score, 2),
                "missing_keywords": missing_skills[:10],  # Top 10 missing skills
                "common_skills": common_skills[:10],  # Top 10 common skills
                "resume_skills_count": len(resume_skills),
                "job_skills_count": len(job_skills)
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to calculate match score: {str(e)}"
            )
    
    @staticmethod
    def _preprocess_text(text: str) -> str:
        """Preprocess text for analysis"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^a-zA-Z0-9\s\+\#\.]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    @staticmethod
    def generate_resume_suggestions(resume_text: str, missing_skills: List[str]) -> List[str]:
        """Generate resume enhancement suggestions"""
        suggestions = []
        
        # Basic suggestions based on missing skills
        if missing_skills:
            suggestions.append(f"Consider adding these skills to your resume: {', '.join(missing_skills[:5])}")
        
        # Check for common resume sections
        resume_lower = resume_text.lower()
        
        if "summary" not in resume_lower and "objective" not in resume_lower:
            suggestions.append("Add a professional summary or objective section at the top of your resume")
        
        if "experience" not in resume_lower and "work" not in resume_lower:
            suggestions.append("Include a detailed work experience section with quantifiable achievements")
        
        if "education" not in resume_lower:
            suggestions.append("Add an education section with your qualifications")
        
        if "project" not in resume_lower:
            suggestions.append("Include relevant projects to showcase your skills")
        
        # Check for quantifiable achievements
        if not re.search(r'\d+%|\d+\s*years?|\d+\s*months?|\$\d+', resume_text):
            suggestions.append("Add quantifiable achievements and metrics to demonstrate your impact")
        
        return suggestions[:5]  # Return top 5 suggestions


@app.post("/resume/match", response_model=ResumeMatchResponse)
async def match_resume_to_job(request: ResumeMatchRequest):
    """Match resume to job description and provide score"""
    try:
        match_result = MLService.calculate_match_score(
            request.resume_text,
            request.job_description
        )
        
        return ResumeMatchResponse(
            match_score=match_result["match_score"],
            missing_keywords=match_result["missing_keywords"],
            common_skills=match_result["common_skills"],
            resume_skills_count=match_result["resume_skills_count"],
            job_skills_count=match_result["job_skills_count"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Resume matching failed: {str(e)}"
        )


@app.post("/resume/enhance", response_model=ResumeEnhanceResponse)
async def enhance_resume(request: ResumeEnhanceRequest):
    """Provide resume enhancement suggestions"""
    try:
        # Extract current skills from resume
        current_skills = MLService.extract_skills(request.resume_text)
        
        # Generate suggestions
        suggestions = MLService.generate_resume_suggestions(
            request.resume_text,
            request.missing_skills or []
        )
        
        return ResumeEnhanceResponse(
            suggestions=suggestions,
            recommended_skills=request.missing_skills[:10] if request.missing_skills else [],
            current_skills=current_skills
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Resume enhancement failed: {str(e)}"
        )


@app.post("/resume/extract-skills", response_model=SkillExtractionResponse)
async def extract_skills_from_text(
    file: UploadFile = File(..., description="Resume file (PDF, DOC, DOCX)")
):
    """Extract skills from uploaded resume file"""
    try:
        # Read file content
        file_content = await file.read()
        
        # Extract text based on file type
        if file.filename.lower().endswith('.pdf'):
            text = MLService.extract_text_from_pdf(file_content)
        elif file.filename.lower().endswith(('.doc', '.docx')):
            text = MLService.extract_text_from_docx(file_content)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file format. Please upload PDF, DOC, or DOCX files."
            )
        
        # Extract skills
        skills = MLService.extract_skills(text)
        
        return SkillExtractionResponse(
            extracted_text=text[:1000] + "..." if len(text) > 1000 else text,
            skills=skills,
            skill_count=len(skills)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Skill extraction failed: {str(e)}"
        )


@app.post("/text/analyze")
async def analyze_job_description(job_description: str):
    """Analyze job description and extract requirements"""
    try:
        # Extract skills and requirements
        skills = MLService.extract_skills(job_description)
        
        # Extract experience requirements
        experience_pattern = r'(\d+)[\+\-\s]*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)'
        experience_matches = re.findall(experience_pattern, job_description.lower())
        min_experience = int(experience_matches[0]) if experience_matches else None
        
        # Extract salary information
        salary_pattern = r'(?:salary|pay|compensation).*?(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:k|thousand|lakh|crore)?'
        salary_matches = re.findall(salary_pattern, job_description.lower())
        
        # Extract location
        location_pattern = r'(?:location|based in|office in)\s*:?\s*([a-zA-Z\s,]+)'
        location_matches = re.findall(location_pattern, job_description, re.IGNORECASE)
        location = location_matches[0].strip() if location_matches else None
        
        return {
            "required_skills": skills,
            "min_experience_years": min_experience,
            "salary_info": salary_matches,
            "location": location,
            "skill_count": len(skills)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Job description analysis failed: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "service": "ml", 
        "timestamp": "2025-08-29T20:22:00Z",
        "models_loaded": {
            "spacy": True,
            "transformers": text_generator is not None
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
