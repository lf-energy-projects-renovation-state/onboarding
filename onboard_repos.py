import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Repo:
    owner_and_name: str
    custom_workflows: Optional[list[str]]


# Constants
REPOS_TO_FORK = [
    Repo(owner_and_name="sogno-platform/cimgen", custom_workflows=[]),
    Repo(owner_and_name="sogno-platform/dpsim", custom_workflows=[]),
    Repo(owner_and_name="PowerGridModel/power-grid-model-io", custom_workflows=[]),
    Repo(owner_and_name="PowerGridModel/power-grid-model", custom_workflows=[]),
    Repo(owner_and_name="com-pas/compas-open-scd", custom_workflows=[]),
    Repo(owner_and_name="com-pas/compas-scl-auto-alignment", custom_workflows=["maven-dependency-submission.yml"]),
    Repo(owner_and_name="com-pas/compas-scl-data-service", custom_workflows=["maven-dependency-submission.yml"]),
    Repo(owner_and_name="com-pas/compas-core", custom_workflows=["maven-dependency-submission.yml"]),
    Repo(owner_and_name="com-pas/compas-sct", custom_workflows=["maven-dependency-submission.yml"]),
    Repo(owner_and_name="EVerest/everest-admin-panel", custom_workflows=[]),
    Repo(owner_and_name="EVerest/EVerest", custom_workflows=[]),
    Repo(owner_and_name="EVerest/everest-core", custom_workflows=[]),
    Repo(owner_and_name="EVerest/libocpp", custom_workflows=[]),
    Repo(owner_and_name="openeemeter/eemeter", custom_workflows=[]),
    Repo(owner_and_name="seapath/meta-seapath", custom_workflows=[])
]

TARGET_ORG = "lf-energy-projects-renovation-state"
"""
Name of the GitHub organization into which to fork the repositories.
"""

CONFIGURATION_BRANCH_NAME = "renovate-and-workflow-files"

local_fork_dir = Path.cwd() / "local-forks"


def check_repo_name_conflict():
    repo_names = set()
    for repo_to_fork in REPOS_TO_FORK:
        _, repo_name = repo_to_fork.owner_and_name.split('/')
        if repo_name in repo_names:
            raise ValueError(f"Duplicate repo name: '{repo_name}'. Ensure that all repository names are unique.")
        repo_names.add(repo_name)


def fork_repo_and_clone_it_locally(owner: str, repo: str):
    subprocess.check_call(
        [
            "gh", "repo", "fork", f"{owner}/{repo}",
            "--org", TARGET_ORG,
            "--clone", "--default-branch-only"
        ],
        cwd=local_fork_dir)
    print(f"Forked {owner}/{repo} successfully")


def get_default_branch_name(repo: str) -> str:
    return subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"],
                                   cwd=local_fork_dir / repo).decode("utf-8").strip()


def create_and_push_orphaned_configuration_branch(repo: str, custom_workflows: list[str]):
    repo_dir = local_fork_dir / repo
    subprocess.check_call(["git", "checkout", "--orphan", CONFIGURATION_BRANCH_NAME], cwd=repo_dir)
    subprocess.check_call(["git", "rm", "-rf", "."], cwd=repo_dir)

    templates_dir = Path.cwd() / "templates"
    shutil.copyfile(src=templates_dir / "renovate.json5", dst=repo_dir / "renovate.json5")
    shutil.copyfile(src=templates_dir / "upstream_commit_hash", dst=repo_dir / "upstream_commit_hash")
    workflows_dir = repo_dir / ".github" / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)

    workflows_to_copy = ["sync-fork.yml"]
    workflows_to_copy.extend(custom_workflows)
    for workflow_filename in workflows_to_copy:
        shutil.copyfile(src=templates_dir / ".github" / "workflows" / workflow_filename,
                        dst=workflows_dir / workflow_filename)

    subprocess.check_call(["git", "add", "."], cwd=repo_dir)
    subprocess.check_call(["git", "commit", "-m", "Initial commit"], cwd=repo_dir)
    subprocess.check_call(["git", "push", "-u", "origin", CONFIGURATION_BRANCH_NAME], cwd=repo_dir)


def set_up_and_trigger_sync_workflow(repo: str, default_branch_name: str):
    repo_dir = local_fork_dir / repo
    subprocess.check_call(["git", "checkout", default_branch_name], cwd=repo_dir)
    destination_dir = repo_dir / ".github" / "workflows"
    destination_dir.mkdir(parents=True, exist_ok=True)
    filename = "sync-fork.yml"
    templates_dir = Path.cwd() / "templates"
    shutil.copyfile(src=templates_dir / ".github" / "workflows" / filename, dst=destination_dir / filename)

    # Note: we add "--force" because some projects (e.g. eemeter) have a .gitignore file that is not tuned correctly,
    # blocking the addition of the .github directory
    # Error message (without --force): "The following paths are ignored by one of your .gitignore files: .github"
    subprocess.check_call(["git", "add", "--force", ".github"], cwd=repo_dir)
    subprocess.check_call(["git", "commit", "-m", "Add sync workflow"], cwd=repo_dir)
    subprocess.check_call(["git", "push"], cwd=repo_dir)
    print(f"Pushed sync workflow for {repo}")
    subprocess.check_call(["gh", "repo", "set-default", f"{TARGET_ORG}/{repo}"], cwd=repo_dir)
    subprocess.check_call(["gh", "workflow", "run", "sync-fork.yml"], cwd=repo_dir)
    print(f"Triggered sync workflow for {repo}")


def enable_github_issues(repo: str):
    subprocess.check_call(["gh", "repo", "edit", f"{TARGET_ORG}/{repo}", "--enable-issues"])


def cleanup_local_repo_clone(repo: str):
    repo_dir = local_fork_dir / repo
    if repo_dir.is_dir():
        repo_dir_path = str(repo_dir)
        if sys.platform == "win32":
            subprocess.check_call(['rmdir', "/S", "/Q", repo_dir_path], shell=True)
        else:
            subprocess.check_call(['rm', "-rf", repo_dir_path])


if __name__ == '__main__':
    check_repo_name_conflict()
    for repo_to_fork in REPOS_TO_FORK:
        owner, repo_name = repo_to_fork.owner_and_name.split('/')
        cleanup_local_repo_clone(repo_name)
        fork_repo_and_clone_it_locally(owner, repo_name)
        default_branch_name = get_default_branch_name(repo_name)
        create_and_push_orphaned_configuration_branch(repo_name, repo_to_fork.custom_workflows)
        set_up_and_trigger_sync_workflow(repo_name, default_branch_name)
        enable_github_issues(repo_name)

    input("Please confirm once all the sync-fork workflows have completed")

    for repo_to_fork in REPOS_TO_FORK:
        if repo_to_fork.custom_workflows:
            owner, repo_name = repo_to_fork.owner_and_name.split('/')
            for custom_workflow in repo_to_fork.custom_workflows:
                subprocess.check_call(["gh", "workflow", "run", custom_workflow], cwd=local_fork_dir / repo_name)
                print(f"Triggered custom workflow {custom_workflow} for {repo_name}")
