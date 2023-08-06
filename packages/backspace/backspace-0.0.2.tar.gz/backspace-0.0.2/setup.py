import setuptools

with open("README.md", "r",encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="backspace",
    version="0.0.2",
    author="lengqie",
    author_email="lengqie@foxmail.com",
    description="backspace formatting tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lengqie/backspace-python.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
