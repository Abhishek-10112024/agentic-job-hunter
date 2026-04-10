from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import os


def explain_match(resume_text: str, job: dict):
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
            Resume:
            {resume}

            Job:
            {job}

            Explain in 2 lines why this job matches the candidate.
            """
        )

        chain = prompt | llm
        response = chain.invoke({
            "resume": resume_text,
            "job": job["title"]
        })

        return response.content.strip()

    except Exception as e:
        return "Explanation unavailable"