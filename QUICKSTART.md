# Quick Start Guide

## Initial Setup (One-time)

1. **Set up your environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` and add your credentials:**
   - Get GitHub token from: https://github.com/settings/tokens
   - Get OpenAI API key from: https://platform.openai.com/api-keys
   - Set a secret key that you'll use in requests
   - Add your GitHub username

3. **Sync dependencies:**
   ```bash
   uv sync
   ```

4. **Verify your configuration:**
   ```bash
   uv run check_config.py
   ```
   
   This checks that all environment variables are set correctly and validates your API tokens.

## Running the Server

```bash
uv run main.py
```

The server will start on http://localhost:5000

## Testing the API

### Option 1: Use the Test Script

In a new terminal:
```bash
uv run test_api.py
```

This will guide you through testing the deployment system.

### Option 2: Use cURL

```bash
curl http://localhost:5000/api-endpoint \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "secret": "your_secret_from_env",
    "task": "my-test-app",
    "round": 1,
    "nonce": "unique-nonce-123",
    "brief": "Create a simple todo list app",
    "checks": [
      "Repo has MIT license",
      "README.md is professional",
      "Todo list works"
    ],
    "evaluation_url": "https://httpbin.org/post"
  }'
```

### Option 3: Use Python

```python
import requests

response = requests.post(
    "http://localhost:5000/api-endpoint",
    json={
        "email": "your-email@example.com",
        "secret": "your_secret_from_env",
        "task": "my-test-app",
        "round": 1,
        "nonce": "unique-nonce-123",
        "brief": "Create a simple weather app",
        "checks": [
            "Repo has MIT license",
            "README is professional",
            "Weather display works"
        ],
        "evaluation_url": "https://httpbin.org/post"
    }
)

print(response.json())
```

## What Happens After a Request?

1. **Secret is verified** - Ensures request is authenticated
2. **Code is generated** - LLM creates a complete web app based on the brief
3. **GitHub repo is created** - New public repository with:
   - Generated code (`index.html`)
   - MIT License
   - Professional README
4. **GitHub Pages is enabled** - App becomes accessible at `https://username.github.io/repo-name/`
5. **Evaluation API is notified** - System sends repo details to the evaluation URL

## Expected Timeline

- **Request processing**: 30-60 seconds
- **GitHub Pages deployment**: 1-2 minutes after repo creation
- **Total time to live app**: 2-3 minutes

## Checking Your Results

After a successful request, you'll receive:

```json
{
  "status": "success",
  "message": "Successfully processed round 1",
  "repo_url": "https://github.com/username/task-name-round-1",
  "pages_url": "https://username.github.io/task-name-round-1/",
  "commit_sha": "abc123..."
}
```

Visit:
- **Repository**: The `repo_url` to see the code
- **Live App**: The `pages_url` to see the deployed app (wait 1-2 minutes)

## Round 2 (Revisions)

To update an app, send another request with `"round": 2`:

```bash
curl http://localhost:5000/api-endpoint \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "secret": "your_secret_from_env",
    "task": "my-test-app",
    "round": 2,
    "nonce": "unique-nonce-456",
    "brief": "Add dark mode toggle to the app",
    "checks": [
      "Dark mode works",
      "Toggle is accessible"
    ],
    "evaluation_url": "https://httpbin.org/post"
  }'
```

The system will:
- Find the existing repository
- Update the code based on the new brief
- Update the README
- Push changes and redeploy

## Troubleshooting

### Server won't start
- Check that port 5000 is available
- Verify all environment variables are set in `.env`
- Ensure dependencies are installed: `uv sync`

### Invalid secret error
- Make sure the `secret` in your request matches the `SECRET` in `.env`

### GitHub errors
- Verify your GitHub token has correct permissions
- Check token hasn't expired
- Ensure you have repo creation permissions

### OpenAI errors
- Verify API key is valid
- Check you have available credits
- Ensure API key has correct permissions

## Notes

- Each request creates a new repository named `{task}-round-{round_num}`
- Repositories are public by default
- GitHub Pages may take 1-2 minutes to build and deploy
- The system uses GPT-4o-mini for code generation
- All secrets stay in `.env` and are never committed to git

## Need Help?

Check the full README.md for detailed documentation and troubleshooting guides.
