# Onboarding automation code

This repo contains a [Python script](./onboard_repos.py) that forks a (possibly large) number of GitHub repositories into a dedicated GitHub organization. For these forks, the script sets up separate (orphaned) configuration branch and a synchronization workflow that runs daily and ensures that your fork is kept up-to-date with upstream, while adding the following files (see the `templates` folder):

- Renovate Bot configuration file (`renovate.json5`) (existing `renovate.json*` files of the upstream repository are deleted)
- Synchronization workflow (so that the sync workflow can restore itself to the default branch after resetting the fork's default branch to the upstream's default branch)
- Zero or more additional (optional) workflows, e.g. `trivy-dependencies-submission.yml`

## Usage

1. If you are on Windows, run `git config --system core.longpaths true` once to avoid path length issues
2. Create a (free) GitHub organization, and store its name in `TARGET_ORG` in the `onboard_repos.py` script
3. In the settings page of your GitHub organization
   * in the **Secrets and variables -> Actions** section, create a new organization secret named `GH_PAT` and set it to the value of a (classic) PAT that has the `repo` and `workflow` scopes (we do this so that the sync workflow can push changes to the fork)
   * in the **Code security -> Configurations** section, create a new configuration which enables the **dependency graph** and **dependabot (alerts)**. In the **Policy** section, set _Use as default for newly created repositories_ to any value other than _None_ (we do this so that the forks have the dependency graph enabled right after creating them, which would otherwise have to be done manually)
4. Configure the repositories you want to fork in the `REPOS_TO_FORK` list in the `onboard_repos.py` script
5. Make sure that the GitHub CLI is installed and authenticated
6. Run the `onboard_repos.py` script with a Python 3.10+ interpreter
7. Open https://github.com/apps/renovate and install the Renovate bot to the organization you created in step 1. Make sure that you explicitly specify the list of all the repos in your organization. Granting Renovate access to _all_ repositories won't work.

## Other scripts
- To update / push some of the files in the `templates` folder that you changed locally _after_ you ran the `onboard_repos.py` script, run the `change_files_in_repos.py` script
- To determine which of the repositories in the `REPOS_TO_FORK` list have the Renovate bot or Dependabot installed, run the `check_renovate_or_dependabot.py` script
- To determine the _current_ state of Dependabot alerts vs. Renovate PRs, run the `compare_vulnerabilities.py` script
