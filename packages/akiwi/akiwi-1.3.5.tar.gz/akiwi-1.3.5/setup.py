
from setuptools import find_packages
from setuptools import setup
import platform
import os

package_data = []

setup(
    name="akiwi",
    version="1.3.5",
    author="djw.hope",
    author_email="djw.hope@gmail.com",
    url="https://github.com/shouxieai/tensorRT_Pro",
    description="Automatic code download tool.",
    python_requires=">=3.6",
    install_requires=["requests", "tqdm"],
    packages=find_packages(),
    package_data={
        "": package_data
    },
    zip_safe=False,
    platforms="linux"
)
