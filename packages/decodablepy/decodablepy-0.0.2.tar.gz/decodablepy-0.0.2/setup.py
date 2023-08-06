from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

requirements = ["requests>=2"]

setup(
    name="decodablepy",
    version="0.0.2",
    author="Hubert Dulay",
    author_email="hubert.dulay@gmail.com",
    description="a client for decodable.co",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/hdulay/decodablepy/",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: Apache Software License",
    ],
)