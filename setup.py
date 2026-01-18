"""
Setup configuration for Salah Prayer API.
"""

from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="salah-prayer-api",
    version="3.2.0",
    author="Salah Prayer API Team",
    description="Professional Prayer Times API for iPhone apps",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/salah-prayer-api",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Religion",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest",
            "black",
            "flake8",
            "mypy"
        ],
        "redis": ["redis>=5.0.0"],
        "postgres": ["asyncpg>=0.27.0", "sqlalchemy>=2.0.0"]
    },
    entry_points={
        "console_scripts": [
            "salah-api=app.main:main",
        ],
    },
)
