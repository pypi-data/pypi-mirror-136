import click
import pypelines.utilities as utilities


def git_branch_name():
    """Current git branch name

    Returns:
    str:Returning current git branch name

    """

    result = utilities.action("git rev-parse --abbrev-ref HEAD")
    utilities.assert_result(result)
    return utilities.transform_result(result)


# -------------------------- commands

# group
@click.group()
def feature():
    pass


# name
@feature.command()
def name():
    print(git_branch_name())


# start
@feature.command()
@click.argument("name")
def start(name):
    """Creates a new branch with the format feature/<name>


    Parameters:
    name (str): feature branch name

    """

    result = utilities.action("git checkout -b feature/" + name)
    utilities.print_result(result)
    utilities.assert_result(result)


# commit
@feature.command()
def add_commit():
    result = utilities.action("git add -A")
    utilities.print_result(result)
    utilities.assert_result(result)

    result = utilities.action("git commit -F COMMIT.md")
    utilities.print_result(result)
    utilities.assert_result(result)


# finish
@feature.command()
def finish():
    branch = git_branch_name()

    result = utilities.action("git checkout main")
    utilities.print_result(result)
    utilities.assert_result(result)

    result = utilities.action("git merge --squash " + branch)
    utilities.print_result(result)
    utilities.assert_result(result)

    result = utilities.action("git branch -D " + branch)
    utilities.print_result(result)
    utilities.assert_result(result)

    result = utilities.action("git pull origin main")
    utilities.print_result(result)
    utilities.assert_result(result)


# merge request
# https://docs.gitlab.com/ee/user/project/merge_requests/merge_when_pipeline_succeeds.html
@feature.command()
def merge_request():
    feature_branch = git_branch_name()
    merge_request_file = open("MERGE_REQUEST.md", "r")
    merge_description = merge_request_file.read()
    merge_request_file.close()

    request = """\
    git push \\
    -o merge_request.create \\
    -o merge_request.target=main \\
    -o merge_request.merge_when_pipeline_succeeds \\
    -o merge_request.remove_source_branch \\
    -o merge_request.title=\"Merge request for {branch}\" \\
    -o merge_request.description=\"{description}\" \\
    origin {branch}
  """.format(
        branch=feature_branch, description=merge_description
    )

    result = utilities.action(request)
    utilities.print_result(result)
    utilities.assert_result(result)
