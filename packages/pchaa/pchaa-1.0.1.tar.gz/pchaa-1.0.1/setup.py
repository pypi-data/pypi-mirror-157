from importlib_metadata import entry_points
from setuptools import setup, find_packages
from pchaa import about

VERSION = '1.0.1' 
DESCRIPTION = 'pchaa'
LONG_DESCRIPTION = 'Power Search and Autocomplete'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name=about.__name__, 
        version=VERSION,
        author="Rushi Chaudhari",
        author_email="rushic24@gmail.com",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=['python-libxdo', 'prompt_toolkit'], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'pchaa', 'power', 'terminal'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 3",
        ],
        entry_points={
            "console_scripts":[
                "pchaa=pchaa.__main__:main",
            ]
        }
)