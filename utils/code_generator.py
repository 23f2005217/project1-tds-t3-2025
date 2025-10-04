from typing import Dict

from .config import get_openai_client


def generate_app_code(brief: str, checks: list, attachments: list = None) -> Dict[str, str]:
    client = get_openai_client()
    
    attachments_info = ""
    if attachments:
        attachments_info = "\n\nAttachments:\n"
        for att in attachments:
            attachments_info += f"- {att.get('name', 'unknown')}\n"
    
    prompt = f"""Generate a complete, minimal single-page web application based on this brief:

Brief: {brief}

Evaluation Checks:
{chr(10).join(['- ' + check for check in checks])}
{attachments_info}

Requirements:
1. Create a single HTML file with embedded CSS and JavaScript
2. The app should be fully functional and deployable to GitHub Pages
3. Include error handling and user feedback
4. Make it visually clean and professional
5. Handle URL parameters as specified in the brief
6. The HTML should be complete and ready to deploy

Return ONLY the HTML code, no explanations."""

    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[
            {"role": "system", "content": "You are an expert web developer. Generate clean, functional, production-ready HTML applications."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    
    html_content = response.choices[0].message.content
    
    if "```html" in html_content:
        html_content = html_content.split("```html")[1].split("```")[0].strip()
    elif "```" in html_content:
        html_content = html_content.split("```")[1].split("```")[0].strip()
    
    return {"index.html": html_content}


def generate_readme(task: str, brief: str, repo_url: str, pages_url: str) -> str:
    client = get_openai_client()
    
    prompt = f"""Generate a professional README.md for this project:

Task: {task}
Brief: {brief}
Repository: {repo_url}
Live Demo: {pages_url}

The README should include:
1. Project title and brief description
2. Features/functionality overview
3. Setup instructions (if any)
4. Usage instructions
5. Technical implementation details
6. License information (MIT)

Make it clear, professional, and well-structured with proper markdown formatting."""

    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[
            {"role": "system", "content": "You are an expert at writing professional technical documentation."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    
    readme_content = response.choices[0].message.content
    
    if "```markdown" in readme_content:
        readme_content = readme_content.split("```markdown")[1].split("```")[0].strip()
    elif "```" in readme_content:
        readme_content = readme_content.split("```")[1].split("```")[0].strip()
    
    return readme_content
