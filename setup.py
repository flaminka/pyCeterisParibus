from setuptools import setup, find_packages

PACKAGE_NAME = 'pyCeterisParibus'
REQUIREMENTS_PATH = 'requirements.txt'
README_PATH = 'README.md'
VERSION = '0.0.1'


def get_requirements():
    with open(REQUIREMENTS_PATH, 'r') as f:
        requirements = f.read().splitlines()
        return requirements


def get_readme():
    with open(README_PATH, 'r') as f:
        return f.read()


setup(name=PACKAGE_NAME,
      version=VERSION,
      description='Ceteris Paribus python package',
      long_description=get_readme(),
      url='https://github.com/ModelOriented/pyCeterisParibus',
      author='Michał Kuźba',
      author_email='michal.kuzba@students.mimuw.edu.pl',
      packages=find_packages(exclude=['examples', 'tests']),
      install_requires=get_requirements())
