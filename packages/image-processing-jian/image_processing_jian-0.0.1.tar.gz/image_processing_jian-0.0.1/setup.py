from setuptools import setup, find_packages

with open("README.md", "r") as f:
    page_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="image_processing_jian",
    version="0.0.1",
    author="Jian Goersch",
    author_email="jian.goersch@gmail.com",
    description="Image Processing Package using Skimage ",
    long_description=page_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JianGoersch/image_processing_jian",
    packages=find_packages(),
    install_requires=requirements,
    python_requires='>=3.8',
)