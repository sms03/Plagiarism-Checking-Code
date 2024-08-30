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
                    result_textbox.insert(ctk.END, f"\nMatch found in {file_path}:\n", "match")
                    for item in search_results.get('items', []):
                        result_textbox.insert(ctk.END, f"- {item['repository']['html_url']} ({item['path']})\n", "match")
                else:
                    result_textbox.insert(ctk.END, f"Match not found for snippet from {file_path}\n", "no_match")
            else:
                result_textbox.insert(ctk.END, f"Error: {response.status_code} - {response.text}\n", "error")

        total_copied_lines += copied_lines_count

    if total_copied_lines > 0:
        result_textbox.insert(ctk.END, f"\nTotal copied lines found: {total_copied_lines}\n", "match")
    else:
        result_textbox.insert(ctk.END, "Match not found in any file.\n", "no_match")

# Function to start the plagiarism check process
def start_check():
    try:
        token = token_entry.get().strip()
        repo_path = repo_path_entry.get().strip()
        snippet_length = int(snippet_length_entry.get().strip())
        search_github_for_code(token, repo_path, snippet_length, result_textbox)
    except ValueError:
        result_textbox.insert(ctk.END, "Please enter a valid number for lines to check.\n", "error")

# Creating the main GUI window
app = ctk.CTk()
app.geometry("700x700")
app.title("AI-Based Plagiarism Detection")

# Configure pastel theme colors
ctk.set_appearance_mode("light")  # Options: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("blue")

app.configure(bg="#e0f7fa")  # Pastel light cyan background

# Styling for widgets
label_font = ("Arial", 14)
entry_font = ("Arial", 12)
button_font = ("Arial", 14, "bold")
result_textbox_font = ("Arial", 12)

# Creating labels and entry fields
token_label = ctk.CTkLabel(app, text="GitHub Personal Access Token:", font=label_font)
token_label.pack(pady=5)
token_entry = ctk.CTkEntry(app, width=400, font=entry_font)
token_entry.pack()

repo_path_label = ctk.CTkLabel(app, text="Repository Path:", font=label_font)
repo_path_label.pack(pady=5)
repo_path_entry = ctk.CTkEntry(app, width=400, font=entry_font)
repo_path_entry.pack()

snippet_length_label = ctk.CTkLabel(app, text="Number of Lines to Check:", font=label_font)
snippet_length_label.pack(pady=5)
snippet_length_entry = ctk.CTkEntry(app, width=50, font=entry_font)
snippet_length_entry.pack()

check_button = ctk.CTkButton(app, text="Check for Plagiarism", font=button_font, command=start_check, fg_color="#80deea", hover_color="#4dd0e1")
check_button.pack(pady=10)

result_textbox = ctk.CTkTextbox(app, width=600, height=300, font=result_textbox_font)
result_textbox.pack(pady=10)

# Corrected tagging setup for the result text box
result_textbox.tag_config("match", foreground="#388e3c")
result_textbox.tag_config("no_match", foreground="#d32f2f")
result_textbox.tag_config("error", foreground="#f57c00")

app.mainloop()
