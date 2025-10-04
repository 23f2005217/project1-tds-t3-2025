from flask import Flask, request, jsonify
from utils import (
    load_config,
    validate_config,
    validate_request,
    generate_app_code,
    create_or_update_repo,
    update_readme,
    notify_evaluation_api
)

app = Flask(__name__)


@app.route('/api-endpoint', methods=['POST'])
def handle_request():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        is_valid, message = validate_request(data)
        if not is_valid:
            return jsonify({"error": message}), 400
        
        email = data["email"]
        task = data["task"]
        round_num = data["round"]
        nonce = data["nonce"]
        brief = data["brief"]
        checks = data["checks"]
        evaluation_url = data["evaluation_url"]
        attachments = data.get("attachments", [])
        
        print(f"Processing request for {email}, task: {task}, round: {round_num}")
        
        print("Generating app code with LLM...")
        code_files = generate_app_code(brief, checks, attachments)
        
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
        notify_evaluation_api(evaluation_url, eval_data)
        
        return jsonify({
            "status": "success",
            "message": f"Successfully processed round {round_num}",
            "repo_url": repo_info["repo_url"],
            "pages_url": repo_info["pages_url"],
            "commit_sha": latest_commit_sha
        }), 200
        
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


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
