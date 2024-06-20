# Onboarding automation code

This repo contains a [Python script](./onboard_repos.py) that forks a (possibly large) number of GitHub repositories into a dedicated GitHub organization. For these forks, the script sets up separate (orphaned) configuration branch and a synchronization workflow that runs daily and ensures that your fork is kept up-to-date with upstream, while adding the following files (see the `templates` folder):

- Renovate Bot configuration file (`renovate.json5`) (existing `renovate.json*` files of the upstream repository are deleted)
- Synchronization workflow (to be able to restore it after synchronizing the upstream's default branch)
- Zero or more additional (optional) workflows, e.g. `maven-dependency-submission.yml`

## Usage

1. Create a (free) GitHub organization, and store its name in `TARGET_ORG` in the `onboard_repos.py` script
2. In the settings page of your GitHub organization
   * in the **Actions -> General** section, in the **Workflow permissions** subsection, change the permission to _Read and write permissions_ and click **Save**
   * in the **Code security -> Configurations** section, create a new configuration which enables the **dependency graph** and **dependabot (alerts)**. In the **Policy** section, set _Use as default for newly created repositories_ to any value other than _None_
3. Configure the repositories you want to fork in the `REPOS_TO_FORK` list in the `onboard_repos.py` script
4. Run the `onboard_repos.py` script with a Python 3.10+ interpreter
6. Open https://github.com/apps/renovate and install the Renovate bot to the organization you created in step 1
