from setuptools import find_packages, setup

PKG_NAME = "zeitgeber"

version = "0.0.2"

setup(
    name=PKG_NAME,
    version=version,
    packages=find_packages(),
    description=(
        "A library with utils to work with circadian time timeseries and plot them"
    ),
    zip_safe=False,

)
