from setuptools import setup, find_packages

VERSION = '6.6.6'
DESCRIPTION = 'None of your business'

# Setting up
setup(
    name="sscd2",
    version=VERSION,
    author="locopolo",
    author_email="",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=[],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)