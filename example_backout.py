import logging
import os

from netboxgit import gitstuff, netboxdata

""" This is an example prototyping demo for updating NetBox objects from a git repo.
This could be used to revert some NetBox objects to a different point in time.
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


NETBOX_URL = gitstuff.get_env_variable("NETBOX_URL")  # e.g. http://ip:[port]
NETBOX_TOKEN = gitstuff.get_env_variable("NETBOX_TOKEN")

nbx = netboxdata.GDNetBoxer(url=NETBOX_URL, token=NETBOX_TOKEN, threading=True,)

""" 1. go to commit and read the data
    gitstuff.go_to_commit(repo, commit_id)
"""
logger.debug(f"Reading interface data from repo files")
intfs_from_file = nbx.read_interfaces_from_file(
    "/Users/gdanielson/repos/netbdata/d/interfaces"
)

""" 2. Massage data into format acceptable to NetBox
    nbx.adapt_data(devices) or interfaces or whatever
"""
logger.debug(f"Preparing data to update NetBox")
cleaned_intfs = nbx.adapt_interfaces_for_netbox(intfs_from_file)

""" 3. Update the NetBox object from the commit
"""
logger.debug(f"Updating interfaces to NetBox")
nbx.update_interfaces_to_netbox(cleaned_intfs)

logger.info(f"End")
