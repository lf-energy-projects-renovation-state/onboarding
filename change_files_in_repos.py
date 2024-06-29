"""
Assuming that the onboard_repos.py script was already executed, this script will update the configuration files in the
<CONFIGURATION_BRANCH_NAME> branch and push it. On the next run of the sync-fork.yml workflow, the changes will be
reflected in the forked repository's default branch.
"""
import shutil
import subprocess
from pathlib import Path

from onboard_repos import REPOS_TO_FORK, local_fork_dir, CONFIGURATION_BRANCH_NAME, TARGET_ORG

if __name__ == '__main__':
    for repo_to_fork in REPOS_TO_FORK:
        owner, repo = repo_to_fork.owner_and_name.split('/')

        repo_dir = local_fork_dir / repo
        if not repo_dir.is_dir():
            subprocess.check_call(["git", "clone", f"https://github.com/{TARGET_ORG}/{repo}.git"],
                                  cwd=local_fork_dir)

        default_branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"],
                                                 cwd=repo_dir).decode("utf-8").strip()

        subprocess.check_call(["git", "checkout", CONFIGURATION_BRANCH_NAME], cwd=repo_dir)
        # The sync workflow might have changed files, so we need to update our (possibly stale) local clone
        subprocess.check_call(["git", "pull"], cwd=repo_dir)

        subprocess.check_call(["git", "rm", "-rf", "."], cwd=repo_dir)
        templates_dir = Path.cwd() / "templates"
        shutil.copyfile(src=templates_dir / "renovate.json5", dst=repo_dir / "renovate.json5")
        shutil.copyfile(src=templates_dir / "upstream_commit_hash", dst=repo_dir / "upstream_commit_hash")
        workflows_to_copy = ["sync-fork.yml"]
        workflows_to_copy.extend(repo_to_fork.custom_workflows)
        workflows_dir = repo_dir / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)
        for workflow_filename in workflows_to_copy:
            shutil.copyfile(src=templates_dir / ".github" / "workflows" / workflow_filename,
                            dst=workflows_dir / workflow_filename)

        subprocess.check_call(["git", "add", "."], cwd=repo_dir)
        subprocess.check_call(["git", "commit", "-m", "Update configuration files"], cwd=repo_dir)
        subprocess.check_call(["git", "push", "-u", "origin", CONFIGURATION_BRANCH_NAME], cwd=repo_dir)
        subprocess.check_call(["git", "checkout", default_branch], cwd=repo_dir)
