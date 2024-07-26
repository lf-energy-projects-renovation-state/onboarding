"""
Produces a CSV file of the following form:
<owner-and-repo-name>,<dependabot-vulnerabilities>,<renovate-prs-with-vulnerabilities>,<renovate-prs-without-vulnerabilities>

The motivation is to determine how much higher the number of Dependabot alerts is, compared to security-related Renovate PRs
(in our forks).

Make sure to set the environment variable GITHUB_TOKEN to a valid GitHub PAT before running this script.
"""
import os

from github import Github, Auth, PullRequest

from onboard_repos import REPOS_TO_FORK, TARGET_ORG


def get_dependabot_alert_count(github: Github, repo_owner_and_name: str) -> int:
    repo = github.get_repo(repo_owner_and_name)
    alerts = repo.get_dependabot_alerts(state='open')
    return len(list(alerts))


def get_renovate_prs(github: Github, repo_owner_and_name: str) -> list[PullRequest]:
    repo = github.get_repo(repo_owner_and_name)

    renovate_prs = []

    prs = repo.get_pulls(state='open')
    for pr in prs:
        if pr.user.login == "renovate[bot]":
            renovate_prs.append(pr)

    return renovate_prs


def get_renovate_prs_with_vulnerabilities(renovate_prs: list[PullRequest]) -> int:
    prs_with_vulnerabilities = 0
    for pr in renovate_prs:
        labels = [label.name for label in pr.labels]
        if "security" in labels:
            prs_with_vulnerabilities += 1
    return prs_with_vulnerabilities


if __name__ == '__main__':
    github_client = Github(auth=Auth.Token(token=os.getenv("GITHUB_TOKEN")))
    github_client.get_user()  # check the PAT for validity

    with open("vulnerability_comparison.csv", "w") as f:
        f.write("Repo,Dependabot vulnerabilities,Renovate PRs with vulnerabilities,Renovate PRS without vulnerabilities\n")

        for forked_repo in REPOS_TO_FORK:
            _, repo_name = forked_repo.owner_and_name.split('/')
            fork_repo_and_name = f"{TARGET_ORG}/{repo_name}"
            dependabot_alerts = get_dependabot_alert_count(github_client, fork_repo_and_name)
            renovate_prs = get_renovate_prs(github_client, fork_repo_and_name)
            renovate_prs_with_vulnerabilities = get_renovate_prs_with_vulnerabilities(renovate_prs)
            renovate_prs_without_vulnerabilities = len(renovate_prs) - renovate_prs_with_vulnerabilities

            f.write(f"{forked_repo.owner_and_name},{dependabot_alerts},{renovate_prs_with_vulnerabilities},{renovate_prs_without_vulnerabilities}\n")
