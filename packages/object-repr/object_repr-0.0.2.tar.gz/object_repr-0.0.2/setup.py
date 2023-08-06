from pathlib import Path
from setuptools import setup, find_packages

VERSION = '0.0.2'
DESCRIPTION = 'Provide dynamic __repr__ method for any __dict__ based class.'
# read the contents of your README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()
project_urls = {
    'Source Code': 'https://git.dev.earnix.com/idank/object-repr',
}

# Setting up
setup(
    name="object_repr",
    version=VERSION,
    author="Idan Kalderon",
    author_email="<idan9532@gmail.com>",
    description=DESCRIPTION,
    long_description=long_description,
    packages=find_packages(),
    install_requires=[],
    project_urls=project_urls,
    keywords=['python', 'repr', 'print'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
