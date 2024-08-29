import requests
import os

# List of commonly used programming language extensions
file_extensions = [
    ".py", ".java", ".js", ".c", ".cpp", ".cc", ".cxx", ".cs", ".rb", ".php", 
    ".go", ".swift", ".ts", ".kt", ".kts", ".rs", ".dart", ".pl", ".pm", 
    ".r", ".scala", ".hs", ".m", ".mm", ".sh"
]

def search_github_for_code(token, repository_path):
    # GitHub API endpoint
    github_search_api = "https://api.github.com/search/code"

    # User input for code snippet length
    snippet_length = int(input("Enter the number of lines to search for plagiarism (suggested: 5-20): "))

    # Gather all code files from the repository
    repo_files = []
    for root, _, files in os.walk(repository_path):
        for file_name in files:
            if any(file_name.endswith(ext) for ext in file_extensions):
                repo_files.append(os.path.join(root, file_name))

    # Iterate over each file to extract snippets and search GitHub
    headers = {"Authorization": f"token {token}"}
    match_found = False

    for file_path in repo_files:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        # Search in chunks to avoid too long snippets
        for i in range(len(lines) - snippet_length + 1):
            snippet = "".join(lines[i:i + snippet_length])

            # Search GitHub for this snippet
            params = {
                "q": f'"{snippet.strip()}" in:file',
                "per_page": 5  # Limit results to avoid too many API calls
            }

            response = requests.get(github_search_api, headers=headers, params=params)
            
            if response.status_code == 200:
                search_results = response.json()
                total_matches = search_results.get('total_count', 0)
                
                if total_matches > 0:
                    match_found = True
                    print(f"\nMatch found in {file_path} with {total_matches} matches:")
                    for item in search_results.get('items', []):
                        print(f"- {item['repository']['html_url']} ({item['path']})")
                else:
                    print(f"Match not found for snippet from {file_path}")
            else:
                print(f"Error: {response.status_code} - {response.text}")

    if not match_found:
        print("Match not found in any file.")

# User input for GitHub token and repository path
github_token = input("Enter your GitHub Personal Access Token: ").strip()
repository_path = input("Enter the path of the repository to check: ").strip()

search_github_for_code(github_token, repository_path)
