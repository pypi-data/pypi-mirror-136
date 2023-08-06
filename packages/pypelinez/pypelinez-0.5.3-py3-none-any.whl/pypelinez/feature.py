import click
import pypelinez.git as git


# -------------------------- commands

# group
@click.group()
def feature():
    pass


# name
@feature.command()
def name():
    print(git.current_branch())


# start
@feature.command()
@click.argument("name")
def start(name):
    """Creates a new branch with the format feature/<name>


    Parameters:
    name (str): feature branch name

    """

    if git.current_branch() == "develop":
        git.create_branch("feature/" + name)
    else:
        print("Must create feature from develop branch")


# commit
@feature.command()
def add_commit():

    git.add()

    git.commit()


# finish
@feature.command()
def finish():
    branch = git.current_branch()

    git.change_to_branch("develop")

    git.merge(branch)

    git.delete(branch)

    git.pull("origin", "develop")


@feature.command()
def request_merge():
    git.merge_request("develop")
