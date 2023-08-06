from setuptools import setup, find_packages

f = open("README.md", "r")
VERSION = '0.0.1' 
DESCRIPTION = 'A Tkinter Extension'
LONG_DESCRIPTION = f.read()

# Setting up 
setup(
       
        name="Raindeer", 
        version=VERSION,
        author="scorpio8k",
        author_email="scorpion8k2@hotmail.com",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=['pillow'], # external packages as dependencies (optional)
        
        keywords=['python', 'extension', 'tkinter'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)