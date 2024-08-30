import customtkinter as ctk
import requests
import os

# Function to search GitHub for code using the GitHub API
def search_github_for_code(token, repository_path, snippet_length, result_textbox):
    github_search_api = "https://api.github.com/search/code"
    file_extensions = [
        ".py", ".java", ".js", ".c", ".cpp", ".cc", ".cxx", ".cs", ".rb", ".php", 
        ".go", ".swift", ".ts", ".kt", ".kts", ".rs", ".dart", ".pl", ".pm", 
        ".r", ".scala", ".hs", ".m", ".mm", ".sh"
    ]

    repo_files = []
    for root, _, files in os.walk(repository_path):
        for file_name in files:
            if any(file_name.endswith(ext) for ext in file_extensions):
                repo_files.append(os.path.join(root, file_name))

    headers = {"Authorization": f"token {token}"}
    total_copied_lines = 0

    result_textbox.delete("1.0", ctk.END)  # Clear the result box before showing new results

    for file_path in repo_files:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        copied_lines_count = 0
        for i in range(len(lines) - snippet_length + 1):
            snippet = "".join(lines[i:i + snippet_length])

            params = {
                "q": f'"{snippet.strip()}" in:file',
                "per_page": 5
            }

            response = requests.get(github_search_api, headers=headers, params=params)
            
            if response.status_code == 200:
                search_results = response.json()
                total_matches = search_results.get('total_count', 0)
                
                if total_matches > 0:
                    copied_lines_count += snippet_length
                    result_textbox.insert(ctk.END, f"\nMatch found in {file_path}:\n")
                    for item in search_results.get('items', []):
                        result_textbox.insert(ctk.END, f"- {item['repository']['html_url']} ({item['path']})\n")
                else:
                    result_textbox.insert(ctk.END, f"Match not found for snippet from {file_path}\n")
            else:
                result_textbox.insert(ctk.END, f"Error: {response.status_code} - {response.text}\n")

        total_copied_lines += copied_lines_count

    if total_copied_lines > 0:
        result_textbox.insert(ctk.END, f"\nTotal copied lines found: {total_copied_lines}\n")
    else:
        result_textbox.insert(ctk.END, "Match not found in any file.\n")

# Function to start the plagiarism check process
def start_check():
    token = token_entry.get().strip()
    repo_path = repo_path_entry.get().strip()
    snippet_length = int(snippet_length_entry.get().strip())
    search_github_for_code(token, repo_path, snippet_length, result_textbox)

# Creating the main GUI window
app = ctk.CTk()
app.geometry("600x600")
app.title("AI-Based Plagiarism Detection")

ctk.CTkLabel(app, text="GitHub Personal Access Token:").pack(pady=5)
token_entry = ctk.CTkEntry(app, width=400)
token_entry.pack()

ctk.CTkLabel(app, text="Repository Path:").pack(pady=5)
repo_path_entry = ctk.CTkEntry(app, width=400)
repo_path_entry.pack()

ctk.CTkLabel(app, text="Number of Lines to Check:").pack(pady=5)
snippet_length_entry = ctk.CTkEntry(app, width=50)
snippet_length_entry.pack()

check_button = ctk.CTkButton(app, text="Check for Plagiarism", command=start_check)
check_button.pack(pady=10)

result_textbox = ctk.CTkTextbox(app, width=550, height=300)
result_textbox.pack(pady=10)

app.mainloop()