from typing import Dict, Optional
import requests
from github import GithubException
from .config import get_github_client, GITHUB_USERNAME, GITHUB_TOKEN
from .code_generator import generate_readme as generate_readme_content


def get_existing_code(task: str, path: str = "index.html") -> Optional[str]:
    try:
        github_client = get_github_client()
        user = github_client.get_user()
        repo = user.get_repo(task)

        try:
            contents = repo.get_contents(path, ref="main")
            if hasattr(contents, "decoded_content"):
                return contents.decoded_content.decode("utf-8")
            return None
        except GithubException:
            return None
    except Exception as e:
        print(f"Error fetching existing code: {str(e)}")
        return None


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


def create_or_update_repo(
    task: str, code_files: Dict[str, str], round_num: int
) -> Dict[str, str]:
    try:
        github_client = get_github_client()
        user = github_client.get_user()
    except Exception as e:
        print(f"Failed to authenticate with GitHub: {str(e)}")
        print("Please check your GITHUB_TOKEN in .env file")
        raise

    repo_name = task
    owner = user.login

    existing_repo = None
    try:
        existing_repo = user.get_repo(repo_name)
        print(
            f"Repository {repo_name} already exists, updating for round {round_num}..."
        )
        repo = existing_repo
    except GithubException as e:
        if e.status == 404:
            print(f"Creating new repository {repo_name}...")
            try:
                repo = user.create_repo(
                    name=repo_name,
                    description=f"Generated app for task: {task}",
                    private=False,
                    auto_init=False,
                )

                try:
                    repo.create_file(
                        path="LICENSE",
                        message="Add MIT License",
                        content=get_mit_license(),
                    )
                except GithubException as license_error:
                    if license_error.status != 422:
                        raise
                    print("LICENSE already exists, skipping...")

                try:
                    repo.create_file(
                        path="README.md",
                        message="Add README",
                        content=f"# {task}\n\nGenerated application for {task}",
                    )
                except GithubException as readme_error:
                    if readme_error.status != 422:
                        raise
                    print("README.md already exists, will be updated later...")

            except GithubException as create_error:
                if (
                    create_error.status == 422
                    and "name already exists" in str(create_error).lower()
                ):
                    print(
                        f"Repository {repo_name} was just created by another process, fetching it..."
                    )
                    repo = user.get_repo(repo_name)
                else:
                    raise
        else:
            raise

    index_content = code_files.get(
        "index.html", "<html><body><h1>Welcome</h1></body></html>"
    )

    upsert_pages_index(
        owner=owner,
        repo_name=repo_name,
        html=index_content,
        branch="main",
        path="index.html",
        commit_msg=f"Deploy app for round {round_num}",
    )

    commits = repo.get_commits()
    latest_commit_sha = commits[0].sha
    pages_url = f"https://{owner}.github.io/{repo_name}/"

    return {
        "repo_url": repo.html_url,
        "commit_sha": latest_commit_sha,
        "pages_url": pages_url,
        "repo": repo,
    }


def upsert_pages_index(
    owner: str,
    repo_name: str,
    html: str,
    branch: str = "main",
    path: str = "index.html",
    commit_msg: Optional[str] = None,
) -> None:
    commit_msg = commit_msg or f"Update {path} for GitHub Pages"

    gh = get_github_client()
    repo = gh.get_repo(f"{owner}/{repo_name}")

    try:
        contents = repo.get_contents(path, ref=branch)
        repo.update_file(
            path=path,
            message=commit_msg,
            content=html,
            sha=contents.sha,
            branch=branch,
        )
        print(f"{path} updated on {branch}")
    except GithubException as e:
        if getattr(e, "status", None) == 404 or "Not Found" in str(e):
            repo.create_file(
                path=path,
                message=f"Add {path} for GitHub Pages",
                content=html,
                branch=branch,
            )
            print(f"{path} created on {branch}")
        else:
            raise

    base = "https://api.github.com"
    hdrs = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    r = requests.get(f"{base}/repos/{owner}/{repo_name}/pages", headers=hdrs)
    if r.status_code == 404:
        body = {"source": {"branch": branch, "path": "/"}}
        cr = requests.post(
            f"{base}/repos/{owner}/{repo_name}/pages", headers=hdrs, json=body
        )
        if cr.status_code not in (201, 202):
            raise RuntimeError(
                f"Failed to create Pages site: {cr.status_code} {cr.text}"
            )
        print("Pages site created")
    elif r.ok:
        body = {"source": {"branch": branch, "path": "/"}}
        pr = requests.patch(
            f"{base}/repos/{owner}/{repo_name}/pages", headers=hdrs, json=body
        )
        if pr.status_code not in (200, 202):
            raise RuntimeError(
                f"Failed to update Pages config: {pr.status_code} {pr.text}"
            )
        print("Pages site updated")
    else:
        raise RuntimeError(f"Failed to query Pages site: {r.status_code} {r.text}")

    br = requests.post(f"{base}/repos/{owner}/{repo_name}/pages/builds", headers=hdrs)
    if br.status_code not in (201, 202):
        print(f"Pages build request returned {br.status_code}: {br.text}")
    else:
        print("Pages build requested")


def update_readme(repo, task: str, brief: str, repo_url: str, pages_url: str):
    readme_content = generate_readme_content(task, brief, repo_url, pages_url)

    try:
        readme_file = repo.get_contents("README.md")
        repo.update_file(
            path="README.md",
            message="Update README",
            content=readme_content,
            sha=readme_file.sha,
        )
    except GithubException:
        repo.create_file(path="README.md", message="Add README", content=readme_content)


def test_github_manager():
    print("Testing GitHub Manager...")
    try:
        github_client = get_github_client()
        user = github_client.get_user()
        print(f"Authenticated as {user.login}")
    except Exception as e:
        print(f"Failed to authenticate with GitHub: {str(e)}")
        return

    task = "test-task"
    round_num = 1
    code_files = {"index.html": "<html><body><h1>Test App</h1></body></html>"}

    try:
        repo_info = create_or_update_repo(task, code_files, round_num)
        print(f"Repository URL: {repo_info['repo_url']}")
        print(f"Pages URL: {repo_info['pages_url']}")
        print(f"Latest Commit SHA: {repo_info['commit_sha']}")

        update_readme(
            repo_info["repo"],
            task,
            "This is a test brief.",
            repo_info["repo_url"],
            repo_info["pages_url"],
        )
        print("README updated successfully.")
    except Exception as e:
        print(f"Error during repository operations: {str(e)}")
