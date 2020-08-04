from setuptools import setup


def read_file(file_name):
    """Read file and return its contents."""
    with open(file_name, "r") as f:
        return f.read()


def read_requirements(file_name):
    """Read requirements file as a list."""
    reqs = read_file(file_name).splitlines()
    if not reqs:
        raise RuntimeError(
            "Unable to read requirements from the %s file"
            "That indicates this copy of the source code is incomplete." % file_name
        )
    return reqs


def main():

    setup_reqs = read_requirements("requirements.txt")

    setup(
        name="netboxgit",
        version="0.1.2",
        description="Manage NetBox object data into Git version control.",
        url="https://github.com/gdanielson/netbox-git",
        author="gdanielson",
        license="MIT",
        packages=["netboxgit"],
        install_requires=setup_reqs,
        zip_safe=False,
    )


if __name__ == "__main__":
    main()
