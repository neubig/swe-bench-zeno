import os
import requests
import json

# Get the GitHub token from the environment variable
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

# Function to fetch issues from a GitHub repository
def fetch_issues(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

# Function to save issues to a file
def save_issues(issues, filename):
    with open(filename, 'w') as f:
        json.dump(issues, f, indent=4)

def main():
    owner = input("Enter the repository owner: ")
    repo = input("Enter the repository name: ")
    issues = fetch_issues(owner, repo)
    filename = f"data/{owner}_{repo}_issues.json"
    save_issues(issues, filename)
    print(f"Issues saved to {filename}")

if __name__ == "__main__":
    main()
