# Onboarding automation code

This repo contains a [Python script](./onboard_repos.py) that forks a (possibly large) number of GitHub repositories into a dedicated GitHub organization. For these forks, the script sets up separate (orphaned) configuration branch and a synchronization workflow that runs daily and ensures that your fork is kept up-to-date with upstream, while adding the following files (see the `templates` folder):

- Renovate Bot configuration file (`renovate.json5`) (existing `renovate.json*` files of the upstream repository are deleted)
- Synchronization workflow (so that the sync workflow can restore itself to the default branch after resetting the fork's default branch to the upstream's default branch)
- Zero or more additional (optional) workflows, e.g. `trivy-dependencies-submission.yml`

## Usage

1. Create a (free) GitHub organization, and store its name in `TARGET_ORG` in the `onboard_repos.py` script
2. In the settings page of your GitHub organization
   * in the **Actions -> General** section, in the **Workflow permissions** subsection, change the permission to _Read and write permissions_ and click **Save** (we do this so that sync workflow can use the `secrets.GITHUB_TOKEN` to push changes to the fork)
   * in the **Code security -> Configurations** section, create a new configuration which enables the **dependency graph** and **dependabot (alerts)**. In the **Policy** section, set _Use as default for newly created repositories_ to any value other than _None_ (we do this so that the forks have the dependency graph enabled right after creating them, which would otherwise have to be done manually)
3. Configure the repositories you want to fork in the `REPOS_TO_FORK` list in the `onboard_repos.py` script
4. Make sure that the GitHub CLI is installed and authenticated
5. Run the `onboard_repos.py` script with a Python 3.10+ interpreter
6. Open https://github.com/apps/renovate and install the Renovate bot to the organization you created in step 1
   * **Either** you configure the Renovate app to scan _all_ repos. If you do so, go to the Mend Renovate app settings (https://developer.mend.io/github/YOUR_GITHUB_ORG/-/settings): in the **Renovate** section, ensure that _Enabled_ is activated, and the _Mode_ is set to _Interactive_. You can set the _Repository onboarding_ to _Scan repos with config file_.
   * **Or** you explicitly specify the list of all the repos in your organization (in this case no further configuration is needed in the Mend app)
