from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'Provide dynamic __repr__ method for any __dict__ based class.'

# Setting up
setup(
    name="object_repr",
    version=VERSION,
    author="Idan Kalderon",
    author_email="<idan.kalderon@earnix.com>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
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
