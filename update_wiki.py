import os
import requests

def update_wiki():
    token = os.getenv('SOPHIA_TOKEN')
    if not token:
        raise ValueError("SOPHIA_TOKEN is not set")

    # Example: Update a Wiki page
    repo = 'username/repository'
    page = 'Home'
    content = 'Updated content for the Wiki page.'
    api_url = f'https://api.github.com/repos/{repo}/contents/wiki/{page}.md'

    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # Get the current page to retrieve the SHA
    response = requests.get(api_url, headers=headers)
    response.raise_for_status()
    data = response.json()
    sha = data['sha']

    # Update the page
    update_data = {
        'message': f'Update {page} page',
        'content': content.encode('utf-8').decode('utf-8'),
        'sha': sha
    }
    update_response = requests.put(api_url, headers=headers, json=update_data)
    update_response.raise_for_status()
    print(f'Updated {page} page successfully.')

if __name__ == '__main__':
    update_wiki()
