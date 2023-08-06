# Project Initializer

Everytime you want to start a project you do the basics. go to your projects folder, create a new folder for the project, do your git commands, sync the repo, add a README file and push your initial commit.

That is what this simple project is for, making your life easier, and doing all that automatically for you.

## Setting up:

1. Install the project.
```bash
$ pip install proj-init
```

2. Create environment variables:

    - `GIT_AUTOMATION = Github Personal Access Token`
    - `PROJECTS = Default path where to create the projects` (Optional, if you don't set this variable the default path will be the current directory)

3. Usage:
```
proj_init [-h] [-l] [-p] [-d PATH] <repo_name>

Automate your workflow with proj_init command.

positional arguments:
  <repo_name>           Name of your repo to be created.

options:
  -h, --help            show this help message and exit
  -l, --local           Creates your repo only locally.
  -p, --private         Creates your repo in private mode.
  -d PATH, --directory PATH
                        Path where the repo is going to be created.
```

Happy Coding!
