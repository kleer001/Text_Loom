from setuptools import setup, find_packages

setup(
    name="TEXT_LOOM",
    version="0.0.1",
    author="Clear Menser",
    author_email="kleer001code@gmail.com",
    description="A terminal-based node editor for text manipulation",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/kleer001/Text_Loom",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "textual>=0.52.1",
        "bandit>=1.7.5",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    python_requires=">=3.8",
    include_package_data=True,
    package_data={
        "TUI": ["themes/*"],
    },
)