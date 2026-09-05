from setuptools import find_packages, setup
from typing import List

HYPHEN_E_DOT = "-e ."


def get_requirements(file_path: str) -> List[str]:
    """
    Parses requirements.txt and returns list of required package dependencies.
    """
    requirements = []
    with open(file_path) as file_obj:
        requirements = file_obj.readlines()
        requirements = [req.replace("\n", "").strip() for req in requirements]
        # Ignore comments and empty lines
        requirements = [req for req in requirements if req and not req.startswith("#")]

        if HYPHEN_E_DOT in requirements:
            requirements.remove(HYPHEN_E_DOT)

    return requirements


setup(
    name="returnshield_ai",
    version="2.0.0",
    author="ReturnShield AI Team",
    packages=find_packages(),
    install_requires=get_requirements("requirements.txt"),
)
