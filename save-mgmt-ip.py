import logging
import os

from netboxgit import gitstuff, netboxdata

""" This is a temporary experimental file to control running things while
prototyping NetBox-Git interactions.
"""

logger = logging.getLogger()
log_formatter = logging.Formatter(
    "%(asctime)s %(filename)s:%(lineno)d %(levelname)+8s: " "%(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%Z",
)
s_handler = logging.StreamHandler()
s_handler.setFormatter(log_formatter)
logger.addHandler(s_handler)
logger.setLevel(logging.INFO if not os.environ.get("DEBUG") else logging.DEBUG)

_ssl_verify = os.environ.get("NETBOX_SSL_VERIFY").lower()
NETBOX_SSL_VERIFY = False if _ssl_verify in ("no", "n", "false", "0", "") else True
NETBOX_URL = gitstuff.get_env_variable("NETBOX_URL")  # e.g. http://ip:[port]
NETBOX_TOKEN = gitstuff.get_env_variable("NETBOX_TOKEN")
NETBOX_TAG = gitstuff.get_env_variable("NETBOX_TAG")
GIT_REMOTE_URL = gitstuff.get_env_variable("GIT_REMOTE_URL")
GIT_LOCAL_PATH = gitstuff.get_env_variable("GIT_LOCAL_PATH")
GIT_BRANCH_MAIN = gitstuff.get_env_variable("GIT_BRANCH_MAIN")


logger.debug(f"Performing git clone from git remote repo")
rpo = gitstuff.clone_repo(GIT_REMOTE_URL, GIT_LOCAL_PATH)
r_path = rpo.working_dir
repo = gitstuff.load_repo(GIT_LOCAL_PATH)
try:
    assert (
        gitstuff.isclean(repo) is True
    ), f"Cannot proceed, git repo {repo.working_dir} contains uncommitted changes or untracked files"
except AssertionError as exc:
    logger.error(str(exc))
    raise exc

logger.debug(f"Performing git checkout -b")
# From <GIT_BRANCH_MAIN>, checkout a new branch named <NETBOX_TAG>
gitstuff.prepare_branch(repo, GIT_BRANCH_MAIN, NETBOX_TAG)

logger.debug(f"Opening connection to NetBox")
nbx = netboxdata.GDNetBoxer(
    url=NETBOX_URL, token=NETBOX_TOKEN, threading=True, ssl_verify=NETBOX_SSL_VERIFY
)

logger.debug(f"Getting interface data from NetBox")
intf_data = nbx.get_interfaces_data(NETBOX_TAG)


logger.info(f"End")
logger.info(f"End")
logger.info(f"End")
logger.info(f"End")
logger.info(f"End")
