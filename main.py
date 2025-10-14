from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from utils import (
    load_config,
    validate_config,
    validate_request,
    generate_app_code,
    create_or_update_repo,
    update_readme,
    notify_evaluation_api,
)
from pydantic import BaseModel
import uvicorn

app = FastAPI()


class RequestData(BaseModel):
    email: str
    task: str
    round: int
    nonce: str
    brief: str
    checks: list
    evaluation_url: str
    attachments: list = []


@app.post("/api-endpoint")
async def handle_request(request: Request):
    current_step = "initialization"
    data = None

    try:
        data = await request.json()
        if not data:
            raise HTTPException(status_code=400, detail="No JSON data provided")

        current_step = "validation"
        is_valid, message = validate_request(data)
        if not is_valid:
            raise HTTPException(status_code=400, detail=message)

        email = data["email"]
        task = data["task"]
        round_num = data["round"]
        nonce = data["nonce"]
        brief = data["brief"]
        checks = data["checks"]
        evaluation_url = data["evaluation_url"]
        attachments = data.get("attachments", [])

        print(f"Processing request for {email}, task: {task}, round: {round_num}")

        existing_code = ""
        if round_num > 1:
            current_step = "fetching existing code"
            try:
                from utils.github_manager import get_existing_code

                existing_code = get_existing_code(task)
                if existing_code:
                    print(
                        f"Successfully fetched existing code from Round {round_num - 1}"
                    )
                else:
                    print(
                        "No existing code found (this is OK for first-time Round {round_num})"
                    )
            except Exception as e:
                print(f"Warning: Could not fetch existing code: {str(e)}")
                print("Continuing without existing code (generating fresh)...")

        current_step = "generating code"
        print("Generating app code with LLM...")
        try:
            code_files = generate_app_code(
                brief, checks, attachments, existing_code, round_num
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Code generation failed: {str(e)}"
            )

        current_step = "creating/updating repository"
        print("Creating/updating GitHub repository...")
        try:
            repo_info = create_or_update_repo(task, code_files, round_num)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Repository operation failed: {str(e)}"
            )

        current_step = "updating README"
        print("Updating README...")
        try:
            update_readme(
                repo_info["repo"],
                task,
                brief,
                repo_info["repo_url"],
                repo_info["pages_url"],
            )
        except Exception as e:
            print(f"Warning: README update failed: {str(e)}")

        current_step = "fetching commit info"
        try:
            commits = repo_info["repo"].get_commits()
            latest_commit_sha = commits[0].sha
        except Exception as e:
            print(f"Warning: Could not fetch commits: {str(e)}")
            latest_commit_sha = repo_info.get("commit_sha", "unknown")

        eval_data = {
            "email": email,
            "task": task,
            "round": round_num,
            "nonce": nonce,
            "repo_url": repo_info["repo_url"],
            "commit_sha": latest_commit_sha,
            "pages_url": repo_info["pages_url"],
        }

        current_step = "notifying evaluation API"
        print("Notifying evaluation API...")
        notify_result = False
        try:
            notify_result = notify_evaluation_api(evaluation_url, eval_data)
        except Exception as e:
            print(f"Warning: Evaluation API notification failed: {str(e)}")

        response_data = {
            "status": "success",
            "repo_url": repo_info["repo_url"],
            "pages_url": repo_info["pages_url"],
            "commit_sha": latest_commit_sha,
        }

        if not notify_result:
            response_data["warning"] = "Failed to notify evaluation API after retries"

        return JSONResponse(content=response_data, status_code=200)

    except Exception as e:
        print(f"Error processing request at step '{current_step}': {str(e)}")
        import traceback

        traceback.print_exc()

        error_message = str(e)
        if current_step != "initialization":
            error_message = f"Failed at step '{current_step}': {error_message}"

        error_response = {
            "status": "error",
            "message": error_message,
        }

        if data and all(k in data for k in ["email", "task", "round", "nonce"]):
            error_response.update(
                {
                    "email": data["email"],
                    "task": data["task"],
                    "round": data["round"],
                    "nonce": data["nonce"],
                }
            )

        return JSONResponse(content=error_response, status_code=500)


@app.get("/health")
def health():
    return JSONResponse(content={"status": "healthy"}, status_code=200)


def main():
    validate_config()
    config = load_config()
    port = config.get("port", 8000)
    print(f"Starting LLM Code Deployment API on port {port}")
    print(f"API endpoint: http://localhost:{port}/api-endpoint")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)


if __name__ == "__main__":
    main()
