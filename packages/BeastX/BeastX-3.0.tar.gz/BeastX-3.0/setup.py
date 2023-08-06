import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
fh.close()

setuptools.setup(
    name="BeastX",
    version="3.0",
    author="@Godmrunal",
    author_email="mrunalgaming7@gmail.com",
    description="A Python Package ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/msy1717",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
