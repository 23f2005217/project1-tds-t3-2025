from flask import Flask, request, jsonify
from utils import (
    load_config,
    validate_config,
    validate_request,
    generate_app_code,
    create_or_update_repo,
    update_readme,
    notify_evaluation_api,
)

app = Flask(__name__)


@app.route('/api-endpoint', methods=['POST'])
def handle_request():
    data = None
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"status": "error", "message": "No JSON data provided"}), 400
        
        is_valid, message = validate_request(data)
        if not is_valid:
            return jsonify({"status": "error", "message": message}), 400
        
        email = data["email"]
        task = data["task"]
        round_num = data["round"]
        nonce = data["nonce"]
        brief = data["brief"]
        checks = data["checks"]
        evaluation_url = data["evaluation_url"]
        attachments = data.get("attachments", [])
        
        print(f"Processing request for {email}, task: {task}, round: {round_num}")
        
        existing_code = None
        if round_num > 1:
            try:
                from utils.github_manager import get_existing_code
                existing_code = get_existing_code(task)
                print(f"Fetched existing code from Round {round_num - 1}")
            except Exception as e:
                print(f"Warning: Could not fetch existing code: {str(e)}")
        
        print("Generating app code with LLM...")
        code_files = generate_app_code(brief, checks, attachments, existing_code, round_num)
        
        print("Creating/updating GitHub repository...")
        repo_info = create_or_update_repo(task, code_files, round_num)
        
        print("Updating README...")
        update_readme(repo_info["repo"], task, brief, repo_info["repo_url"], repo_info["pages_url"])
        
        commits = repo_info["repo"].get_commits()
        latest_commit_sha = commits[0].sha
        
        eval_data = {
            "email": email,
            "task": task,
            "round": round_num,
            "nonce": nonce,
            "repo_url": repo_info["repo_url"],
            "commit_sha": latest_commit_sha,
            "pages_url": repo_info["pages_url"]
        }
        
        print("Notifying evaluation API...")
        notify_result = notify_evaluation_api(evaluation_url, eval_data)
        
        response_data = {
            "status": "success",
            "repo_url": repo_info["repo_url"],
            "pages_url": repo_info["pages_url"],
            "commit_sha": latest_commit_sha
        }
        
        if not notify_result:
            response_data["warning"] = "Failed to notify evaluation API after retries"
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        import traceback
        traceback.print_exc()
        
        error_response = {
            "status": "error",
            "message": str(e)
        }
        
        if data and all(k in data for k in ["email", "task", "round", "nonce"]):
            error_response.update({
                "email": data["email"],
                "task": data["task"],
                "round": data["round"],
                "nonce": data["nonce"]
            })
        
        return jsonify(error_response), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200


def main():
    validate_config()
    
    config = load_config()
    port = config["port"]
    print(f"Starting LLM Code Deployment API on port {port}")
    print(f"API endpoint: http://localhost:{port}/api-endpoint")
    app.run(host="0.0.0.0", port=port, debug=True)


if __name__ == "__main__":
    main()
