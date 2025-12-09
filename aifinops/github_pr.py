from __future__ import annotations
import os
from github import Github
import subprocess
from typing import Optional

def create_pr(repo_full_name: str, branch_name: str, pr_title: str, pr_body: str, push: bool = False) -> Optional[str]:
    """
    Dry-run by default. If GITHUB_TOKEN and push=True, will create branch, commit PR file, push and open PR.
    """
    token = os.getenv("GITHUB_TOKEN")
    remote = os.getenv("GITHUB_REMOTE", "origin")
    if not token or not push:
        # dry-run: print instructions
        print("=== DRY-RUN: PR Body ===")
        print(pr_body)
        print("\nTo create a PR automatically, set GITHUB_TOKEN env var and call with push=True.")
        return None

    g = Github(token)
    repo = g.get_repo(repo_full_name)
    # create branch name must be unique
    master_ref = repo.get_git_ref("heads/main")
    new_ref = repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=master_ref.object.sha)
    # Add a file - pr_body.md
    from base64 import b64encode
    content = pr_body
    repo.create_file(path=f"pr-{branch_name}.md", message=f"chore: add PR body {branch_name}", content=content, branch=branch_name)
    pr = repo.create_pull(title=pr_title, body=pr_body, head=branch_name, base="main")
    print(f"PR created: {pr.html_url}")
    return pr.html_url
