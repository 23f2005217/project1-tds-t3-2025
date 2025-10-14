# LLM Code Deployment System

An automated application deployment system that receives briefs, generates apps using LLMs, deploys them to GitHub Pages, and handles iterative updates.

## Overview

This project implements an automated workflow for building and deploying web applications:

1. **Build Phase**: Receives a brief, generates code using OpenAI, creates a GitHub repository, and deploys to GitHub Pages
2. **Revise Phase**: Accepts update requests, modifies existing code, and redeploys

## Features

- **LLM-Powered Code Generation**: Uses OpenAI GPT-4 to generate complete web applications
- **Automated GitHub Deployment**: Creates repositories, manages code, and enables GitHub Pages
- **Multi-Round Support**: Handles initial build and subsequent revision requests
- **Secret Verification**: Validates requests with a secret key
- **Professional Documentation**: Auto-generates README files and includes MIT License
- **Retry Logic**: Ensures evaluation API notifications with exponential backoff

## Setup Instructions

### 1. Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) package manager
- GitHub account with a Personal Access Token
- OpenAI API key

### 2. Install Dependencies

```bash
# Install packages with uv
uv sync
```

All required packages are already defined in `pyproject.toml`.

### 3. Configure Environment Variables

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` and set:

- `GITHUB_TOKEN`: Your GitHub Personal Access Token
  - Create at: <https://github.com/settings/personal-access-tokens/new>  - Required scopes: `repo`, `workflow`, `admin:repo_hook`
- `GITHUB_USERNAME`: Your GitHub username
- `OPENAI_API_KEY`: Your GEMINI API key
  - Get from: <https://aistudio.google.com/api-keys>
  - Watch how to create one: <https://youtu.be/6BRyynZkvf0>
- `SECRET`: Your secret key for request verification
- `PORT`: (Optional) Server port, defaults to 5000

### 4. GitHub Personal Access Token Setup

1. Go to <https://github.com/settings/tokens/new>
2. Give it a descriptive name (e.g., "LLM Deployment System")
3. Select scopes:
   - `repo` (Full control of private repositories)
   - `workflow` (Update GitHub Action workflows)
   - `admin:repo_hook` (Manage repository webhooks)
4. Click "Generate token" and copy it to your `.env` file

![Access Token](.github/assets/access_token.png)
![Permissions](.github/assets/permissions.png)

### 5. Verify Configuration

Before running the server, verify your configuration:

```bash
uv run check_config.py
```

This will:

- Check if all required environment variables are set
- Validate your GitHub token by authenticating
- Validate your OpenAI API key
- Display masked values for confirmation

If any issues are found, you'll get clear instructions on how to fix them.

## Usage

### Running the Server

```bash
uv run main.py
```

The server will start on `http://localhost:5000` (or the port specified in your `.env`).

### Run with Docker

Build the image and run the container (exposes port 5000 by default):

```bash
# Build
docker build -t llm-deploy:latest .

# Run (maps host 5000 -> container 5000)
docker run --env-file .env -p 5000:5000 llm-deploy:latest
```

Notes:

- The Docker image installs Python 3.13 and uv, copies `.env` early for better caching, and starts the app via `uv run main.py`.
- Override the port by setting `PORT` in your `.env` and mapping it accordingly, e.g. `-p 8080:8080`.

### Hugging Face Spaces Configuration

You can configure your Hugging Face Space by adding a YAML block to the top of your `README.md` file. Here are some of the key parameters:

*   **`title`**: Display title for the Space.
*   **`emoji`**: Space emoji.
*   **`colorFrom`**, **`colorTo`**: Colors for the thumbnail gradient.
*   **`sdk`**: Can be `gradio`, `docker`, or `static`.
*   **`python_version`**: Python version to use (e.g., `3.9`).
*   **`sdk_version`**: Version of the SDK to use (e.g., `gradio` version).
*   **`suggested_hardware`**: Suggested hardware for the Space (e.g., `cpu-basic`, `t4-small`).
*   **`suggested_storage`**: Suggested permanent storage (`small`, `medium`, `large`).
*   **`app_file`**: Path to the main application file.
*   **`app_build_command`**: Command to run to generate static files (e.g., `npm run build`).
*   **`secrets`**: A list of secrets to be passed as environment variables.

For a full list of options, see the [Hugging Face Spaces Configuration Reference](https://huggingface.co/docs/hub/spaces-config-reference).

### API Endpoints

#### POST `/api-endpoint`

Main endpoint for build and revise requests.

**Request Format:**

```json
{
  "email": "student@example.com",
  "secret": "your_secret_key",
  "task": "captcha-solver-xyz",
  "round": 1,
  "nonce": "ab12-cd34",
  "brief": "Create a captcha solver that handles ?url=https://.../image.png",
  "checks": [
    "Repo has MIT license",
    "README.md is professional",
    "Page displays captcha URL passed at ?url=...",
    "Page displays solved captcha text within 15 seconds"
  ],
  "evaluation_url": "https://example.com/notify",
  "attachments": [
    {
      "name": "sample.png",
      "url": "data:image/png;base64,iVBORw..."
    }
  ]
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Successfully processed round 1",
  "repo_url": "https://github.com/username/captcha-solver-xyz-round-1",
  "pages_url": "https://username.github.io/captcha-solver-xyz-round-1/",
  "commit_sha": "abc123def456"
}
```

#### GET `/health`

Health check endpoint.

**Response:**

```json
{
  "status": "healthy"
}
```

### Testing with cURL

```bash
curl http://localhost:5000/api-endpoint \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "secret": "your_secret_key",
    "task": "test-app-001",
    "round": 1,
    "nonce": "test-nonce-123",
    "brief": "Create a simple calculator app",
    "checks": [
      "Has MIT license",
      "README is professional",
      "Calculator works correctly"
    ],
    "evaluation_url": "https://httpbin.org/post"
  }'
```

## Architecture

### Core Components

1. **Request Handler** (`handle_request`):
   - Validates incoming requests
   - Orchestrates the entire build/revise workflow
   - Returns appropriate HTTP responses

2. **Secret Verification** (`verify_secret`):
   - Ensures requests are authenticated
   - Prevents unauthorized access

3. **LLM Code Generator** (`generate_app_code`):
   - Uses OpenAI GPT-4o-mini to generate HTML/CSS/JS applications
   - Includes embedded styles and scripts for single-file deployment
   - Considers brief requirements and evaluation checks

4. **GitHub Repository Manager** (`create_or_update_repo`):
   - Creates new repositories for round 1
   - Updates existing repositories for round 2+
   - Adds MIT LICENSE automatically
   - Enables GitHub Pages on main branch

5. **README Generator** (`generate_readme`):
   - Uses LLM to create professional documentation
   - Includes project description, usage, and technical details

6. **Evaluation Notifier** (`notify_evaluation_api`):
   - Sends repository details to evaluation URL
   - Implements exponential backoff (1, 2, 4, 8 seconds)
   - Retries up to 5 times on failure

### Workflow

```
┌─────────────────┐
│ Incoming POST   │
│    Request      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Validate & Auth │
│  (verify secret)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Generate Code   │
│   with LLM      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Create/Update   │
│  GitHub Repo    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Enable GitHub   │
│     Pages       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Generate README │
│  & Update Repo  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Notify Eval API │
│  (with retries) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Return Success  │
│    Response     │
└─────────────────┘
```

## Round 2 (Revise) Handling

The system automatically handles Round 2 requests:

1. Detects `"round": 2` in the request
2. Finds the existing repository from Round 1
3. Generates updated code based on the new brief
4. Updates files in the repository
5. Regenerates README with new information
6. Notifies evaluation API with updated commit SHA

## Security Considerations

- Secret verification prevents unauthorized access
- No secrets stored in git history
- Environment variables for sensitive data
- `.env` file excluded from git (add to `.gitignore`)

## Error Handling

- Invalid requests return HTTP 400 with error details
- Internal errors return HTTP 500 with error messages
- Evaluation API failures trigger automatic retries
- All errors are logged to console for debugging

## Dependencies

Core libraries:

- `flask`: Web framework for API endpoint
- `openai`: LLM integration for code generation
- `pygithub`: GitHub API client
- `requests`: HTTP client for evaluation API
- `python-dotenv`: Environment variable management

## Limitations & Future Improvements

- Currently generates single-page HTML applications
- GitHub Pages may take 1-2 minutes to deploy
- Rate limits on OpenAI and GitHub APIs
- Could add support for multi-file projects
- Could implement caching for faster regeneration

## License

MIT License - see LICENSE file for details

## Troubleshooting

### GitHub Token Issues

- Ensure all required scopes are enabled
- Token must have `repo` access for public repositories
- Verify token hasn't expired

### OpenAI API Issues

- Check API key is valid and has credits
- Verify internet connectivity
- Review rate limits on your OpenAI account

### GitHub Pages Not Deploying

- Wait 1-2 minutes after creation
- Check repository settings → Pages section
- Ensure repository is public
- Verify `index.html` exists in main branch

### Port Already in Use

- Change `PORT` in `.env` file
- Or kill the process using: `lsof -ti:5000 | xargs kill -9`

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review error messages in console output
3. Verify all environment variables are set correctly
4. Ensure GitHub and OpenAI credentials are valid
