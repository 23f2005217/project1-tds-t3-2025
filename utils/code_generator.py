from typing import Dict, Optional
import base64

from .config import get_openai_client


def generate_app_code(
    brief: str,
    checks: list,
    attachments: Optional[list] = None,
    existing_code: Optional[str] = None,
    round_num: int = 1,
) -> Dict[str, str]:
    client = get_openai_client()

    attachments_info = ""
    if attachments:
        attachments_info = "\n\nAttachments (data URIs to embed):\n"
        for att in attachments:
            if isinstance(att, str):
                attachments_info += f"- {att[:100]}...\n"
                continue
            
            if not isinstance(att, dict):
                continue
            
            name = att.get("name", att.get("filename", "unknown"))
            url = att.get("url", att.get("data", att.get("content", "")))
            
            if not url and "path" in att:
                try:
                    with open(att["path"], 'r', encoding='utf-8', errors='ignore') as f:
                        url = f.read()
                except Exception:
                    pass
            
            if url:
                attachments_info += f"- {name}: {url[:100]}...\n"
            else:
                attachments_info += f"- {name}: [no content]\n"
                continue
            
            if name.lower().endswith(('.txt', '.csv', '.tsv', '.log', '.md', '.json', '.xml', '.yaml', '.yml', '.ini', '.conf')):
                try:
                    decoded_data = None
                    
                    if isinstance(url, bytes):
                        decoded_data = url
                    elif url.startswith('data:'):
                        parts = url.split(',', 1)
                        if len(parts) == 2:
                            if 'base64' in parts[0]:
                                decoded_data = base64.b64decode(parts[1])
                            else:
                                decoded_data = parts[1].encode('utf-8')
                    elif url.startswith(('http://', 'https://')):
                        attachments_info += "  [Remote file - preview not available]\n"
                        continue
                    else:
                        decoded_data = url.encode('utf-8')
                    
                    if decoded_data:
                        text_content = decoded_data.decode('utf-8', errors='ignore')
                        lines = text_content.splitlines()
                        first_5_lines = lines[:5]
                        
                        if first_5_lines:
                            attachments_info += f"\n  First 5 lines of {name}:\n"
                            for i, line in enumerate(first_5_lines, 1):
                                line_preview = line[:200] if len(line) > 200 else line
                                attachments_info += f"  {i}. {line_preview}\n"
                        else:
                            attachments_info += "\n  [Empty file]\n"
                except Exception:
                    attachments_info += f"\n  Could not read preview of {name}\n"
            
            elif name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg', '.ico', '.tiff', '.tif')):
                try:
                    image_info = f"\n  Image file: {name}\n"
                    
                    if url.startswith('data:image/'):
                        mime_type = url.split(';')[0].replace('data:', '')
                        image_info += f"  Type: {mime_type}\n"
                        image_info += "  Format: Data URI (embedded, ready to use in <img> tag)\n"
                        
                        if 'base64' in url:
                            try:
                                base64_data = url.split(',', 1)[1]
                                decoded_size = len(base64.b64decode(base64_data))
                                image_info += f"  Size: ~{decoded_size / 1024:.1f} KB\n"
                            except Exception:
                                pass
                        
                        image_info += f"  Usage: <img src=\"{{{{ data URI }}}}\" alt=\"{name}\">\n"
                        image_info += "  Note: Full data URI is included in attachment - use it directly in HTML\n"
                    
                    elif url.startswith(('http://', 'https://')):
                        image_info += "  Type: Remote URL\n"
                        image_info += f"  URL: {url[:100]}{'...' if len(url) > 100 else ''}\n"
                        image_info += f"  Usage: <img src=\"{url}\" alt=\"{name}\">\n"
                    
                    elif isinstance(url, bytes) or (isinstance(url, str) and len(url) > 1000):
                        image_info += "  Type: Binary/Base64 data\n"
                        image_info += "  Note: Convert to data URI for use in HTML\n"
                    
                    else:
                        image_info += "  Type: File path or reference\n"
                        image_info += f"  Path: {url}\n"
                    
                    attachments_info += image_info
                except Exception:
                    attachments_info += f"\n  Image file detected but could not extract details: {name}\n"
            
            elif name.lower().endswith(('.mp4', '.webm', '.ogg', '.mov', '.avi')):
                attachments_info += f"\n  Video file: {name}\n"
                if url.startswith('data:video/'):
                    attachments_info += "  Format: Data URI (use in <video> tag)\n"
                elif url.startswith(('http://', 'https://')):
                    attachments_info += "  Format: Remote URL\n"
                attachments_info += "  Usage: <video src=\"{{ URL }}\" controls></video>\n"
            
            elif name.lower().endswith(('.mp3', '.wav', '.ogg', '.m4a', '.flac')):
                attachments_info += f"\n  Audio file: {name}\n"
                if url.startswith('data:audio/'):
                    attachments_info += "  Format: Data URI (use in <audio> tag)\n"
                elif url.startswith(('http://', 'https://')):
                    attachments_info += "  Format: Remote URL\n"
                attachments_info += "  Usage: <audio src=\"{{ URL }}\" controls></audio>\n"
            
            elif name.lower().endswith(('.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx')):
                attachments_info += f"\n  Document file: {name}\n"
                if url.startswith(('http://', 'https://')):
                    attachments_info += "  Format: Remote URL\n"
                    attachments_info += f"  Usage: <a href=\"{url}\" download>Download {name}</a>\n"
                elif url.startswith('data:'):
                    attachments_info += "  Format: Data URI (use in download link)\n"
                    attachments_info += f"  Usage: <a href=\"{{{{ data URI }}}}\" download=\"{name}\">Download</a>\n"

    existing_context = ""
    if existing_code and round_num > 1:
        existing_context = f"""\n\nEXISTING CODE FROM ROUND {round_num - 1}:\n```html\n{existing_code}\n```\n\nIMPORTANT: Modify and enhance the existing code above according to the new brief below. Preserve all working functionality from previous rounds unless the brief explicitly asks to change it.\n"""

    prompt = f"""Generate a complete, minimal single-page web application based on this brief:{existing_context}

Brief: {brief}

Evaluation Checks (must all pass):
{chr(10).join(["- " + check for check in checks])}
{attachments_info}

Critical Requirements:
1. Create a single HTML file with embedded CSS and JavaScript
2. The app must satisfy ALL evaluation checks listed above
3. If attachments are provided as data URIs, embed them directly in the HTML
4. Handle URL parameters (e.g., ?url=, ?token=) as specified in the brief
5. Use CDN links for external libraries (Bootstrap, marked, highlight.js, etc.)
6. Include proper error handling and user feedback
7. Make it visually clean and professional
8. Ensure all required element IDs match the checks exactly
9. The HTML should be complete, valid, and ready to deploy to GitHub Pages
10. Test that all JavaScript functionality works correctly

Return ONLY the complete HTML code with no explanations, no comments, no markdown formatting."""

    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[
            {
                "role": "system",
                "content": "You are an expert web developer. Generate clean, functional, production-ready HTML applications that pass all specified checks.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
    )

    html_content = response.choices[0].message.content

    if html_content is None:
        print("No HTML content generated.")
        return {"index.html": ""}

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
            {
                "role": "system",
                "content": "You are an expert at writing professional technical documentation.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
    )

    readme_content = response.choices[0].message.content

    if readme_content is None:
        print("No README content generated.")
        return ""

    if "```markdown" in readme_content:
        readme_content = readme_content.split("```markdown")[1].split("```")[0].strip()
    elif "```" in readme_content:
        readme_content = readme_content.split("```")[1].split("```")[0].strip()

    return readme_content
