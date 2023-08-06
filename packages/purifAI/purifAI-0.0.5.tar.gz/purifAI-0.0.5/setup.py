from setuptools import setup, find_packages

VERSION = '0.0.5' 
DESCRIPTION = 'purifai'
LONG_DESCRIPTION = 'Machine Learning for solid phase extraction Method Prediction'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="purifAI", 
        version=VERSION,
        author="Ying Ying Cheung, Jennifer Amis, Luke Perrin",
        author_email="<yycheungds@gmail.com>,<jenamis@gmail.com>,<luperrin@westmont.edu>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'first package'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)
