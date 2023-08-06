from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Read long description from the readme.md file
with open("README.md") as f:
    readme = f.read()

with open("LICENSE") as f:
    license = f.read()

setup(
    name="investani",
    version="0.0.1",
    description="A package that expected to help people analyze the company for investment.",
    long_description_content_type="text/markdown",
    long_description=readme,
    author="Nopporn Phantawee",
    author_email="n.phantawee@gmail.com",
    url="https://github.com/noppGithub/investani",
    license="MIT",
    packages=find_packages(exclude=("tests", "docs")),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
    ],
    install_requires=[
        "bs4==0.0.1",
        "pandas>=1.1.0",
        "PyYAML>=6.0",
        "requests>=2.20.1",
        "scikit-learn>=1.0.0",
    ],
    extras_require={
        "dev": ["check-manifest"],
        "test": ["coverage"],
    },
    python_requires=">=3.6, <4",
)
