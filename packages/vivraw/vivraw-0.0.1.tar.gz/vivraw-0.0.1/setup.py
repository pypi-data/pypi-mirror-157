import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

install_requires = open("requirements.txt", "r").readlines()

setuptools.setup(
    name="vivraw",
    version="0.0.1",
    author="Thomas Meacham",
    author_email="thomas.meacham@vivent.ch",
    description="Common module to interact with raw files created on the Vivent PSR devices",
    install_requires=install_requires,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vivent-sarl/vivraw",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
