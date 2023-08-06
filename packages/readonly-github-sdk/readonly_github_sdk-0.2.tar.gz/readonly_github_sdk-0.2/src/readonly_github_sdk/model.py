from collections import Counter
from functools import cached_property
from typing import List
from attrs import define
from src.readonly_github_sdk.endpoints import (
    get_following,
    get_followers,
    get_contributors,
    get_languages,
    get_repos,
)


@define(slots=False)
class User:
    username: str

    @cached_property
    def followers(self) -> List["User"]:
        followers = []
        for user_dict in get_followers(self.username):
            followers.append(User(user_dict["login"]))
        return followers

    @cached_property
    def following(self) -> List["User"]:
        following = []
        for user_dict in get_following(self.username):
            following.append(User(user_dict["login"]))
        return following

    @cached_property
    def repos(self):
        repos = []
        for repo_dict in get_repos(self.username):
            print(f"{repo_dict=}")
            repos.append(Repo(self, repo_dict["name"]))
        return repos


@define(slots=False)
class Repo:
    owner: User
    name: str

    @cached_property
    def contributors(self):
        contributors = []
        for user_dict in get_contributors(self.owner.username, self.name):
            contributors.append(User(user_dict["login"]))
        return contributors

    @cached_property
    def languages(self):
        return get_languages(self.owner.username, self.name)
