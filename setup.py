from setuptools import find_packages, setup
from typing import List

HYPHEN_E_DOT = "-e ."

def get_requirements(file_path: str) -> List[str]:
    """
    Yeh function requirements.txt padhta hai aur packages ki list return karta hai.
    """
    requirements = []
    with open(file_path) as file_obj:
        requirements = file_obj.readlines()
        requirements = [req.replace("\n", "") for req in requirements]
        
        # Comments (#) aur empty lines ko ignore karo
        requirements = [req for req in requirements if req and not req.startswith("#")]

        if HYPHEN_E_DOT in requirements:
            requirements.remove(HYPHEN_E_DOT)
            
    return requirements

setup(
    name="returnshield_ai",
    version="0.0.1",
    author="Hackathon Team",
    author_email="example@domain.com",
    packages=find_packages(),
    install_requires=get_requirements("requirements.txt")
)
