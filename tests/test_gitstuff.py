import pytest

from .context import gitstuff

# def test_get_env_variable():
#    get_env_variable(name)


def test_load_repo(repo_path):
    r = gitstuff.load_repo(repo_path)
    assert r.working_dir == repo_path


# def test_that_repo_is_clean(repo):
#     """Ensure there are no uncommited changes or untracked files.
#     """
#     # check that the repo is clean, no uncommited changes
#     
#     r = gitstuff.check_repo(repo)
# 
#     assert not r.is_dirty()
#     assert len(r.untracked_files) == 0
