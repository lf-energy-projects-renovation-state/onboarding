# Onboarding automation code

This repo contains a [Python script](./onboard_repos.py) that forks a (possibly large) number of GitHub repositories into a dedicated GitHub organization. For these forks, the script sets up a new default branch and creates files in it:

- configuration for an automated code synchronization mechanism, which ensure that upstream changes are pulled into the forks on a daily basis
- Renovate Bot configuration file

## Usage

1. Create a (free) GitHub organization, and store its name in `TARGET_ORG` in the script
2. Configure the repositories you want to fork in the `REPOS_TO_FORK` list in the script
3. Run the script with a Python 3.10+ interpreter
4. Open https://github.com/apps/renovate and install the Renovate bot to the organization you created in step 1
5. Open https://github.com/apps/pull and install the Pull app to the organization you created in step 1
6. For the code synchronization (using wei/pull) to work, you need to _manually_ either
   * wait (until the upstream has new commits, then wait up to another 24h) for the wei/pull app to create a PR in your fork (that PR would merge the upstream changes into your fork), and approve the workflow (you need to approve it only _once_), or
   * open the settings of the fork repo (the _Actions -> General_ section) and change the **Fork pull request workflows from outside collaborators** setting to _Require approval for first-time contributors who are new to GitHub_ (the Python script cannot do this programmatically yet, see [discussion](https://github.com/orgs/community/discussions/35808))
