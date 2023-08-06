from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'Pytest tools'
LONG_DESCRIPTION = 'Verifies that no exception is raised'

setup(
        name="pytest_tools",
        version=VERSION,
        author="José Luis Lloret",
        author_email="<l1oret@outlook.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=['pytest'],
        keywords=['python', 'pytest'],
        classifiers= [
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "Framework :: Pytest",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 3",
            "Topic :: Software Development :: Testing",
        ]
)