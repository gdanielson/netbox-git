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
    """Create a local clone from the remote repo to work on.

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
    """Load a repo from the path specified and checking it is in a clean state.

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
    """Checkout a new git branch ready for updates to commit.

    git checkout MASTER
    git checkout branch_to
    if error branch_to doesn't exist:
        git checkout -b branch_to --no-track origin/master

    :param repo: The repo to operate on
    :type repo: :class:`git.cmd.Git`
    :param branch_from: Branch name to branch from
    :type branch_from: str
    :param branch_to: Branch name to create
    :type branch_to: str
    :return: Branch name created
    :rtype: TODO
    """

    # TODO check confirm is this check needed when cloning from a bare repo?
    logger.debug(f"Check that repo is on {branch_from}")
    if repo.rev_parse("--abbrev-ref", "HEAD") != branch_from:
        raise RuntimeError(f"The remote repo is not on branch {branch_from}")

    logger.debug(f"git checkout branch {branch_to} for updating")
    try:
        repo.checkout(branch_to)
    except GitError as exc:
        repo.checkout(branch_from, b=branch_to)

    try:
        assert (
            repo.rev_parse("--abbrev-ref", "HEAD") == branch_to
        ), f"Problem with git checkout of {branch_to} "
    except AssertionError as exc:
        logger.error(str(exc))
        raise exc


def commit_all(repo, commit_msg):
    """Add all changes (including untracked files) creating a new commit.

    :param repo: The repo to operate on
    :type repo: :class:`git.cmd.Git`
    :param commit_msg: Information string for the git commit
    :type commit_msg: str
    :return: `True` if the commit succeeded, `False` otherwise
    :rtype: bool
    """
    # TODO(GD) As things progress it may be valuable to return the new commit id.

    logger.debug(f"Performing git commit of all changes")
    if not isclean(repo):
        repo.add("--all")
        repo.commit(message=commit_msg)
        return True
    else:
        return False


def push_branch(repo, branch_name, remote="origin"):
    """Perform git push of the given branch to the named remote.

    :param repo: The repo to operate on
    :type repo: :class:`git.cmd.Git`
    :param branch_name: The git branch to push
    :type branch_name: str
    :param remote: The name of the git remote to push to
    :type remote: str
    """
    try:
        push_out_raw = repo.push("--porcelain", remote, branch_name)
    except GitError as exc:
        logger.error(str(exc))
        raise exc

    bad_words = ["failed", "error", "rejected"]

    if any([word in push_out_raw.lower() for word in bad_words]):
        [logger.error(eline) for eline in push_out_raw.splitlines()]
        raise RuntimeError(
            f"Bad response detected in the output of 'git push {remote} {branch_name}'"
        )

    logger.debug(push_out_raw.splitlines())


def delete_branch(repo, branch_name):
    """Delete the given git branch from the repo.

    :param repo: The repo to operate on
    :type repo: :class:`git.cmd.Git`
    :param branch_name: The git branch to delete
    :type branch_name: str
    """
    pass


if __name__ == "__main__":
    # main()
    print("Not designed to be executed directly")
