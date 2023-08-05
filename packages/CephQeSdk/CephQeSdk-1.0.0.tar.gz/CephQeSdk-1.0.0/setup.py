# -*- coding: utf-8 -*-
try:
    from setuptools import find_packages, setup
except ImportError:
    from ez_setup import use_setuptools

    use_setuptools()
    from setuptools import find_packages, setup

setup(
    name="CephQeSdk",
    version="1.0.0",
    description="RHCS QE SDK Library",
    url="https://gitlab.cee.redhat.com/rhcs-qe/rhcs-qe-sdk",
    author="Red Hat Inc.",
    author_email="cephci@redhat.com",
    install_requires=["fabric3"],
    long_description_content_type="text/markdown",
    zip_safe=True,
    include_package_data=True,
    packages=find_packages("src", exclude=["ez_setup"]),
    package_dir={"": "src"},
)
