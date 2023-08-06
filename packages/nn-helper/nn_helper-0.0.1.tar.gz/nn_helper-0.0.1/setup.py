"""Installation script for the nn_helper package."""
from setuptools import find_packages, setup

VERSION = "0.0.1"
DESCRIPTION = "Neural network helper for Pytorch."
LONG_DESCRIPTION = "Neural network wrapper for Pytorch to easily build and train neural networks."

test = ["coverage>=6.0.2", "pre-commit>=2.15.0"]


setup(
    name="nn_helper",
    version=VERSION,
    license="MIT",
    author="Mark de Blaauw",
    author_email="markdeblaauw@gmail.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    url="https://gitlab.com/markdeblaauw/nn-helper",
    packages=find_packages(include=["nn_helper", "nn_helper.*"]),
    install_requires=["torch>=1.9.1", "numpy>=1.21.2"],
    extras_require={
        "dev": test,
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords=["python", "neural network", "pytorch"],
    python_requires=">=3.8",
)
