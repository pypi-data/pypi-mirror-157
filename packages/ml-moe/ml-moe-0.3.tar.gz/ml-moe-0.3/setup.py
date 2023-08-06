import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


def parse_dependency(filepath):
    return [
        dependency
        for dependency in open(filepath).read().splitlines()
        if "==" in dependency
    ]


base_requirements = parse_dependency("requirements/base.txt")
dev_requirements = parse_dependency("requirements/dev.txt")

setuptools.setup(
    name="ml-moe",
    version="0.3",
    author="Shagun Sodhani",
    author_email="sshagunsodhani@gmail.com",
    description="Mixture of Experts",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    install_requires=base_requirements,
    url="https://github.com/shagunsodhani/moe",
    packages=setuptools.find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests", "docs", "docsrc"]
    ),
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    extras_require={
        # Install development dependencies with
        # pip install -e .[dev]
        "dev": dev_requirements,
    },
)
