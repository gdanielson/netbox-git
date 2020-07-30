import json
import logging
import os
import sys
from pathlib import Path

import pynetbox
import requests

logger = logging.getLogger(__name__)


class GDNetBoxer:
    """
    """

    def __init__(self, url=None, token=None, threading=False, ssl_verify=True):
        """
        """

        self.url = url
        self.token = token
        self.threading = threading

        self.nb = pynetbox.api(self.url, token=self.token, threading=self.threading)
        self.nb.http_session = requests.Session()
        self.nb.http_session.verify = True if ssl_verify else False

    def _fix_for_filename(self, in_filename):
        """ Replace path separator character in name.
        """
        return in_filename.replace("/", "-")

    def _del_items_with_value(self, d, vals_to_del):
        """ Recursively remove dictionary items that have a value in vals_to_del

        :param d: Dict to operate on
        :type d: dict
        :param vals_to_del: A list of values for dict.items to be removed
        :type vals_to_del: list 
        :return: Dict with selected items removed
        :rtype: dict
        """
        if not isinstance(d, dict):
            return d
        return dict(
            (k, self._del_items_with_value(v, vals_to_del))
            for k, v in d.items()
            if v not in vals_to_del
        )

    def _del_keys_from_dict(self, d, keys_to_del):
        """ Recursively remove dictionary items that have a key in keys_to_del

        :param d: Dict to operate on.
        :type d: dict
        :param keys_to_del: A list of keys for items to be removed.
        :type keys: list
        :return: Dict with selected items removed
        :rtype: dict
        """
        if not isinstance(d, dict):
            return d
        return {
            k: self._del_keys_from_dict(v, keys_to_del)
            for k, v in d.items()
            if not k in keys_to_del
        }

    def find_pri_device_for_object(self, in_obj):
        """For a given object find the relating device containing the primary IP address.

        :param in_obj: pynetbox input object
        :type in_obj: pynetbox input object
        :return: pynetbox object containing the primary IP address
        :rtype: pynetbox device
        """

        try:

            if in_obj.primary_ip4.address:
                return in_obj

        except AttributeError:

            # The management IP address of an interface that is within a virtual chassis...
            # intf = nb.dcim.devices.get(INTERFACE)
            # intf_dev = intf.device.id
            # intf_dev_vc = intf_dev.virtual_chassis.master.id
            # intf_dev_vc_addr = intf_dev_vc.primary_ip4.address  # e.g. 192.168.1.21/24

            try:
                _device = self.nb.dcim.devices.get(in_obj.virtual_chassis.master.id)
            except AttributeError:
                pass

            try:
                _device = self.nb.dcim.devices.get(in_obj.device.id)
            except AttributeError:
                pass

            return self.find_pri_device_for_object(_device)

    def get_tag_from_netbox(self, tag_name=""):
        """Retrieve the named NetBox tag data.
        """
        self.tag_name = tag_name
        self.tag_data = self.nb.extras.tags.filter(name=self.tag_name)
        logger.debug(f"Tag data received from Netbox: {self.tag_data}")
        assert (
            len(self.tag_data) == 1
        ), f"Unexpected number of tags received, expected one"
        return self.tag_data[0]

    def upd_tag_to_netbox(self, tag_name, **kwargs):
        """Update the NetBox tag with new information provided."
        """
        pass

    def get_interfaces_data(self, nbx_tag):
        """Get interfaces for a tag.

        :param nbx_tag: The name of the NetBox tag
        :type nbx_tag: str
        """
        if not nbx_tag:
            msg = "A NetBox tag must be given to be used as a filter."
            logger.error(msg)
            raise ValueError(msg)

        self.nbx_tag = nbx_tag
        self.interfaces = self.nb.dcim.interfaces.filter(tag=self.nbx_tag)
        return self.interfaces

    def write_devices_to_file(self, devices, base_path):
        """Write data for each device to a JSON file.

        :param interfaces: A dict of device information
        :type interfaces: dict
        """
        self.devices = devices
        file_path = Path.joinpath(Path(base_path), Path("devices/"))
        file_path.mkdir(parents=True, exist_ok=True)
        fout = Path(file_path / "devices.json")
        with open(fout, "w", buffering=1) as f:
            f.write(json.dumps(self.devices, sort_keys=True, indent=4))

    def write_interfaces_to_file(self, interfaces, base_path):
        """Write data for each interface to a JSON file.

        :param interfaces: A list of pynetbox interface objects
        :type interfaces: list
        """
        self.interfaces = interfaces
        file_path = Path.joinpath(Path(base_path), Path("interfaces/"))
        file_path.mkdir(parents=True, exist_ok=True)

        for interface in self.interfaces:
            # Generate output filename as <device--interface.json> replacing / with -
            intf_name = interface.name
            intf_name = intf_name.replace("/", "-")
            file_str = "--".join((interface.device.name, intf_name)) + ".json"

            fout = Path(file_path / file_str)
            if not fout.exists():
                fout.touch()
            intf = dict(interface)  # cast pynetbox object to dict
            intf_rec = json.dumps(intf, sort_keys=True, indent=4)
            with open(fout, "w", buffering=1) as f:
                f.write(intf_rec)

    def read_interfaces_from_file(self, input_path):
        """Read interface JSON file(s) into a dictionary.

        :param input_path: Source directory of files to read
        :type input_path: string
        :return: build_dict
        :rtype: dict
        """
        files_path = Path(input_path)
        # FIXME(GD) Use input parameter once prototyping completed.
        files_path = Path("/Users/gdanielson/repos/netbdata/d/interfaces")
        files = [i for i in files_path.iterdir() if i.is_file()]
        build_dict = {}

        for file in files:
            with open(file, "r") as f:
                this = json.loads(f.read())
            dev_name = this["device"]["name"]
            if not dev_name in build_dict:
                build_dict[dev_name] = {}
            build_dict[dev_name][this["name"]] = this
        return build_dict

    def get_devices_data(self, nbx_tag=""):
        """Get devices for a tag.
        """
        self.nbx_tag = nbx_tag
        self.devices = self.nb.dcim.devices.filter(tag=self.nbx_tag)
        return self.devices

    def adapt_interfaces_for_netbox(self, objects):
        """

        NOTE: when casting a NetBox object to a dict, this cannot be pushed
        back into NetBox as is. As the data has embedded hypertext links for
        correct REST API navigation the API won't accept this back in. Other
        fields not accepted are "display_name", "status" value must be the
        int not the string ...and some others I can't recall right now.
        However, if method serialize() is used this data is less useful to
        commit into git and operate on for deployment purposes but it can be
        written back to NetBox as is. Two options at the moment:

        1. just cast to a dict, then when needed to put back to
        Netbox perform a whole lot of data editing to remove all the bits and
        pieces NetBox doesn't allow back in. 
        TODO(GD): Check on removing/cleaning up the "problem" data when
        recving from NetBox but that may lose useful data for deployment.

        2. keep both serialized and the dict versions of the object so that
        serialised data can be written back without having to reverse engineer
        the mangling required. Downside tho is having to track pieces of data
        for every NetBox object and the risk of them getting out of
        state/sync.
        """

        # list of keys to be removed
        unwanted_dict_keys = ["display_name", "url"]
        unwanted_dict_values = []  # remove keys with these values

        for intfs in objects.values():
            for intf in intfs.values():
                intf["type"] = intf["type"]["id"]

        cleaned_objects = self._del_items_with_value(objects, unwanted_dict_values)
        return self._del_keys_from_dict(cleaned_objects, unwanted_dict_keys)

    def update_interfaces_to_netbox(self, dev_intf_data):
        """ Write interface data to NetBox.

        :param dev_intf_data: A dictionary of interfaces
        :type dev_intf_data: dict
        :return: A boolean of True if the operation succeeds, otherwise False.
        :rtype: bool
        """

        try:
            assert isinstance(dev_intf_data, dict), "Input parameter is not a dict."
        except AssertionError as error:
            logger.exception(error)

        for dev_name, intfs in dev_intf_data.items():
            intf_names = list(intfs.keys())
            nbx_intfs = self.nb.dcim.interfaces.filter(device=dev_name, name=intf_names)

            try:
                for nbx_intf in nbx_intfs:
                    assert nbx_intf.update(
                        intfs[nbx_intf.name]
                    ), f"Error detected while updating {dev_name} {nbx_intf.name} to NetBox"
            except AssertionError as error:
                logger.exception(error)
            except Exception as exc:  # unexpected exception
                logger.exception(exc, False)


def main():
    """
    """
    pass


if __name__ == "__main__":
    # main()
    print("Not designed to be executed directly")
