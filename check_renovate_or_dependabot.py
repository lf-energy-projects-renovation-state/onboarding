"""
This helper script determines whether any of the repos in REPOS_TO_FORK have either Dependabot or Renovate Bot enabled,
by printing one line for each repo where this is the case.

Make sure to set the environment variable GITHUB_TOKEN to a valid GitHub PAT before running this script.
"""
import os

from github import Github, Auth, UnknownObjectException

from onboard_repos import REPOS_TO_FORK




def get_default_branch_name(github: Github, repo_owner_and_name: str) -> str:
    repo = github.get_repo(repo_owner_and_name)
    return repo.default_branch


def has_dependabot_config(github: Github, repo_owner_and_name: str) -> bool:
    repo = github.get_repo(repo_owner_and_name)
    try:
        repo.get_contents('.github/dependabot.yml')
        return True
    except UnknownObjectException:
        return False


def has_renovate_config(github: Github, repo_owner_and_name: str) -> bool:
    repo = github.get_repo(repo_owner_and_name)
    for f in ['renovate.json', 'renovate.json5']:
        try:
            repo.get_contents(f)
            return True
        except UnknownObjectException:
            pass
    return False


if __name__ == '__main__':
    github_client = Github(auth=Auth.Token(token=os.getenv("GITHUB_TOKEN")))
    github_client.get_user()  # check the PAT for validity

    for forked_repo in REPOS_TO_FORK:
        default_branch = get_default_branch_name(github_client, forked_repo.owner_and_name)

        has_dependabot = has_dependabot_config(github_client, forked_repo.owner_and_name)

        has_renovate = has_renovate_config(github_client, forked_repo.owner_and_name)

        state = "none"
        if has_renovate:
            state = "renovate"
        elif has_dependabot:
            state = "dependabot"

        print(f"{forked_repo.owner_and_name}: {state}")
