from typing import Dict
from github import GithubException
from .config import get_github_client, GITHUB_USERNAME
from .code_generator import generate_readme as generate_readme_content


def get_mit_license() -> str:
    year = "2025"
    name = GITHUB_USERNAME or "Student"
    
    return f"""MIT License

Copyright (c) {year} {name}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


def create_or_update_repo(task: str, code_files: Dict[str, str], round_num: int) -> Dict[str, str]:
    try:
        github_client = get_github_client()
        user = github_client.get_user()
    except Exception as e:
        print(f"Failed to authenticate with GitHub: {str(e)}")
        print("Please check your GITHUB_TOKEN in .env file")
        raise
    
    repo_name = f"{task}-round-{round_num}"
    
    existing_repo = None
    try:
        existing_repo = user.get_repo(repo_name)
        print(f"Repository {repo_name} already exists, updating...")
    except GithubException:
        print(f"Creating new repository {repo_name}...")
    
    if existing_repo is None:
        repo = user.create_repo(
            name=repo_name,
            description=f"Generated app for task: {task}",
            private=False,
            auto_init=False
        )
        
        repo.create_file(
            path="LICENSE",
            message="Add MIT License",
            content=get_mit_license()
        )
        
        for filename, content in code_files.items():
            repo.create_file(
                path=filename,
                message=f"Add {filename}",
                content=content
            )
        
        repo.create_file(
            path="README.md",
            message="Add README",
            content=f"# {task}\n\nGenerated application for {task}"
        )
        
    else:
        repo = existing_repo
        
        for filename, content in code_files.items():
            try:
                file = repo.get_contents(filename)
                repo.update_file(
                    path=filename,
                    message=f"Update {filename} for round {round_num}",
                    content=content,
                    sha=file.sha
                )
            except GithubException:
                repo.create_file(
                    path=filename,
                    message=f"Add {filename} for round {round_num}",
                    content=content
                )
    
    try:
        repo.create_pages_site(
            source={
                "branch": "main",
                "path": "/"
            }
        )
        print("GitHub Pages enabled")
    except GithubException as e:
        if "already exists" not in str(e):
            print(f"Pages might already be enabled: {e}")
    
    commits = repo.get_commits()
    latest_commit_sha = commits[0].sha
    
    return {
        "repo_url": repo.html_url,
        "commit_sha": latest_commit_sha,
        "pages_url": f"https://{user.login}.github.io/{repo_name}/",
        "repo": repo
    }


def update_readme(repo, task: str, brief: str, repo_url: str, pages_url: str):
    readme_content = generate_readme_content(task, brief, repo_url, pages_url)
    
    try:
        readme_file = repo.get_contents("README.md")
        repo.update_file(
            path="README.md",
            message="Update README",
            content=readme_content,
            sha=readme_file.sha
        )
    except GithubException:
        repo.create_file(
            path="README.md",
            message="Add README",
            content=readme_content
        )
