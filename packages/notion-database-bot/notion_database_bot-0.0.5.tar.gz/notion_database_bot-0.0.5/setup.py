from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="notion_database_bot",
    version="0.0.5",
    author="Oliver Liu",
    author_email="zhliu0106@gmail.com",
    description="A package for synchronizing data in Notion Database through Notion official api.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zhliu0106/Notion-Database-Bot",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
