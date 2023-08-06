from setuptools import setup, find_packages
import codecs
import os

VERSION = '1.1.8'
DESCRIPTION = 'Takes command from user and converts text to speech, this module is used for A.I Systems to make system speak and listen'
LONG_DESCRIPTION = 'A package to make system speak and listen'

# Setting up
setup(
    name="commandtaker",
    version=VERSION,
    author="Mahfuz Rahman",
    author_email="mahfuzrahman038@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['speechrecognition', 'pyttsx3'],
    keywords=['speech recognition', 'text to speech', 'take command', 
    'A.I system', 'A.i Assistant', 'jarvis', 'personal assistant', 
    'mahfuz rahman', 'how to make personal assistant using python', 
    'python personal assistant', 'commandtaker', 'CommandTaker', 
    'Command Taker', 'command taker'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ]
)