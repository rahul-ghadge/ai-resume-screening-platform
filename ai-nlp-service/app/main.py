"""
AI Resume Screening — Python NLP Microservice
=============================================
FastAPI service that provides:
  - Skill extraction from raw resume text
  - Named entity recognition (NER)
  - Resume-to-job match scoring
  - Text summarization

Dependencies: fastapi, uvicorn, spacy, transformers, sentence-transformers
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import re
import logging
import time
import os

# ── Optional heavy imports (graceful fallback) ──────────────
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except Exception:
    SPACY_AVAILABLE = False
    logging.warning("spaCy not available — using rule-based fallback")

try:
    from sentence_transformers import SentenceTransformer, util
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    SBERT_AVAILABLE = True
except Exception:
    SBERT_AVAILABLE = False
    logging.warning("sentence-transformers not available — using keyword matching")

# ── App setup ───────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Resume Screening — NLP Microservice",
    description="NLP-powered skill extraction and job matching scoring",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Skill taxonomy (expandable — load from DB in production) ─
TECH_SKILLS = {
    "languages": [
        "java", "python", "javascript", "typescript", "kotlin", "scala",
        "go", "golang", "rust", "c++", "c#", "ruby", "php", "swift", "r",
    ],
    "frameworks": [
        "spring boot", "spring", "django", "flask", "fastapi", "react",
        "angular", "vue", "node.js", "nodejs", "express", "nestjs",
        "hibernate", "jpa", "rails", "laravel",
    ],
    "databases": [
        "mysql", "postgresql", "mongodb", "elasticsearch", "redis",
        "cassandra", "oracle", "dynamodb", "neo4j", "sqlite", "mariadb",
    ],
    "cloud_devops": [
        "aws", "azure", "gcp", "docker", "kubernetes", "k8s", "terraform",
        "ansible", "jenkins", "github actions", "gitlab ci", "circleci", "helm",
        "prometheus", "grafana", "elk stack",
    ],
    "messaging": [
        "kafka", "rabbitmq", "activemq", "sqs", "pubsub", "nats",
    ],
    "ai_ml": [
        "machine learning", "deep learning", "tensorflow", "pytorch",
        "scikit-learn", "nlp", "bert", "gpt", "openai", "langchain",
        "computer vision", "mlops", "mlflow",
    ],
}
ALL_SKILLS = [s for skills in TECH_SKILLS.values() for s in skills]

SOFT_SKILLS = [
    "leadership", "communication", "teamwork", "problem solving",
    "critical thinking", "adaptability", "time management", "creativity",
    "collaboration", "mentoring", "project management", "agile", "scrum",
]

EDUCATION_LEVELS = {
    "phd": 5, "doctorate": 5, "master": 4, "msc": 4, "mba": 4,
    "bachelor": 3, "bsc": 3, "be": 3, "b.tech": 3, "b.e": 3,
    "associate": 2, "diploma": 1,
}


# ── Pydantic models ──────────────────────────────────────────

class ExtractRequest(BaseModel):
    text: str = Field(..., min_length=10, description="Raw resume text")

class MatchScoreRequest(BaseModel):
    resume_text: str
    required_skills: List[str]
    preferred_skills: Optional[List[str]] = []

class Education(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_year: Optional[str] = None
    end_year: Optional[str] = None

class WorkExperience(BaseModel):
    company: Optional[str] = None
    title: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: Optional[bool] = False
    description: Optional[str] = None
    technologies: Optional[List[str]] = []

class ExtractResponse(BaseModel):
    technical_skills: List[str]
    soft_skills: List[str]
    certifications: List[str]
    summary: Optional[str] = None
    experience_years: Optional[float] = None
    confidence_score: float
    work_experience: List[WorkExperience] = []
    education: List[Education] = []
    processing_time_ms: int

class MatchScoreResponse(BaseModel):
    score: float
    skill_match_score: float
    semantic_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    explanation: str


# ── Extraction helpers ───────────────────────────────────────

def extract_technical_skills(text: str) -> List[str]:
    lower = text.lower()
    found = []
    for skill in ALL_SKILLS:
        if skill.lower() in lower:
            # Word boundary check for short skills
            if len(skill) <= 3:
                pattern = r'\b' + re.escape(skill) + r'\b'
                if re.search(pattern, lower):
                    found.append(skill.title())
            else:
                found.append(skill.title())
    return sorted(set(found))


def extract_soft_skills(text: str) -> List[str]:
    lower = text.lower()
    return sorted(set(
        skill.title() for skill in SOFT_SKILLS if skill in lower
    ))


def extract_certifications(text: str) -> List[str]:
    cert_patterns = [
        r'\b(AWS Certified[\w\s]+)\b',
        r'\b(Google Cloud Professional[\w\s]+)\b',
        r'\b(Microsoft Certified[\w\s]+)\b',
        r'\b(Certified Kubernetes[\w\s]+)\b',
        r'\b(CKA|CKAD|CKS)\b',
        r'\b(PMP|PRINCE2)\b',
        r'\b(Scrum Master|CSM|PSM)\b',
        r'\b(CISSP|CompTIA[\w\s]+)\b',
        r'\b(Oracle Certified[\w\s]+)\b',
    ]
    found = []
    for pattern in cert_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        found.extend(matches)
    return list(set(found))


def extract_experience_years(text: str) -> Optional[float]:
    patterns = [
        r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:professional\s*)?experience',
        r'experience\s*(?:of\s*)?(\d+)\+?\s*years?',
        r'(\d+)\+?\s*years?\s*(?:in\s*)?(?:the\s*)?(?:industry|field)',
    ]
    max_years = 0.0
    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            try:
                years = float(match.group(1))
                max_years = max(max_years, years)
            except ValueError:
                pass
    return max_years if max_years > 0 else None


def extract_work_experience(text: str) -> List[WorkExperience]:
    """Heuristic work experience extraction — enhance with NER in production."""
    experiences = []
    # Look for company patterns (simplistic — use NER/LLM in production)
    company_pattern = r'(?:at|@|with)\s+([A-Z][A-Za-z\s&,\.]+(?:Inc|Ltd|LLC|Corp|Co|Technologies|Solutions|Systems)?)'
    date_pattern    = r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[\s,]+(\d{4})'
    title_pattern   = r'(?:as|position|role|title)[\s:]+([A-Z][A-Za-z\s]+(?:Engineer|Developer|Manager|Lead|Architect|Analyst|Designer|Scientist))'

    companies = re.findall(company_pattern, text)
    titles    = re.findall(title_pattern, text)

    for i, company in enumerate(companies[:5]):  # max 5
        exp = WorkExperience(
            company=company.strip(),
            title=titles[i].strip() if i < len(titles) else None,
        )
        experiences.append(exp)
    return experiences


def extract_education(text: str) -> List[Education]:
    """Extract education entries."""
    education = []
    degree_patterns = [
        r'(Bachelor|Master|PhD|Doctorate|B\.?Sc|M\.?Sc|MBA|B\.?E|B\.?Tech|M\.?Tech)'
        r'[\s,]+(?:in|of|–|-|:)?\s*([A-Za-z\s]+?)(?:\s+from\s+|\s+at\s+|\s+,\s+)?'
        r'([A-Z][A-Za-z\s,]+University|[A-Z][A-Za-z\s,]+College|[A-Z][A-Za-z\s,]+Institute)?'
    ]
    for pattern in degree_patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            edu = Education(
                degree=match.group(1),
                field_of_study=match.group(2).strip() if match.group(2) else None,
                institution=match.group(3).strip() if match.group(3) else None,
            )
            education.append(edu)
    return education[:3]  # max 3 entries


def generate_summary(text: str, skills: List[str]) -> str:
    """Rule-based summary — replace with LLM in production."""
    exp_years = extract_experience_years(text)
    top_skills = skills[:5]
    exp_str = f"{int(exp_years)}+ years of experience" if exp_years else "Experience"
    skills_str = ", ".join(top_skills) if top_skills else "various technologies"
    return f"{exp_str} in {skills_str}."


def compute_keyword_match(resume_lower: str, required: List[str], preferred: List[str]) -> tuple:
    req_set  = {s.lower() for s in required}
    pref_set = {s.lower() for s in preferred}

    matched  = [s for s in req_set  if s in resume_lower]
    missing  = [s for s in req_set  if s not in resume_lower]
    bonus    = [s for s in pref_set if s in resume_lower]

    skill_score = (len(matched) / len(req_set) * 100) if req_set else 100.0
    bonus_boost = min(10.0, len(bonus) * 2.5)
    return min(100.0, skill_score + bonus_boost), matched, missing


def compute_semantic_score(resume_text: str, job_text: str) -> float:
    if not SBERT_AVAILABLE:
        return -1.0
    try:
        emb_resume = embedder.encode(resume_text[:2000], convert_to_tensor=True)
        emb_job    = embedder.encode(job_text[:1000],    convert_to_tensor=True)
        similarity = util.cos_sim(emb_resume, emb_job).item()
        return round(similarity * 100, 2)
    except Exception as e:
        logger.warning(f"Semantic scoring failed: {e}")
        return -1.0


# ── API Endpoints ────────────────────────────────────────────

@app.get("/health")
def health():
    return {
        "status": "UP",
        "spacy": SPACY_AVAILABLE,
        "sentence_transformers": SBERT_AVAILABLE,
    }


@app.post("/api/v1/extract", response_model=ExtractResponse)
def extract_skills(request: ExtractRequest):
    """Extract structured information from raw resume text."""
    start = time.time()
    text  = request.text

    try:
        tech_skills   = extract_technical_skills(text)
        soft_skills   = extract_soft_skills(text)
        certifications = extract_certifications(text)
        exp_years     = extract_experience_years(text)
        work_exp      = extract_work_experience(text)
        education     = extract_education(text)
        summary       = generate_summary(text, tech_skills)

        # Confidence: more skills + experience found = higher confidence
        confidence = min(1.0, (len(tech_skills) * 0.05) + (0.3 if exp_years else 0.0) + 0.3)

        elapsed_ms = int((time.time() - start) * 1000)
        logger.info(f"Extracted {len(tech_skills)} skills in {elapsed_ms}ms")

        return ExtractResponse(
            technical_skills=tech_skills,
            soft_skills=soft_skills,
            certifications=certifications,
            summary=summary,
            experience_years=exp_years,
            confidence_score=round(confidence, 2),
            work_experience=work_exp,
            education=education,
            processing_time_ms=elapsed_ms,
        )
    except Exception as e:
        logger.error(f"Extraction failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/match-score", response_model=MatchScoreResponse)
def compute_match_score(request: MatchScoreRequest):
    """Compute a resume-to-job match score (0–100)."""
    resume_lower = request.resume_text.lower()

    # Keyword match
    skill_score, matched, missing = compute_keyword_match(
        resume_lower, request.required_skills, request.preferred_skills or [])

    # Semantic match (if available)
    job_text     = " ".join(request.required_skills + (request.preferred_skills or []))
    semantic_score = compute_semantic_score(request.resume_text, job_text)

    if semantic_score >= 0:
        final_score = (skill_score * 0.6) + (semantic_score * 0.4)
    else:
        final_score = skill_score

    final_score = round(min(100.0, final_score), 2)
    logger.info(f"Match score computed: {final_score} (skill={skill_score:.1f}, semantic={semantic_score:.1f})")

    return MatchScoreResponse(
        score=final_score,
        skill_match_score=round(skill_score, 2),
        semantic_score=round(semantic_score, 2) if semantic_score >= 0 else 0.0,
        matched_skills=matched,
        missing_skills=missing,
        explanation=(
            f"Matched {len(matched)}/{len(request.required_skills)} required skills. "
            f"Semantic similarity: {'N/A' if semantic_score < 0 else f'{semantic_score:.1f}%'}."
        ),
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
