## Useful git commands (besides pull, commit, and push)

## removing .git after cloning a repo

When you clone a repo, git automatically creates a `.git` folder inside it. This folder contains the entire history and configuration of the **original** repo you cloned from.

If you want to use the cloned code as a **starting point for your own new project**, you should delete this `.git` folder. Otherwise your project is still connected to the original repo's history, and if you run `git push` you will be pushing to the original repo (or get an error if you don't have access).

```
rm -rf .git   - remove the .git folder completely
```

After this, the folder is just plain code with no git history. You can then start fresh:

```
git init               - initialize a new git repo
git add .
git commit -m "initial commit"
```

And connect it to your own remote repository.

If you just want to use the code locally without any git tracking at all, `rm -rf .git` is enough — you don't need to do anything else.

## branches

```
git checkout -b branch_name - we create a new branch and switch to it

Example: git checkout -b dev

git checkout branch_name - we switch to the branch

Example: git checkout main
```

### What is the point of having other branches except for main?

+ Suppose you have a working code and you want to make an experiment on making you pipeline (for example, machine learning model) better. You can create a new branch and do your experiment there. If it works, you can merge it with the main branch. If it doesn't, you won't mess up your working code, because you are working on a new branch

+ Suppose there are multiple people working on the same project on the same features or models. Each person can work on his/her own branch and then merge it with the main branch. So nobody will affect the work of others

Common branches include:

+ main - the main branch, where the working code is
+ dev - development
+ feature - for new features
+ bugfix - for fixing bugs
+ hotfix - for fixing bugs that are critical and need to be fixed immediately

```
git branch -a - list the branches we have. It will also show what branch we are currently at (marked with a *)
```

## merge and pull requests

Suppose we made some changes on the dev or feature (or other) branch, and the changes to the original code look good to us. So we want to merge them with the main branch

If this needs to be approved by someone, we create a pull request (merge request). Pull requests basically means that we created some useful changes and want to merge them with another branch (usually with the main) branch

Suppose no approval is needed and we want to merge the feature from the feature branch to the main branch. We can do this with the following commands:

```
git checkout main - we switch to the main branch

git merge feature - we merge the feature branch with the main branch
```

## conflicts when merging

Sometimes, when we merge two branches, there are conflicts. This happens when two people changed the same line of code in two different branches. For example, I was working on the main branch, and someone else was working on the feature branch. I changed something in the main.py, and someone else also changed something in the main.py. Then when I merge the feature branch with the main branch, I will get a conflict, and it will look like this:

```
CONFLICT (content): Merge conflict in main.py
Automatic merge failed; fix conflicts and then commit the result.

To fix the conflict, we need to open the file with the conflict (main.py in this case) and manually fix the conflict. We can do this with the following commands:

git diff - show the conflicts

So when the conflict occurs (for example, in the main.py) - we need to open this main.py file and fix the conflict by hand. After that, we can commit the changes and push them

git add main.py - add the file with the resolved conflict
git commit - commit the changes (at this point we do not need to add a message because it is a merge commit)

Then we will get a message like this:

Merge branch 'feature' into main
# Please enter a commit message to explain why this merge is necessary,
# especially if it merges an updated upstream into a topic branch.
#
# Lines starting with '#' will be ignored, and an empty message aborts
# the commit.

We do not need to do anything here except for exiting vim (:wq + enter), and the merge will be completed
```

## remove files from the directory

Sometimes we want to remove some files from the directory. Deleting them from VScode folder is not enough. We need to delete them from git as well. We can do this with the following commands:

```
git rm file_name - remove a file from git AND from the filesystem (disk)

Example: git rm old_script.py

git rm -r folder_name - remove a folder from git AND from the filesystem (disk)

Example: git rm -r old_folder
```

Then we can commit these changes and push them - files will be removed from the remote repository as well

### git rm vs git rm --cached

`git rm <file>` removes the file from **both** git tracking and your disk. It is equivalent to:

```
rm file_name         - delete the file from disk
git add file_name    - stage the deletion
```

`git rm --cached <file>` removes the file from git tracking only — the file **stays on your disk**. Git will no longer track it after the next commit.

When to use each:

+ `git rm file_name` — you want to delete the file entirely
+ `git rm --cached file_name` — you want to stop tracking the file but keep it locally (e.g. you accidentally committed a `.env` file)

Common workflow for untracking a sensitive file:

```
git rm --cached .env
echo ".env" >> .gitignore
git commit -m "stop tracking .env"
```

The `.env` file stays on your machine, but Git no longer tracks it going forward

## undo the last commit (before pushing)

```
git reset --soft HEAD~1  - undo the commit, keep changes staged (ready to re-commit)
git reset HEAD~1         - undo the commit, keep changes in files but unstaged
```

`HEAD~1` means "one commit before the current one". In both cases the files stay in your local filesystem — the changes are not lost. The difference is only whether they are staged or not:

+ `--soft` keeps changes **staged** (as if you just ran `git add`) — useful if you want to re-commit immediately with small fixes
+ no flag keeps changes **unstaged** (as if you just edited the files) — more commonly useful

To undo multiple commits at once, replace `~1` with the number of commits you want to undo:

```
git reset --soft HEAD~3  - undo last 3 commits, keep changes staged
git reset HEAD~3         - undo last 3 commits, keep changes unstaged
```

Your files stay safe either way — only the commits are removed.

Note: only do this before pushing. If the commit is already on the remote, see `git revert` instead.

## discard all local changes (before git add / commit)

Suppose you made some changes but have not run `git add` or `git commit` yet, and you want to throw everything away and get back to the last pushed state.

To discard changes to **tracked files** (files that already exist in git):

```
git checkout -- .   - restore all tracked files to their last committed state
```

This does NOT remove new files you created. To also delete new (untracked) files:

```
git clean -fd       - delete all untracked files and folders
```

+ `-f` means force (required by git as a safety measure)
+ `-d` includes untracked folders, not just files

To do both in one go:

```
git checkout -- .
git clean -fd
```

After this, your working directory will look exactly like the last commit that was pushed. **This cannot be undone** — the changes are permanently lost.

## inspect a commit

After you have already committed, `git diff` and `git status` won't show the changes (the working tree is clean). To see what is inside the last commit:

```
git show --stat      - list of changed files with lines added/removed
git show             - full diff of the last commit
git show --name-only - just the list of changed files
```

`git show` defaults to the latest commit (HEAD). You can also inspect any other commit by passing its hash:

The output is displayed in a pager (less). Navigation keys:

+ `Space` or `f` - next page
+ `b` - previous page
+ arrow keys - line by line
+ `q` - quit

The same navigation applies to other git commands that use the pager, like `git log`.

```
git show abc1234
```

## status

```
git status shows what files have been changed, what files have been added, what files have been deleted, etc. It also shows what branch we are currently at
```

Example: Suppose we

+ created:

+ + new_api.py

+ + notes.txt

+ modified:

+ + app.py

+ + config.json

+ deleted:

+ + old_script.py

Then git status could look like this:

On branch dev
Changes not staged for commit:
  (use "git add/rm <file>..." to update what will be committed)

        modified:   app.py
        modified:   config.json
        deleted:    old_script.py

Untracked files:
  (use "git add <file>..." to include in what will be committed)

        new_api.py
        notes.txt

no changes added to commit

