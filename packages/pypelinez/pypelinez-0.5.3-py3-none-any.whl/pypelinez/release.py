import click
import pypelinez.git as git


# -------------------------- commands

# group
@click.group()
def release():
    pass


# start
@release.command()
def start():
    """Creates a new release branch"""

    if git.current_branch() == "develop":
        git.create_branch("release")
    else:
        print("Must create release from develop branch")


# set version
@release.command()
@click.argument("version")
def set(version):
    """Creates a tag for the release"""

    if git.current_branch() == "release":
        git.tag(version)
    else:
        print("Must set version on release branch")


# submit version
@release.command()
@click.argument("version")
def submit(version):
    """Submits the release as a merge request"""

    if git.current_branch() == "release":
        git.release_request(version)
    else:
        print("Must set version on release branch")
