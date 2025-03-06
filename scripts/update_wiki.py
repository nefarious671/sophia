import os
import requests
import base64

def update_wiki():
    token = os.getenv('SOPHIA_TOKEN')  # Read the token from environment variable
    if not token:
        raise ValueError("SOPHIA_TOKEN is not set")

    repo = 'nefarious671/sophia.wiki'  # Use the correct Wiki repository
    page = 'Home'  # The Wiki page to update (case-sensitive)
    new_content = 'Updated content for the Wiki page.'  # Replace with actual content
    api_url = f'https://api.github.com/repos/{repo}/contents/{page}.md'

    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # Get the current page content (to retrieve SHA)
    response = requests.get(api_url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        sha = data['sha']
    elif response.status_code == 404:
        sha = None  # Page doesn't exist yet, will be created
    else:
        response.raise_for_status()

    # Encode content to Base64 (GitHub API requirement)
    encoded_content = base64.b64encode(new_content.encode()).decode()

    # Prepare the update request
    update_data = {
        'message': f'Update {page} page',
        'content': encoded_content,
        'sha': sha if sha else None  # Include SHA if page exists
    }

    # Send update request
    update_response = requests.put(api_url, headers=headers, json=update_data)
    update_response.raise_for_status()
    
    print(f'✅ Successfully updated "{page}" Wiki page!')

if __name__ == '__main__':
    update_wiki()
