"""
github_skill.py — AgenticBusinessEmpire GitHub Integration
Provides tools for PR review, issue tracking, and repository management.
"""
import logging
import os
from typing import Dict, Any, List
from AgenticBusinessEmpire.kernel.registry import registry
from AgenticBusinessEmpire.core.models import TaskContext
from AgenticBusinessEmpire.kernel import inference_node
from AgenticBusinessEmpire.core import config
import httpx

logger = logging.getLogger("agenticbusinessempire.github")

class GitHubSkill:
    def __init__(self):
        self.token = config.get_secret("GITHUB_TOKEN")
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        } if self.token else {}

    async def _request(self, method: str, path: str, **kwargs):
        if not self.token:
            return {"error": "GITHUB_TOKEN not configured"}
        
        async with httpx.AsyncClient() as client:
            resp = await client.request(method, f"{self.base_url}{path}", headers=self.headers, **kwargs)
            resp.raise_for_status()
            return resp.json()

    async def list_prs(self, repo: str) -> List[Dict[str, Any]]:
        """List open pull requests for a repository."""
        return await self._request("GET", f"/repos/{repo}/pulls")

    async def review_pr(self, repo: str, pr_number: int) -> Dict[str, Any]:
        """Review a PR by summarizing changes using AI logic."""
        # 1. Fetch PR metadata
        pr_data = await self._request("GET", f"/repos/{repo}/pulls/{pr_number}")
        
        # 2. Fetch the actual diff
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/repos/{repo}/pulls/{pr_number}",
                headers={**self.headers, "Accept": "application/vnd.github.v3.diff"},
                timeout=30.0
            )
            resp.raise_for_status()
            diff_content = resp.text
            
        # 3. Feed the diff to inference_node for real review
        # We truncate diff if it's too large for the context
        max_diff_len = 15000 
        truncated_diff = diff_content[:max_diff_len] + ("\n... [TRUNCATED]" if len(diff_content) > max_diff_len else "")
        
        review_result = await inference_node.process({
            "task_id": f"GH-REVIEW-{repo.replace('/', '_')}-{pr_number}",
            "tenant": "tenant_zero",
            "payload": {
                "action": "github_summarize_pr",
                "repo": repo,
                "pr_number": pr_number,
                "title": pr_data.get("title"),
                "diff": truncated_diff,
                "role": "engineer" 
            }
        })
        
        return {"status": "reviewed", "repo": repo, "pr": pr_number, "analysis": review_result}

    async def create_issue(self, repo: str, title: str, body: str) -> Dict[str, Any]:
        """Create a new issue on GitHub."""
        return await self._request("POST", f"/repos/{repo}/issues", json={"title": title, "body": body})

    async def create_pr(self, repo: str, title: str, head: str, base: str, body: str) -> Dict[str, Any]:
        """Create a new Pull Request."""
        return await self._request("POST", f"/repos/{repo}/pulls", json={"title": title, "head": head, "base": base, "body": body})

    async def merge_pr(self, repo: str, pr_number: int) -> Dict[str, Any]:
        """Merge an existing Pull Request."""
        return await self._request("PUT", f"/repos/{repo}/pulls/{pr_number}/merge")

    async def add_comment(self, repo: str, issue_number: int, body: str) -> Dict[str, Any]:
        """Add a comment to an issue or pull request."""
        return await self._request("POST", f"/repos/{repo}/issues/{issue_number}/comments", json={"body": body})

github_skill = GitHubSkill()

@registry.register("github_sync")
async def handle_github(task: TaskContext) -> dict:
    """Entry point for GitHub/Ecosystem integration tasks."""
    # ROBUSTNESS: Prefer server for GitHub heavy lifting
    if not config.IS_SERVER and not task.payload.get("_delegated"):
        from AgenticBusinessEmpire.sync_engine.balancer import balancer
        if balancer.should_offload(threshold=0.0): # Always offload GH tasks if not on server
             return {"status": "delegated", "reason": "server_preferred_for_github"}

    action = task.payload.get("sub_action", "list_prs")
    repo = task.payload.get("repo")
    
    if action == "list_prs":
        if not repo: return {"error": "repo required"}
        data = await github_skill.list_prs(repo)
        return {"status": "success", "prs": data}
    elif action == "review_pr":
        pr_number = task.payload.get("pr_number")
        if not repo or not pr_number: return {"error": "repo and pr_number required"}
        return await github_skill.review_pr(repo, pr_number)
    elif action == "create_issue":
        title = task.payload.get("title")
        body = task.payload.get("body", "")
        if not repo or not title: return {"error": "repo and title required"}
        return await github_skill.create_issue(repo, title, body)
    elif action == "create_pr":
        title = task.payload.get("title")
        head = task.payload.get("head")
        base = task.payload.get("base", "master")
        body = task.payload.get("body", "")
        if not repo or not title or not head: return {"error": "repo, title, and head required"}
        return await github_skill.create_pr(repo, title, head, base, body)
    elif action == "merge_pr":
        pr_number = task.payload.get("pr_number")
        if not repo or not pr_number: return {"error": "repo and pr_number required"}
        return await github_skill.merge_pr(repo, pr_number)
    elif action == "add_comment":
        issue_number = task.payload.get("issue_number")
        body = task.payload.get("body")
        if not repo or not issue_number or not body: return {"error": "repo, issue_number, and body required"}
        return await github_skill.add_comment(repo, issue_number, body)
    elif action == "linear_sync":
        team_id = task.payload.get("team_id", "default")
        return await github_skill.sync_linear_issues(team_id)
    elif action == "notion_sync":
        database_id = task.payload.get("database_id", "default")
        return await github_skill.sync_notion_docs(database_id)
    elif action == "list_issues":
        if not repo: return {"error": "repo required"}
        data = await github_skill.list_issues(repo)
        return {"status": "success", "issues": data}

@registry.register("github_summarize_pr")
async def handle_summarize_pr(task: TaskContext) -> dict:
    """Uses LLM to summarize a GitHub PR diff."""
    diff = task.payload.get("diff", "")
    title = task.payload.get("title", "Untitled PR")
    
    prompt = f"""
Analyze the following GitHub Pull Request and provide a concise technical summary of changes.
Identify any potential bugs, security concerns, or architectural regressions.

PR Title: {title}

### DIFF CONTENT:
{diff}
"""
    # Trigger LLM inference via the task prompt
    task.payload["prompt"] = prompt
    return await inference_node.infer_intent(task)


