from setuptools import setup, find_packages

setup(
    name="sculblog",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "markdown",
        "beautifulsoup4",
        "sqlite3",  # Note: sqlite3 is built into Python, you don't need to list it here
    ],
    entry_points={
        "console_scripts": [
            "sculblog=sculblog.main:main",  # Changed from cli:main to main:main
        ],
    },
    author="Diego Cabello",
    description="Super Cool Utility Lightweight Blog - A minimalist blogging framework",
    python_requires=">=3.6",
)
