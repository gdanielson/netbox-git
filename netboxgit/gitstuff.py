import logging
import os
import sys
import textwrap

import git
from git.exc import GitError

"""
NOTE
# from git import Repo
Orignally went down the path of using git.Repo but then found it seems that
it is not designed to do the equivalent of simple git cli operations e.g. git
add --all. Right now I'm not willing to go deep down a git rabbit hole so for
now just started to use git.Git which you can do cli stuff with
--porcelain param. It may be that need to revert to the fuller functionality
later if more complex git operations are needed to find diffs etc.
"""

logger = logging.getLogger(__name__)


def get_env_variable(env_var):
    try:
        logger.debug(f"Get environment variable {env_var}")
        return os.environ[env_var]

    except KeyError as exc:
        message = f"The environment variable '{env_var}' was not found."
        logger.error(message)
        raise exc

    except Exception as exc:
        message = f"Unexpected problem loading environment variable '{env_var}' "
        logger.error(message)
        raise exc


# def load_repo(repo_location):
#    """ Load a repo from the path specified and checking it is in a clean state.
#    """
#    try:
#        repo = git.Repo(repo_location)
#        assert len(repo.untracked_files) == 0, "Repo has untracked file(s) present"
#        assert not repo.is_dirty(), "Repo has uncommitted changes present"
#
#    except AssertionError as exc:
#        logger.error(str(exc))
#        raise exc
#
#    except Exception as exc:
#        message = f"Failed to load the repo from location '{repo_location}' "
#        logger.error(message)
#        logger.error(exc.__repr__())
#        raise exc
#
#    return repo


def clone_repo(remote_url, local_path):
    """ Create a local clone from the remote repo to work on.

    :param remote_url: The Git URL of the source to clone from.
    :type remote_url: str File system path.
    :param local_path: The local destination diretory to git clone to.
    :type local_path: str File system path.
    :return: Repo instance pointing to the cloned directory
    """

    try:
        return git.Repo.clone_from(remote_url, local_path)
    except GitError as exc:
        message = f"Problem while cloning the repo from {remote_url} to {local_path}"
        logger.error(message)
        logger.error(exc.__repr__())
        raise exc


def load_repo(repo_path):
    """ Load a repo from the path specified and checking it is in a clean state.

    :param repo_path: The git working tree directory to work on
    :type repo_path: str File system path
    :return: A git repo :class:`git.cmd.Git`
    :rtype: git.cmd.Git
    """
    logger.debug(f"Loading git repo at path {repo_path}")
    repo = git.Git(repo_path)

    try:
        repo.status("--porcelain")

    except Exception as exc:
        message = f"Failed to load the repo at path {repo_path}"
        logger.error(message)
        logger.error(exc.__repr__())
        raise

    else:
        return repo


def isclean(repo):
    """Return True if the repo is clean and also contains no untracked files.

    :param repo: The repo to operate on
    :type repo: :class:`git.cmd.Git`
    :return: `True` if the repo is clean, `False` otherwise
    :rtype: bool
    """
    logger.debug(f"Checking git repo is clean")
    gstatus = repo.status("--porcelain")  # returns empty string if clean

    if gstatus == "":
        return True
    else:
        return False


def prepare_branch(repo, branch_from, branch_to):
    """ Checkout a new git branch ready for updates to commit.

    git checkout MASTER
    git fetch -p origin
    git checkout -b newbranch --no-track origin/master

    :param repo: The repo to operate on
    :type repo: :class:`git.cmd.Git`
    :param branch_from: Branch name to branch from
    :type branch_from: str
    :param branch_to: Branch name to create
    :type branch_to: str
    :return: Branch name created
    :rtype: TODO
    """
    logger.debug(f"git checkout a new branch for updating")
    assert (
        repo.rev_parse("--abbrev-ref", "HEAD") == branch_from
    ), f"Repo is not on branch {branch_from}"

    try:
        repo.checkout(branch_from, b=branch_to)
    except GitError as exc:
        logger.error(str(exc))
        raise exc

    try:
        assert (
            repo.rev_parse("--abbrev-ref", "HEAD") == branch_to
        ), f"Problem with git checkout -b {branch_to} "
    except AssertionError as exc:
        logger.error(str(exc))
        raise exc


def commit_all(repo):
    """Add all changes (including untracked files) creating a new commit.

        The generated commit message is made up of the filenames up to a max. line length.

    :param repo: The repo to operate on
    :type repo: :class:`git.cmd.Git`
    :return: `True` if the commit succeeded, `False` otherwise
    :rtype: bool
    """
    # TODO(GD) As things progress it may be valuable to return the new commit id.

    logger.debug(f"Performing git commit of all changes")
    if not isclean(repo):
        rawstring = repo.status("--porcelain")
        # 1st 3 chars in porcelain output is status, drop them leaving just the filename
        filenames = [i[3:] for i in rawstring.splitlines()]
        long_msg = ["Upd"] + filenames
        commit_msg = textwrap.shorten(" ".join(long_msg), width=70, placeholder="...")
        repo.add("--all")
        repo.commit(message=commit_msg)
        return True
    else:
        return False


def push_branch(repo, branch_name, remote="origin"):
    """ Perform git push of the given branch to the named remote.

    :param repo: The repo to operate on
    :type repo: :class:`git.cmd.Git`
    :param branch_name: The git branch to push
    :type branch_name: str
    :param remote: The name of the git remote to push to
    :type remote: str
    """
    pass


def delete_branch(repo, branch_name):
    """ Delete the given git branch from the repo.

    :param repo: The repo to operate on
    :type repo: :class:`git.cmd.Git`
    :param branch_name: The git branch to delete
    :type branch_name: str
    """
    pass


if __name__ == "__main__":
    # main()
    print("Not designed to be executed directly")
