from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import os
import json


# 🔥 Advanced fallback skills (real-world gaps)
ADVANCED_SKILLS = [
    "Kubernetes",
    "Distributed Systems",
    "System Design",
    "Terraform",
    "Model Monitoring",
    "Data Pipelines",
    "Scalable ML Systems"
]


def analyze_skill_gap(resume_text: str, job: dict):
    try:
        llm = ChatOpenAI(
            temperature=0,
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
            model="llama-3.1-8b-instant"
        )

        prompt = PromptTemplate(
            input_variables=["resume", "job"],
            template="""
            Resume Skills:
            {resume}

            Job Title:
            {job}

            Task:
            - Identify ADVANCED or PRODUCTION-LEVEL skills required for this job
            - Compare with resume skills
            - Return ONLY skills that are NOT clearly present in resume

            IMPORTANT:
            - Do NOT repeat resume skills
            - Focus on real industry gaps (not basic tools)
            - Return max 3-5 skills

            Return ONLY JSON:

            {{
                "missing_skills": []
            }}
            """
        )

        chain = prompt | llm

        response = chain.invoke({
            "resume": resume_text,
            "job": job["title"]
        })

        # 🔥 Clean response
        cleaned = response.content.replace("```json", "").replace("```", "").strip()

        result = json.loads(cleaned)

        # 🔥 Fallback logic (VERY IMPORTANT)
        if not result.get("missing_skills"):
            result["missing_skills"] = ADVANCED_SKILLS[:3]

        return result

    except Exception as e:
        # 🔥 Safe fallback
        return {
            "missing_skills": ADVANCED_SKILLS[:3]
        }