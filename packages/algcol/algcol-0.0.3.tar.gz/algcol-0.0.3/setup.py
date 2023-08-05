import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="algcol",
    version="0.0.3",
    author="Remy Duijsens",
    author_email="remyduijsens@gmail.com",
    description="A library of common algorithms",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/remyd95/Algcol",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)