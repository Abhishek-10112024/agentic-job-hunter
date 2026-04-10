from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import os
import json
import re


def extract_resume_info(resume_text: str):
    llm = ChatOpenAI(
        temperature=0,
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1",
        model="llama-3.1-8b-instant"
    )

    prompt = PromptTemplate(
        input_variables=["resume"],
        template="""
        Extract structured information from the following resume:

        Resume:
        {resume}

        Return ONLY valid JSON (no explanation, no markdown):
        {{
            "skills": [],
            "experience": [],
            "roles": [],
            "domains": []
        }}
        """
    )

    chain = prompt | llm
    response = chain.invoke({"resume": resume_text})

    raw_output = response.content

    # 🔥 CLEAN MARKDOWN
    cleaned_output = re.sub(r"```json|```", "", raw_output).strip()

    # 🔥 PARSE JSON SAFELY
    try:
        parsed_output = json.loads(cleaned_output)
    except:
        parsed_output = {"error": "Failed to parse JSON", "raw": cleaned_output}

    return parsed_output