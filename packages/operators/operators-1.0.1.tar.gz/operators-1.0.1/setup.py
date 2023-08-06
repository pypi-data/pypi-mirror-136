from setuptools import setup, find_packages

VERSION = '1.0.1' 
DESCRIPTION = 'Arithmetic Operators'
LONG_DESCRIPTION = 'This package has all the basic arithmetic operators like addition, subtrations, multiply, divide'

# Setting up
setup(
       # the name must match the folder name 
        name="operators", 
        version=VERSION,
        author="Dushyant Lavania",
        author_email="<dushyantlavania2001@gmail.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'Arithmetic operators'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)