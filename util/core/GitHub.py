import configparser
from github import Github

# GitHub Setup
token = configparser.ConfigParser()
token.read("token.cfg")
g = Github(token["GIT"]["secret"])

# Select Majam Repo:
alexi_repo = g.get_repo("Arthurdw/Majam")


def version():
    """Get the current version (github)"""
    github_version = 0
    for _ in alexi_repo.get_commits():
        github_version += 1
    _version = str(github_version/1000).replace(".", "")
    return f"v {_version[:1]}.{_version[1:-2]}.{_version[2:]}"
