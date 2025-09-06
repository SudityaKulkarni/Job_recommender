from pydantic_ai import Agent
from pydantic import BaseModel
from typing import List
from .schemas import JobRoles
from pydantic_ai.models.gemini import GeminiModel
import os
from dotenv import load_dotenv
import httpx

load_dotenv()

ADZUNA_API_ID = os.getenv("ADZUNA_API_ID")
ADZUNA_API_KEY = os.getenv("ADZUNA_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

#defining the agent
gemini_model = GeminiModel("gemini-1.5-flash")
job_role_agent = Agent(gemini_model)


#function to get job roles using generative AI agent
async def get_job_roles(skills: List[str]) -> JobRoles:
    prompt = f"""Suggest a few suitable job roles based for the following skills: {', '.join(skills)}
    Return the result strictly in JSON format as:
    {{
        "roles": ["Role1", "Role2", "Role3"]
    }}"""
    result = await job_role_agent.run(prompt)
    # Access the output content from the AgentRunResult
    response_text = result.output
    
    # Clean up the response more thoroughly
    response_text = response_text.strip()
    
    # Remove markdown code blocks
    if response_text.startswith('```json'):
        response_text = response_text[7:]  # Remove ```json
    elif response_text.startswith('```'):
        response_text = response_text[3:]   # Remove ```
    
    if response_text.endswith('```'):
        response_text = response_text[:-3]  # Remove trailing ```
    
    response_text = response_text.strip()
    
    return JobRoles.parse_raw(response_text)


#function to get job links from adzuna api
async def get_job_links(role:str, location: str = "India"):
    url = "https://api.adzuna.com/v1/api/jobs/in/search/1"
    params = {
        "app_id": ADZUNA_API_ID,
        "app_key": ADZUNA_API_KEY,
        "what": role,
        "where": location,
        "results_per_page": 5,
        "content-type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()

    return [
        {
            "title": job.get("title"),
            "company": job.get("company", {}).get("display_name"),
            "location": job.get("location", {}).get("display_name"),
            "url": job.get("redirect_url")
        }
        for job in data.get("results", [])
    ]
    

        