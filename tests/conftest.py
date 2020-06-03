import os

import pytest
from git import Repo


@pytest.fixture
def repo_path(tmp_path_factory):
    """ Create a git repo to test on. 
    
    tmp_path_factory is managed by pytest
    """
    r_path = tmp_path_factory.mktemp("git_test_repo")
    Repo.init(path=str(r_path))
    return str(r_path)


# @pytest.fixture
# def repo(tmp_path_factory):
#    """ Create a git repo to test on. tmp_path is managed by pytest.
#    """
#    r_path = tmp_path_factory.mktemp("git_test_repo")
#    return Repo.init(path=str(r_path))


# def rm_dir(directory):
#     """Recursively remove directory and it's contents.
#     """
#     for item in directory.iterdir():
#         if item.is_dir():
#             rm_dir(item)
#         else:
#             item.unlink()
#     directory.rmdir()
