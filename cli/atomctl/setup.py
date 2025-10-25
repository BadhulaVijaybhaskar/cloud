from setuptools import setup, find_packages

setup(
    name="atomctl",
    version="1.0.0",
    description="ATOM Cloud CLI - Manage workflow packages (WPKs)",
    author="ATOM DevOps Team",
    author_email="devops@atom.cloud",
    packages=find_packages(),
    py_modules=["main"],
    install_requires=[
        "click>=8.1.0",
        "pyyaml>=6.0.0",
        "requests>=2.31.0",
    ],
    entry_points={
        "console_scripts": [
            "atomctl=main:atomctl",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
)