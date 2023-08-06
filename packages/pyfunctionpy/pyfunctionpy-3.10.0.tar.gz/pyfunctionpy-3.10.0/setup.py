from setuptools import setup, find_packages

VERSION = '3.10.0' 
DESCRIPTION = 'A package that simplifies alot of stuff'
LONG_DESCRIPTION = 'very simple'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="pyfunctionpy", 
        version=VERSION,
        author="Daniel Duchouquette",
        author_email="<danpersonguything@email.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'Simple'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)