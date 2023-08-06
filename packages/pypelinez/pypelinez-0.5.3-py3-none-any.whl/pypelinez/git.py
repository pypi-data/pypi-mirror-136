import pypelines.utilities as utilities


def current_branch():
    """Current git branch name

    Returns:
    str:Returning current git branch name

    """

    result = utilities.action("git rev-parse --abbrev-ref HEAD")
    utilities.assert_result(result)
    return utilities.transform_result(result)


def create_branch(name):
    result = utilities.action("git checkout -b " + name)
    utilities.print_result(result)
    utilities.assert_result(result)


def change_to_branch(name):
    result = utilities.action("git checkout " + name)
    utilities.print_result(result)
    utilities.assert_result(result)


def add():
    result = utilities.action("git add -A")
    utilities.print_result(result)
    utilities.assert_result(result)


def commit():
    result = utilities.action("git commit -F COMMIT.md")
    utilities.print_result(result)
    utilities.assert_result(result)


def merge(branch):
    result = utilities.action("git merge --squash " + branch)
    utilities.print_result(result)
    utilities.assert_result(result)


def delete(branch):
    result = utilities.action("git branch -D " + branch)
    utilities.print_result(result)
    utilities.assert_result(result)


def pull(source, branch):
    result = utilities.action("git pull " + source + " " + branch)
    utilities.print_result(result)
    utilities.assert_result(result)


# merge request
# https://docs.gitlab.com/ee/user/project/merge_requests/merge_when_pipeline_succeeds.html
def merge_request(target):
    feature_branch = current_branch()
    merge_request_file = open("MERGE_REQUEST.md", "r")
    merge_description = merge_request_file.read()
    merge_request_file.close()

    request = """\
    git push \\
    -o merge_request.create \\
    -o merge_request.target={target} \\
    -o merge_request.merge_when_pipeline_succeeds \\
    -o merge_request.remove_source_branch \\
    -o merge_request.title=\"Merge request for {branch}\" \\
    -o merge_request.description=\"{description}\" \\
    origin {branch}
  """.format(
        target=target, branch=feature_branch, description=merge_description
    )

    result = utilities.action(request)
    utilities.print_result(result)
    utilities.assert_result(result)


# merge request
# https://docs.gitlab.com/ee/user/project/merge_requests/merge_when_pipeline_succeeds.html
def release_request(version):

    branch = current_branch()

    request = """\
    git push \\
    -o merge_request.create \\
    -o merge_request.target=main \\
    -o merge_request.merge_when_pipeline_succeeds \\
    -o merge_request.remove_source_branch \\
    -o merge_request.title=\"Merge request for Release {version}\" \\
    -o merge_request.description=\"Release {version}\" \\
    origin {branch}
  """.format(
        version=version, branch=branch
    )

    result = utilities.action(request)
    utilities.print_result(result)
    utilities.assert_result(result)


def tag(version):
    result = utilities.action("git tag -a " + version + " -m " + version)
    utilities.print_result(result)
    utilities.assert_result(result)
