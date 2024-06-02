import shutil
import subprocess
import sys
from pathlib import Path

# Constants
REPOS_TO_FORK = [
    "sogno-platform/cimgen",
    "sogno-platform/dpsim",
    "PowerGridModel/power-grid-model-io",
    "PowerGridModel/power-grid-model",
    "com-pas/compas-open-scd",
    "com-pas/compas-scl-auto-alignment",
    "com-pas/compas-scl-data-service",
    "com-pas/compas-core",
    "com-pas/compas-sct",
    "EVerest/everest-admin-panel",
    "EVerest/EVerest",
    "EVerest/everest-core",
    "EVerest/libocpp",
    "openeemeter/eemeter",
    "seapath/meta-seapath"
]

TARGET_ORG = "energy-projects-renovation-state"
"""
Name of the GitHub organization into which to fork the repositories.
"""

NEW_DEFAULT_BRANCH_NAME = "sync-and-renovate-settings"

local_fork_dir = Path.cwd() / "local-forks"


def check_repo_name_conflict():
    repo_names = set()
    for repo_to_fork in REPOS_TO_FORK:
        _, repo_name = repo_to_fork.split('/')
        if repo_name in repo_names:
            raise ValueError(f"Duplicate repo name: '{repo_name}'. Ensure that all repository names are unique.")
        repo_names.add(repo_name)


def fork_repo_and_clone_it_locally(owner: str, repo: str):
    subprocess.check_call(
        [
            "git", "clone", f"https://github.com/{owner}/{repo}.git",
        ],
        cwd=local_fork_dir)
    print(f"Forked {owner}/{repo} successfully")


def get_default_branch_name(repo: str) -> str:
    return subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"],
                                   cwd=local_fork_dir / repo).decode("utf-8").strip()


def generate_templated_files(owner: str, repo: str, upstream_default_branch_name: str):
    repo_dir = local_fork_dir / repo

    github_dir = repo_dir / ".github"
    github_dir.mkdir()

    for template_source, target_path in [("README.md", "README.md"), ("renovate.json5", "renovate.json5"),
                                         ("pull.yml", ".github/pull.yml")]:
        templated_content = (Path.cwd() / "templates" / template_source).read_text()
        templated_content = templated_content.replace("###REPO_NAME###", repo)
        templated_content = templated_content.replace("###OWNER###", owner)
        templated_content = templated_content.replace("###UPSTREAM_DEFAULT_BRANCH###", upstream_default_branch_name)

        (repo_dir / target_path).write_text(templated_content)


def create_and_push_orphaned_sync_branch(owner: str, repo: str, upstream_default_branch_name: str):
    repo_dir = local_fork_dir / repo
    subprocess.check_call(["git", "checkout", NEW_DEFAULT_BRANCH_NAME], cwd=repo_dir)
    subprocess.check_call(["git", "rm", "-rf", "."], cwd=repo_dir)
    generate_templated_files(owner, repo, upstream_default_branch_name)
    subprocess.check_call(["git", "add", "."], cwd=repo_dir)
    subprocess.check_call(["git", "commit", "-m", "Update configs"], cwd=repo_dir)
    subprocess.check_call(["git", "push"], cwd=repo_dir)


def change_default_branch(repo: str):
    subprocess.check_call(["gh", "repo", "edit", f"{TARGET_ORG}/{repo}", "--default-branch", NEW_DEFAULT_BRANCH_NAME])


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
        owner, repo_name = repo_to_fork.split('/')
        cleanup_local_repo_clone(repo_name)
        fork_repo_and_clone_it_locally(owner, repo_name)
        default_branch_name = get_default_branch_name(repo_name)

        cleanup_local_repo_clone(repo_name)
        subprocess.check_call(
            [
                "git", "clone", f"https://github.com/{TARGET_ORG}/{repo_name}.git",
            ],
            cwd=local_fork_dir)

        create_and_push_orphaned_sync_branch(owner, repo_name, default_branch_name)
        # change_default_branch(repo_name)
        # enable_github_issues(repo_name)
