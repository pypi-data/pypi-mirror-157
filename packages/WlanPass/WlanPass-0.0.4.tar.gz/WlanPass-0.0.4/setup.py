from setuptools import setup, find_packages
import codecs
import os
VERSION = '0.0.4'
DESCRIPTION = 'Prints The Stored Wlan Details'
LONG_DESCRIPTION = 'A module that can access the details of stored password or any other information related to wlan'

# Setting up
setup(
    name="WlanPass",
    version=VERSION,
    author="Mohammad Mahfuz Rahman",
    author_email="mahfuzrahman038@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['commandtaker'],
    keywords=['python', 'wi-fi', 'wlan', 'passwords', 'wi-fi hacker', 'cracker'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ]
)