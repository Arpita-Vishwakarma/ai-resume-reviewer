import os
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import fitz  # PyMuPDF

# LangChain imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# ✅ Load environment variables
load_dotenv()

app = FastAPI(title="AI Resume Reviewer")

# ✅ Allow frontend (React, static HTML, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Setup templates directory
templates = Jinja2Templates(directory="templates")

# ✅ Get model and key from .env
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")  # default fallback

if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found in .env file!")

# ✅ Initialize Gemini model
llm = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL,
    api_key=GEMINI_API_KEY
)

# ✅ Define HR review prompt
prompt = PromptTemplate(
    input_variables=["resume_text"],
    template="""
You are an experienced HR recruiter reviewing a candidate's resume for a Python Developer role.

Resume:
{resume_text}

Your task:
1. Give a **rating (1–10)** based on relevance and strength.
2. Write a short **summary** of what stands out.
3. Suggest **3 specific improvements** to make it more appealing.

Respond clearly in sections:
Rating:
Summary:
Improvements:
"""
)

# ✅ LangChain pipeline
chain = prompt | llm | StrOutputParser()


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file using PyMuPDF."""
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text.strip()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve upload page."""
    return templates.TemplateResponse("upload.html", {"request": request})


@app.post("/analyze-resume/")
async def analyze_resume(file: UploadFile = File(...)):
    """Analyze uploaded resume and return structured AI feedback."""
    try:
        # Save uploaded PDF temporarily
        file_path = f"temp_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Extract text
        resume_text = extract_text_from_pdf(file_path)
        os.remove(file_path)

        # Get AI feedback
        raw_feedback = chain.invoke({"resume_text": resume_text})

        # Parse response into structured data
        lines = raw_feedback.splitlines()
        rating, summary = "", ""
        improvements = []

        section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.lower().startswith("rating"):
                section = "rating"
                rating = line
            elif line.lower().startswith("summary"):
                section = "summary"
                summary = ""
            elif line.lower().startswith("improvements"):
                section = "improvements"
            elif section == "summary":
                summary += line + " "
            elif section == "improvements" and (line.startswith("-") or line.startswith("•") or line[0].isdigit()):
                improvements.append(line.strip("•-1234567890. ").strip())

        return {
            "rating": rating or "Rating not found",
            "summary": summary.strip() or "No summary provided.",
            "improvements": improvements or ["No improvements detected."],
            "raw_feedback": raw_feedback
        }

    except Exception as e:
        return {"error": str(e)}
