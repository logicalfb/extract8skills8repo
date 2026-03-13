from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests
import re

app = FastAPI()

# This allows your future JavaScript frontend to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class RepoRequest(BaseModel):
    url: str

def extract_owner_repo(url):
    match = re.search(r"github\.com/([^/]+)/([^/]+)", url)
    if match:
        repo = match.group(2).replace(".git", "").strip("/")
        return match.group(1), repo
    return None, None

def get_technology_scores(repo_url):
    owner, repo = extract_owner_repo(repo_url)
    if not owner or not repo:
        return None
    
    headers = {"Accept": "application/vnd.github.v3+json"}
    lang_url = f"https://api.github.com/repos/{owner}/{repo}/languages"
    lang_response = requests.get(lang_url, headers=headers)
    
    if lang_response.status_code == 200:
        languages_data = lang_response.json()
        if not languages_data:
            return None

        total_bytes = sum(languages_data.values())
        language_scores = {}
        
        for lang, bytes_count in languages_data.items():
            percentage = (bytes_count / total_bytes) * 100
            language_scores[lang] = round(percentage, 2)
            
        return dict(sorted(language_scores.items(), key=lambda item: item[1], reverse=True))
    return None

@app.post("/analyze")
def analyze_repo(request: RepoRequest):
    scores = get_technology_scores(request.url)
    if not scores:
        raise HTTPException(status_code=400, detail="Invalid URL or GitHub API limit reached.")
    return {"repository": request.url, "scores": scores}
