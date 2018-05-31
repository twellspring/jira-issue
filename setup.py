import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="jira-issue",
    version="0.0.4",
    author="Todd Wells",
    author_email="todd@wells.ws",
    description="Quickly create jira issues from the command line",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/twellspring/jira-issue",
    install_requires=['jira', 'python-editor>=1.0.3'],
    packages=setuptools.find_packages(),
    scripts=['bin/jira-issue'],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ),
)
