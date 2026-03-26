"""
github_skill.py — AgentOS GitHub Integration
Provides tools for PR review, issue tracking, and repository management.
"""
import logging
import os
from typing import Dict, Any, List
from AgentOS.kernel.registry import registry
from AgentOS.core.models import TaskContext
from AgentOS.kernel import inference_node
from AgentOS.core import config
import httpx

logger = logging.getLogger("agentos.github")

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
        pr_data = await self._request("GET", f"/repos/{repo}/pulls/{pr_number}")
        diff_url = pr_data.get("diff_url")
        
        # In a real scenario, we'd fetch the diff and feed it to inference_node
        summary = await inference_node.process({
            "task_id": f"GH-REVIEW-{pr_number}",
            "payload": {
                "action": "summarize_pr",
                "repo": repo,
                "pr_number": pr_number,
                "title": pr_data.get("title")
            }
        })
        
        return {"status": "reviewed", "summary": summary}

    async def list_issues(self, repo: str) -> List[Dict[str, Any]]:
        """List open issues for a repository."""
        return await self._request("GET", f"/repos/{repo}/issues")

github_skill = GitHubSkill()

@registry.register("github_sync")
async def handle_github(task: TaskContext) -> dict:
    """Entry point for GitHub integration tasks."""
    action = task.payload.get("sub_action", "list_prs")
    repo = task.payload.get("repo")
    
    if not repo:
        return {"error": "Repository ('repo') must be specified (e.g., 'owner/repo')"}

    if action == "list_prs":
        data = await github_skill.list_prs(repo)
        return {"status": "success", "prs": data}
    elif action == "review_pr":
        pr_number = task.payload.get("pr_number")
        if not pr_number:
            return {"error": "PR number required"}
        return await github_skill.review_pr(repo, pr_number)
    elif action == "list_issues":
        data = await github_skill.list_issues(repo)
        return {"status": "success", "issues": data}
    
    return {"error": f"Unknown GitHub action: {action}"}
