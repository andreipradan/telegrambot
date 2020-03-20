import os
import sys

from git import Repo

PATH_OF_GIT_REPO = os.getenv('PATH_TO_GIT_FOLDER')


def git_push(commit_message):
    repo = Repo(PATH_OF_GIT_REPO)
    repo.git.add(A=True)
    repo.index.commit(commit_message)
    origin = repo.remote(name='origin')
    origin.push()


if __name__ == '__main__':
    message = sys.argv[1] if len(sys.argv) == 2 else 'Auto commit'
    git_push(message)
