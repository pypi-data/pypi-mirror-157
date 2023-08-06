# Github SDK

## Goal
Github SDK is a big topic. 
A use case to focus on will narrow the API calls substantially for a 3 hours technical exercise include: 
* Coding
* Deploy
* README
* Packaging
* Formatting

My goal is to have an SDK that is complete enough to solve a real world problem. A research topic like this does not use any authenticated calls, and does not create/modify/delete any resources. With my Data Science background, I have a lot of experience with data gathering projects and clearly understand the requirements.

## Use Case: 
Analyze use of Vulnerability Alerts Feature in Github Ecosystem

* By Repo Language
* By Repo Popularity (Stars / Forks)
* By Owner Experience ( # of commits, # of repos, # of repos the user contributes to)
* By Owner Network Importance (# of followers vs # of people the user follows)
  

### API Endpoints:
* User
  * Followers
    * List followers of a user
    * List the people a user follows

* Repositories
  * Repositories
    * Get a repository
    * List repository contributors
    * List repositories for a user
    * ~~Get all repository topics~~ 
    * List repository languages
    * ~~Check if vulnerability alerts are enabled for a repository~~
  * Contents
    * Get a repository README


## Status
Vulnerability Status endpoints are only available for repos the authenticated user owns. It wasn't possible to finish the original task, but the SDK could still be used for other network analysis problems about users, repos, and languages.

## Using this Repository

### Install dependencies for test/development
> pip install -r requirements.txt
> pip install -e . 

### Formatting
> black src
> 
> black tests

### Run Tests
> pytest tests

### Package
> python setup.py sdist

### Deploy
> twine upload dist/*

### Skipped Because of Time
* pre-commit hooks for black and maybe tests