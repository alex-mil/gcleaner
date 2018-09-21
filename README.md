# gcleaner
Git remote branches cleaner.

Python scripts for versions 2.X and 3.X to cleanup all branches but `master` and `production` in remote repositories.

### Usage

Open a terminal and run the script with `python gcleaner.py`. You will be asked to enter a path to a folder
you want to be scanned. By default it will be the current folder.
The script will search for a `.git/` directory in all subfolders and try to execute git commands to delete remote branches.

Let's say you have the following structure:
```
projects/
  project_a/
    .git/
    ...
  project_b/
    .git/
    ...
```
You can direct the script to the `projects/` directory and it will handle automatically `project_a/` and `project_b/`.
Or you can simply run it directly in one of the projects and it will only clean it's remote repository.
