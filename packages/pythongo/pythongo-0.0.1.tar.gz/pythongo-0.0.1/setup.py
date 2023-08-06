from setuptools import setup, find_packages

with open("README.md", "r") as f:
    desc = f.read()

setup(
    name="pythongo",
    version="0.0.1",
    description="Minimal MongoDB OOP client based on motor package.",
    long_description=desc,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/aiocat/pythongo",
    author="aiocat",
    author_email="",
    license="MIT",
    project_urls={
        "Bug Tracker": "https://gitlab.com/aiocat/pythongo/-/issues",
    },
    classifiers=[
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3"
    ],
    keywords=["mongodb", "oop", "motor"],
    packages=find_packages(),
    python_requires=">=3.6.0",
    install_requires=["motor"]
)
