import os
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import fitz  # PyMuPDF

# LangChain (modular imports)
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain.chains.llm import LLMChain




# Load environment variables
load_dotenv()

app = FastAPI(title="AI Resume Reviewer")

# Allow frontend access (React Native, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup Gemini model
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key=os.getenv("GEMINI_API_KEY"))

# Prompt template
prompt = PromptTemplate(
    input_variables=["resume_text"],
    template="""
You are an experienced HR recruiter.
Here is a candidate's resume:

{resume_text}

Rate this resume on a scale of 1 to 10 for a Python Developer role.
Then, suggest 3 specific improvements to make it more appealing.
Respond in clear, structured bullet points.
"""
)

chain = LLMChain(llm=llm, prompt=prompt)


def extract_text_from_pdf(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text


@app.post("/analyze-resume/")
async def analyze_resume(file: UploadFile = File(...)):
    try:
        file_path = f"temp_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(await file.read())

        resume_text = extract_text_from_pdf(file_path)
        os.remove(file_path)

        response = chain.invoke({"resume_text": resume_text})
        return {"feedback": response["text"]}
    except Exception as e:
        return {"error": str(e)}
