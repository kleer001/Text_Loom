from setuptools import setup, find_packages

setup(
    name="TEXT_LOOM",
    version="0.0.1",
    author="Clear Menser",
    author_email="kleer001code@gmail.com",
    description="A node based text, queery, and results editor",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/kleer001/Text_Loom",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        # List your package dependencies here
        "numpy>=1.18.0",
        "pandas>=1.0.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12.3",
    ],
    python_requires=">=3.12",
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.10",
            "flake8>=3.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "your-command=your_package.module:main_function",
        ],
    },
)
