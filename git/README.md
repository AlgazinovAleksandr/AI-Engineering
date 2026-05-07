### Useful git commands (besides pull, commit, and push)

##### branches

```
git checkout -b branch_name - we create a new branch and switch to it

Example: git checkout -b dev

git checkout branch_name - we switch to the branch

Example: git checkout main
```

**What is the point of having other branches except for main?**

+ Suppose you have a working code and you want to make an experiment on making you pipeline (for example, machine learning model) better. You can create a new branch and do your experiment there. If it works, you can merge it with the main branch. If it doesn't, you won't mess up your working code, because you are working on a new branch

+ Suppose there are multiple people working on the same project on the same features or models. Each person can work on his/her own branch and then merge it with the main branch. So nobody will affect the work of others

Common branches include:

+ main - the main branch, where the working code is
+ dev - development
+ feature - for new features
+ bugfix - for fixing bugs
+ hotfix - for fixing bugs that are critical and need to be fixed immediately

git branch -a - list the branches we have. It will also show what branch we are currently at (marked with a *)

##### merge and pull requests

Suppose we made some changes on the dev or feature (or other) branch, and the changes to the original code look good to us. So we want to merge them with the main branch

If this needs to be approved by someone, we create a pull request (merge request). Pull requests basically means that we created some useful changes and want to merge them with another branch (usually with the main) branch

Suppose no approval is needed and we want to merge the feature from the feature branch to the main branch. We can do this with the following commands:

```
git checkout main - we switch to the main branch

git merge feature - we merge the feature branch with the main branch
```

##### conflicts when merging

Sometimes, when we merge two branches, there are conflicts. This happens when two people changed the same line of code in two different branches. For example, I was working on the main branch, and someone else was working on the feature branch. I changed something in the main.py, and someone else also changed something in the main.py. Then when I merge the feature branch with the main branch, I will get a conflict, and it will look like this:

```
CONFLICT (content): Merge conflict in main.py
Automatic merge failed; fix conflicts and then commit the result.
```

To fix the conflict, we need to open the file with the conflict (main.py in this case) and manually fix the conflict. We can do this with the following commands:

git diff - show the conflicts

So when the conflict occurs (for example, in the main.py) - we need to open this main.py file and fix the conflict by hand. After that, we can commit the changes and push them

git add main.py - add the file with the resolved conflict
git commit - commit the changes (at this point we do not need to add a message because it is a merge commit)

Then we will get a message like this:

```
Merge branch 'feature' into main
# Please enter a commit message to explain why this merge is necessary,
# especially if it merges an updated upstream into a topic branch.
#
# Lines starting with '#' will be ignored, and an empty message aborts
# the commit.
```

We do not need to do anything here except for exiting vim (:wq + enter), and the merge will be completed


##### remove files from the directory

Sometimes we want to remove some files from the directory. Deleting them from VScode folder is not enough. We need to delete them from git as well. We can do this with the following commands:

```
git rm file_name - remove a file from git

Example: git rm old_script.py

git rm -r folder_name - remove a folder from git

Example: git rm -r old_folder
```

Then we can commit these changes and push them - files will be removed from the remote repository as well

##### status

git status shows what files have been changed, what files have been added, what files have been deleted, etc. It also shows what branch we are currently at

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

