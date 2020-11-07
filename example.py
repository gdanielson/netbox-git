import logging
import os
from pathlib import Path

from netboxgit import gitstuff, netboxdata

""" Retrieve NetBox interfaces with specified NetBox tag then commit changes
to the given Git repo. """

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
NETBOX_SSL_VERIFY = False if _ssl_verify in ("no", "n", "false", "0") else True
NETBOX_URL = gitstuff.get_env_variable("NETBOX_URL")  # e.g. http://ip[:port]
NETBOX_TOKEN = gitstuff.get_env_variable("NETBOX_TOKEN")
NETBOX_TAG = gitstuff.get_env_variable("NETBOX_TAG")
GIT_REMOTE_URL = gitstuff.get_env_variable("GIT_REMOTE_URL")
GIT_LOCAL_PATH = gitstuff.get_env_variable("GIT_LOCAL_PATH")
GIT_BRANCH_MAIN = gitstuff.get_env_variable("GIT_BRANCH_MAIN")


def setup_data_path(base_path):
    """ Ensure filesystem path for the data exists."""

    _dpath = Path.joinpath(Path(base_path), "data")
    _dpath.mkdir(parents=True, exist_ok=True)
    return _dpath


rpo = gitstuff.clone_repo(GIT_REMOTE_URL, GIT_LOCAL_PATH)
repo_path = rpo.working_dir

logger.debug("Performing git clone from git remote repo")
repo = gitstuff.load_repo(GIT_LOCAL_PATH)
try:
    assert (
        gitstuff.isclean(repo) is True
    ), f"Cannot proceed, git repo {repo_path} contains uncommitted changes or untracked files"
except AssertionError as exc:
    logger.error(str(exc))
    raise exc

data_path = setup_data_path(repo_path)

# From <GIT_BRANCH_MAIN>, checkout a new branch named <NETBOX_TAG>
gitstuff.prepare_branch(repo, GIT_BRANCH_MAIN, NETBOX_TAG)

logger.debug("Opening connection to NetBox")
nbx = netboxdata.GDNetBoxer(
    url=NETBOX_URL, token=NETBOX_TOKEN, threading=True, ssl_verify=NETBOX_SSL_VERIFY
)

logger.debug("Getting interface data from NetBox")
""" get_interfaces_data() returns a list of dicts, one per interface
        {
            "interface": <Interface object>
            "mgmt_name": <string>
            "mgmt_device": <Device object>
            "parent_device": <Device object>
        }
"""
intf_data = nbx.get_interfaces_data(NETBOX_TAG)
if not intf_data:
    logger.info(f"No data returned for NetBox objects tagged {NETBOX_TAG}")

logger.debug("Getting device name & ip for interface data")
devices = {}
for intf in intf_data:
    device = {}

    device["hostname"] = intf["mgmt_device"].primary_ip.address
    device["platform"] = intf["mgmt_device"].platform.slug
    device_name = intf["mgmt_name"]
    devices[device_name] = device

logger.debug(f"Writing device data to {data_path}")
nbx.write_devices_to_file(devices, data_path)

logger.debug(f"Writing interface data to {data_path}")
nbx.write_interfaces_to_file(intf_data, data_path)

if gitstuff.commit_all(repo, NETBOX_TAG):
    logger.info(f"Updates committed to git branch {NETBOX_TAG}")
    gitstuff.push_branch(repo, NETBOX_TAG)
    logger.info(f"git branch {NETBOX_TAG} pushed to remote")
else:
    logger.debug("git repo detected no changes")
    # FIXME gitstuff.delete_branch(repo, NETBOX_TAG) # No changes so delete the feature branch

logger.info("End")
