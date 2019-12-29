import configparser
from github import Github

# GitHub Setup
token = configparser.ConfigParser()
token.read("token.cfg")
g = Github(token["GIT"]["secret"])

# Select Majam Repo:
majam_repo = g.get_repo("Arthurdw/Majam")


def version():
    """Get the current version (github)"""
    github_version = majam_repo.get_commits().totalCount
    return f"v {str(github_version)[:0] or '0'}.{str(github_version)[:1] or '0'}.{str(github_version)[1:] or '0'}"
