'''
this is an essential filr for packaging and distributing python projects.
it is used by setuptools to define the config of your project,such as metadata,
dependencies, and entry points...etc
'''
from setuptools import setup, find_packages#it search for __init__.py in all folders (find_packages)
from typing import List
def get_requirements()->List[str]:
    """
    this function will return the list of requirements
    """
    requirement_lst:List[str]=[]
    try:
        with open('requirements.txt') as f:
            lines = f.readlines()
            #process the requirements
            for line in lines:
                requirement=line.strip()
                if requirement and requirement!='-e .':
                    requirement_lst.append(requirement)
    except FileNotFoundError:
        print("requirements.txt file not found. Please ensure it exists.")
    return requirement_lst
print(get_requirements())

#setup metadata
setup(
    name="NetworkSecurityNew",
    version="0.0.1",
    author="Jayavardhan",
    author_email="jayavardhanperala@gmail.com",
    packages=find_packages(),  # Automatically find packages in the project directory
    install_requires=get_requirements(),  # List of dependencies
)