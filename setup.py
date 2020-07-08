from setuptools import setup

setup(
    name="netboxgit",
    version="0.1",
    description="Manage NetBox object data into Git version control.",
    url="https://github.com/gdanielson/netbox-git",
    author="gdanielson",
    license="MIT",
    packages=["netboxgit"],
    install_requires=[
        "certifi==2020.4.5.2",
        "chardet==3.0.4",
        "gitdb==4.0.5",
        "GitPython==3.1.3",
        "idna==2.9",
        "pynetbox==4.3.1",
        "requests==2.24.0",
        "six==1.15.0",
        "smmap==3.0.4",
        "urllib3==1.25.9",
    ],
    zip_safe=False,
)
