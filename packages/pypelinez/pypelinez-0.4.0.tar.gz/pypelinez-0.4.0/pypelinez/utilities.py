import os
import subprocess
import sys
import shutil

current = os.getcwd()

# -------------------------- utilities


def action(command, cwd=current):
    return subprocess.run(command, cwd=cwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def assert_result(result):
    if result.returncode != 0:
        sys.exit(result.returncode)


def transform_result(result):
    # https://stackoverflow.com/questions/41918836/how-do-i-get-rid-of-the-b-prefix-in-a-string-in-python
    return (result.stdout.decode("UTF-8") + result.stderr.decode("UTF-8")).strip()


def print_result(result):
    print(transform_result(result))


def remove_directory(directory):
    shutil.rmtree(directory)
