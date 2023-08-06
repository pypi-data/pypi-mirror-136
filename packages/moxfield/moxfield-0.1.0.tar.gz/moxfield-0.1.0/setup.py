from setuptools import setup, find_packages

VERSION = '0.1.0' 
DESCRIPTION = 'Moxfield'
LONG_DESCRIPTION = 'Python tools to interact with Moxfield'

# Setting up
setup(
        name="moxfield", 
        version=VERSION,
        author="Michael Celani",
        author_email="michael.j.celani@gmail.com",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[],
        
        keywords=['python'],
        classifiers= [
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)