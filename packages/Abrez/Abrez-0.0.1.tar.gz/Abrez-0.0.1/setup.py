from setuptools import setup, find_packages
import codecs
import os

VERSION = "0.0.1"
DESCREPTION = "ABREZ"
LONG_DESCREPTION = "when you'll make jarvis it will help you very much you'll not need to install many modules"

setup(
    name="Abrez",
    version=VERSION,
    author="Abrez",
    author_email="tajwarhuma2015@gmail.com",
    description=DESCREPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCREPTION,
    packages=find_packages(),
    install_requires =['pyttsx3', 'speech_recognition', 'datetime'],
    keywords=['speak', 'wish', 'take_command','python_tutorial', 'jarvis', 'Artificial Intelligence', 'AI', 'Abrez'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)