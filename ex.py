import requests
import re

def extract_owner_repo(url):
    """Extracts the owner and repository name from a GitHub URL."""
    match = re.search(r"github\.com/([^/]+)/([^/]+)", url)
    if match:
        repo = match.group(2).replace(".git", "").strip("/")
        return match.group(1), repo
    return None, None

def get_technology_scores(repo_url, github_token=None):
    owner, repo = extract_owner_repo(repo_url)
    if not owner or not repo:
        print("Invalid GitHub URL. Please provide a valid link.")
        return None
    
    headers = {"Accept": "application/vnd.github.v3+json"}
    if github_token:
        headers['Authorization'] = f"token {github_token}"
    
    print(f"Analyzing repository: {owner}/{repo}...\n")

    # Fetch Programming Languages and their byte counts
    lang_url = f"https://api.github.com/repos/{owner}/{repo}/languages"
    lang_response = requests.get(lang_url, headers=headers)
    
    if lang_response.status_code == 200:
        languages_data = lang_response.json()
        
        if not languages_data:
            print("No language data found for this repository.")
            return None

        # Calculate total bytes across all languages
        total_bytes = sum(languages_data.values())
        
        language_scores = {}
        
        # Calculate percentage (score / 100) for each language
        for lang, bytes_count in languages_data.items():
            percentage = (bytes_count / total_bytes) * 100
            # Round to 2 decimal places for a clean score
            language_scores[lang] = round(percentage, 2)
            
        # Sort the dictionary by score in descending order
        sorted_scores = dict(sorted(language_scores.items(), key=lambda item: item[1], reverse=True))
        return sorted_scores
        
    elif lang_response.status_code in [403, 429]:
        print("GitHub API rate limit exceeded. Try adding a GitHub Personal Access Token.")
        return None
    else:
        print(f"Failed to fetch repository data. Status code: {lang_response.status_code}")
        return None

# --- How to run the script ---
if __name__ == "__main__":
    url = input("Enter the GitHub repository URL: ")
    
    # Optional: Put your GitHub token here if you hit API limits
    # token = "YOUR_GITHUB_TOKEN" 
    
    scores = get_technology_scores(url) # Pass github_token=token if needed

    if scores:
        print("=== Language Scores (/100) ===")
        for lang, score in scores.items():
            # Formatting the output to look like a clean score and percentage
            print(f"{lang.ljust(15)}: {score:>5}%  (Score: {score}/100)")
            