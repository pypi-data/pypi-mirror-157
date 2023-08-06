from setuptools import setup, find_packages


VERSION = "0.1"
DESCRIPTION = "My First Python Package"
LONG_DESCRIPTION = "My First Python Pakage With some more description"


setup(
    name="sagar_module",
    version=VERSION,
    author="Sagar Neupane",
    author_email="Sagar.neupane419@gmail.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires = [],
    keywords=["python","first package"],
    classifiers=[
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        
    ]
    
)

