import os
import re

from setuptools import find_packages, setup

def read_file(filename):
    with open(filename) as file:
        return file.read()

__version__ = re.search("__version__ = '([0-9.]*)'",
                        read_file('stable_baselines3/__init__.py')).group(1)


long_description = """
# This isn't the official Stable Baselines3, it's an experimental version

The official SB3 is here: https://github.com/DLR-RM/stable-baselines3"""  # noqa:E501


setup(
    name="rigged_sb3",
    packages=[package for package in find_packages() if package.startswith("stable_baselines3")],
    package_data={"rigged_sb3": ["py.typed"]},
    install_requires=[
        "gym==0.22",
        "numpy",
        "torch>=1.11",
        # For saving models
        "cloudpickle",
        # For reading logs
        "pandas",
        # Plotting learning curves
        "matplotlib",
    ],
    extras_require={
        "tests": [
            # Run tests and coverage
            "pytest",
            "pytest-cov",
            "pytest-env",
            "pytest-xdist",
            # Type check
            "pytype",
            # Lint code
            "flake8>=3.8",
            # Find likely bugs
            "flake8-bugbear",
            # Sort imports
            "isort>=5.0",
            # Reformat
            "black",
            # For toy text Gym envs
            "scipy>=1.4.1",
        ],
        "docs": [
            "sphinx",
            "sphinx-autobuild",
            "sphinx-rtd-theme",
            # For spelling
            "sphinxcontrib.spelling",
            # Type hints support
            "sphinx-autodoc-typehints",
        ],
        "extra": [
            # For render
            "opencv-python",
            # For atari games,
            "ale-py==0.7.4",
            "autorom[accept-rom-license]~=0.4.2",
            "pillow",
            # Tensorboard support
            "tensorboard>=2.2.0",
            # Protobuf >= 4 has breaking changes
            # which does play well with tensorboard
            "protobuf~=3.19.0",
            # Checking memory taken by replay buffer
            "psutil",
        ],
    },
    description="Experimental version of SB3",
    author="Ram Rachum",
    url="https://github.com/DLR-RM/stable-baselines3",
    author_email="antonin.raffin@dlr.de",
    keywords="reinforcement-learning-algorithms reinforcement-learning machine-learning "
    "gym openai stable baselines toolbox python data-science",
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version=__version__,
    python_requires=">=3.7",
    # PyPI package information.
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)

# python setup.py sdist
# python setup.py bdist_wheel
# twine upload --repository-url https://test.pypi.org/legacy/ dist/*
# twine upload dist/*
