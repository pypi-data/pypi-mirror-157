from typing import List, Dict
import requests


def rate_limited_get(*args, **kwargs):
    requests.get(*args, **kwargs)


def get_paginated_results(url, headers=None, params=None):
    """Gets paginated results from a Github API Endpoint (JSON only)"""
    # Default to max page size for most endpoints
    if params is None:
        params = {"per_page": "100"}

    # Default to most common accept header
    if headers is None:
        headers = {"Accept": "application/vnd.github+json"}

    results = []
    resp = requests.get(url, headers=headers, params=params)
    results.extend(resp.json())

    while resp.links.get("next"):
        url = resp.links["next"]["url"]
        resp = requests.get(url, params=params)
        results.extend(resp.json())

    return results


def get_user(username: str):
    return requests.get(
        f"https://api.github.com/users/{username}",
        headers={"Accept": "application/vnd.github+json"},
    ).json()


def get_followers(username: str, **kwargs) -> List[Dict]:
    """Gets all followers for provided user"""
    return get_paginated_results(
        f"https://api.github.com/users/{username}/followers",
        **kwargs,
    )


def get_following(username: str, **kwargs) -> List[Dict]:
    """Gets all users who follow the provided user"""
    return get_paginated_results(
        f"https://api.github.com/users/{username}/following",
        **kwargs,
    )


def get_repos(username: str, **kwargs) -> List[Dict]:
    """Gets all public repos the provided user owns"""
    return get_paginated_results(
        f"https://api.github.com/users/{username}/repos",
        **kwargs,
    )


def get_contributors(username: str, repo: str, **kwargs) -> List[Dict]:
    return get_paginated_results(
        f"https://api.github.com/repos/{username}/{repo}/contributors", **kwargs
    )


def get_languages(username: str, repo: str, **kwargs) -> List[str]:
    return requests.get(
        f"https://api.github.com/repos/{username}/{repo}/languages", **kwargs
    ).json()


print(get_contributors("foo", "algorithmic-networks"))
print(get_languages("foo", "algorithmic-networks"))
print(get_repos("foo"))
