import os
import sys
import requests
import base64

# GitHub Repo & Token Setup
GITHUB_TOKEN = os.getenv('SOPHIA_TOKEN')
REPO_OWNER = "nefarious671"
REPO_NAME = "sophia"
FOLDER_PATH = "rhif"  # Where Markdown files are stored

if not GITHUB_TOKEN:
    raise ValueError("SOPHIA_TOKEN is not set! Please set it in your environment variables.")

# GitHub API Headers
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def list_md_files():
    """Lists all Markdown files in the RHIF directory."""
    api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FOLDER_PATH}"
    response = requests.get(api_url, headers=HEADERS)
    if response.status_code == 200:
        files = [file["name"] for file in response.json() if file["name"].endswith(".md")]
        return files
    return []

def update_markdown_file(filename, content, mode="overwrite"):
    """Creates, updates, or appends to a Markdown file in the GitHub repository."""
    api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FOLDER_PATH}/{filename}"

    # Check if file exists
    response = requests.get(api_url, headers=HEADERS)
    sha = None
    existing_content = ""
    if response.status_code == 200:
        sha = response.json().get("sha")
        existing_content = base64.b64decode(response.json().get("content")).decode()
    elif response.status_code != 404:
        response.raise_for_status()
    
    # Handle different modes
    if mode == "append":
        content = existing_content + "\n" + content
    elif mode == "overwrite":
        pass  # Default behavior
    else:
        raise ValueError("Invalid mode. Use 'overwrite' or 'append'.")

    # Encode content in Base64 (GitHub API requirement)
    encoded_content = base64.b64encode(content.encode()).decode()

    # Prepare the update request
    update_data = {
        "message": f"Updated {filename}",
        "content": encoded_content,
        "sha": sha if sha else None  # Include SHA if updating
    }
    update_response = requests.put(api_url, headers=HEADERS, json=update_data)
    update_response.raise_for_status()
    print(f"✅ Successfully updated {filename} in {FOLDER_PATH}!")

def delete_markdown_file(filename):
    """Deletes a Markdown file from the GitHub repository."""
    api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FOLDER_PATH}/{filename}"
    response = requests.get(api_url, headers=HEADERS)
    if response.status_code != 200:
        print(f"❌ File '{filename}' not found.")
        return
    sha = response.json().get("sha")
    delete_data = {
        "message": f"Deleted {filename}",
        "sha": sha
    }
    delete_response = requests.delete(api_url, headers=HEADERS, json=delete_data)
    delete_response.raise_for_status()
    print(f"🗑️ Successfully deleted {filename}.")

def generate_index():
    """Generates an index.md file listing all Markdown files in the directory."""
    files = list_md_files()
    index_content = "# RHIF Index\n\n" + "\n".join([f"- [{file}](./{file})" for file in files])
    update_markdown_file("index.md", index_content, mode="overwrite")
    print("📜 Index updated!")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python rhif_markdown_manager.py <action> <filename> [content]")
        sys.exit(1)
    
    action = sys.argv[1].lower()
    filename = sys.argv[2]
    content = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else ""
    
    if action == "create" or action == "overwrite":
        update_markdown_file(filename, content, mode="overwrite")
    elif action == "append":
        update_markdown_file(filename, content, mode="append")
    elif action == "delete":
        delete_markdown_file(filename)
    elif action == "index":
        generate_index()
    else:
        print("❌ Invalid action. Use 'create', 'append', 'delete', or 'index'.")
