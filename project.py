"""
project.py
----------

Project management script

This file provides implementations for:

    - Semantic versioning from git tags;

    - Project file parser;

    - Integration with setuptools/distutils;

    - Tools for CI/CD;

When executed from command line, this script will try, by default, to
increase the current version based on the last commit message.  If a
flag is passed to the script, it will only echo information to stdout.
"""
from __future__ import print_function, unicode_literals

import logging
import os
import subprocess
from enum import Enum
from re import match

BASE_VERSION = None
COMMIT_COUNT = None

logger = logging.getLogger(__name__)


def shell_output(cmd):
    """Execute a shell command and return it's output."""
    return subprocess.check_output(cmd.split()).decode().strip()


def get_base_version():
    """Get base version from repository.

    Tags must follow the pattern: MAJOR.MINOR.PATCH
    """
    if BASE_VERSION is None:
        return shell_output('git describe --tags --abbrev=0')
    return BASE_VERSION


def get_commit_count():
    """Get commit count since last tag."""
    if COMMIT_COUNT is None:
        return shell_output('git rev-list {base_version}..HEAD --count'
                            .format(base_version=get_base_version()))
    return COMMIT_COUNT


def get_commit_message():
    """Get last commit message."""
    return shell_output('git log HEAD -1 --pretty=%B')


def get_increased_base_version(index):
    base_version = [int(v) for v in get_base_version().split('.')]
    base_version[index] += 1
    for i in range(index+1, 3):
        base_version[i] = 0
    return '.'.join([str(v) for v in base_version])


def log_history_predicate_factory(prefix):
    """Build a function that check for ``prefix`` on log history
    collection with the following regex: ^{prefix}(\\(\\w+\\))?:

    When any of log messages contains ``prefix``, the predicate
    function returns True.  Otherwise the function will always return
    False.
    """
    def log_history_checker(log_history):
        for log_message in log_history:
            if bool(match('^{prefix}(\\(\\w+\\))?:'
                          .format(prefix=prefix), log_message)):
                return True
        return False
    return log_history_checker


(has_breaking_changes,
 has_features,
 has_fixes) = [log_history_predicate_factory(key)
               for key in ['BREAKING CHANGE',
                           'feat',
                           'fix']]


def get_log_history(from_version=None):
    cmd = 'git log --pretty=format:%s'
    if from_version is not None:
        cmd = 'git log {from_version}..HEAD --pretty=format:%s'\
            .format(from_version=from_version)
    return shell_output(cmd).splitlines()


def get_rolling_log_history():
    """Get rolling log history, i.e. the log history since last added
    tag.
    """
    current_tag = get_current_tag()
    return get_log_history(current_tag)


def get_increased_version():
    """Accordingly to log history, increase the current version
    """
    logs = get_rolling_log_history()

    if has_breaking_changes(logs):
        return get_increased_base_version(0)
    if has_features(logs):
        return get_increased_base_version(1)
    if has_fixes(logs):
        return get_increased_base_version(2)


def bump_version():
    """Bump version"""
    version = get_increased_version()

    if version is not None:
        subprocess.call(['git', 'tag', '-a', version,
                         '-m', 'Release ' + version])
    else:
        message = ('Error ~ Cannot bump version.\n' +
                   'Check if log history contains convetional commits...')
        raise Exception(message)


def get_version(ignore_dirty=False):
    base_version = get_base_version()
    commit_count = get_commit_count()
    if commit_count == "0" or ignore_dirty:
        return base_version
    return base_version + '-unstable' + commit_count.zfill(4)


def get_change_log():
    """Get CHANGELOG.md"""
    logs = get_rolling_log_history()

    def filter_type(prefix):
        def func(log):
            return bool(match('^{prefix}(\\(\\w+\\))?:'
                              .format(prefix=prefix), log))
        return func

    breaks = list(filter(filter_type('BREAKING CHANGES'), logs))
    feats = list(filter(filter_type('feat'), logs))
    fixes = list(filter(filter_type('fix'), logs))

    change_log = []
    change_log.append('Version {version} changelog'
                      .format(version=get_increased_version()))
    change_log.append('')

    if len(breaks):
        change_log.append('## Breaking Changes')
        for log in breaks:
            message = log.split(':')[1]
            change_log.append('  - {message}'
                              .format(message=message.strip()))
        change_log.append('')

    if len(feats):
        change_log.append('## Features')
        for log in feats:
            message = log.split(':')[1]
            change_log.append('  - {message}'
                              .format(message=message.strip()))
        change_log.append('')

    if len(fixes):
        change_log.append('## Fixes')
        for log in fixes:
            message = log.split(':')[1]
            change_log.append('  - {message}'
                              .format(message=message.strip()))
        change_log.append('')

    return change_log


def get_current_tag():
    """Get current tag"""
    return get_version(ignore_dirty=True)


def get_requirements():
    """Get project requirements"""
    with open('requirements.txt') as fp:
        requirements = fp.read()
    return requirements.split()


def get_project_config():
    """Get project config file"""
    if get_project_config.CONFIG is None:
        import json
        with open('project.json') as fp:
            get_project_config.CONFIG = json.load(fp)
    return get_project_config.CONFIG


get_project_config.CONFIG = None


def try_get_project_property(prop_name):
    project = get_project_config()
    prop = project.get(prop_name)
    if prop is None:
        raise ValueError('`%s` must be defined' % prop_name)
    return prop


def get_description():
    """Get project description"""
    return try_get_project_property('description')


def get_project_name():
    """Get project name"""
    return try_get_project_property('projectName')


def get_package_name():
    """Get package name from project.json"""
    return try_get_project_property('packageName')


def get_package_path():
    """Get package path from package_name"""
    package_name = get_package_name()
    return package_name.replace('.', '/')


def release_branch():
    increased_version = get_increased_version()
    if increased_version is None:
        raise Exception("There is no need to build a release at this point")
    release_branch = "release/" + increased_version
    current_branch = subprocess.check_output(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"])\
        .decode().splitlines()[0]

    print('Preparing {branch} ...'.format(branch=release_branch))
    subprocess.check_call(
        ["git", "checkout", "-b", release_branch])
    subprocess.check_call(
        ["git", "push", "-u", "origin", release_branch])
    subprocess.check_call(
        ["git", "checkout", current_branch])
    subprocess.check_call(
        ["git", "branch", "-d", release_branch])
    print('Done ...')


def get_cmdclass():
    from setuptools.command.build_py import build_py
    from setuptools.command.sdist import sdist

    class cmd_build_py(build_py):
        def run(self):
            build_py.run(self)
            target = os.path.join(self.build_lib,
                                  get_package_path(),
                                  '_version.py')
            update_version_file(target)

    class cmd_sdist(sdist):
        def run(self):
            self.distribution.metadata.version = get_version()
            return sdist.run(self)

        def make_release_tree(self, base_dir, files):

            sdist.make_release_tree(self, base_dir, files)
            target = os.path.join(base_dir,
                                  'src',
                                  get_package_path(),
                                  '_version.py')
            update_version_file(target)
            update_installer(base_dir)

    return {'build_py': cmd_build_py,
            'sdist': cmd_sdist}


def update_version_file(vfile_path):
    template = '''"""
Autogenerated versioning file

This file was automagically produced and SHOULD NOT be modified.
"""

def get_version():
    return '{VERSION}'
'''
    with open(vfile_path, 'w') as fp:
        fp.write(template.format(VERSION=get_version()))


def update_installer(base_dir):
    vpath = os.path.join(base_dir, 'project.py')
    with open(vpath) as fp:
        original = fp.read()

    base_version = get_base_version()
    commit_count = get_commit_count()
    updated = original\
        .replace("BASE_VERSION = None",
                 "BASE_VERSION = '%s'" % base_version)\
        .replace("COMMIT_COUNT = None",
                 "COMMIT_COUNT = '%s'" % commit_count)

    with open(vpath, 'w') as fp:
        fp.write(updated)


class ENV(Enum):
    DEVELOPMENT = "dev"
    STAGE = "stage"
    PRODUCTION = "prod"


def map_environment(env):
    """Map environment cases to a single enum."""
    if env in {'dev', 'develop', 'development'}:
        return 'dev'
    if env in {'prod', 'production'}:
        return 'prod'
    return env


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('env',
                        nargs='?', default='dev',
                        help="environment name (required for versioning)")

    parser.add_argument('--change-log', '-cl',
                        action='store_true',
                        help="print CHANGELOG.md")

    parser.add_argument('--version', '-v',
                        action='store_true',
                        help="print project version to stdout")

    parser.add_argument('--release', '-r',
                        action='store_true',
                        help="make a new release from development branch")

    parser.add_argument('--no-dirty', '-nd',
                        action='store_true',
                        help=("ignore `unstable` suffix when " +
                              "printing dirty version"))

    parser.add_argument('--increased-version', '-iv',
                        action='store_true',
                        help="print increased version")

    parser.add_argument('--needs-build', '-nb',
                        action='store_true',
                        help="predicate to check if project needs build")

    parser.add_argument('--bump', '-b',
                        action='store_true',
                        help=("bump version based on convetional " +
                              "commits since last tag"))

    parser.add_argument('--project-name',
                        '-Pn',
                        action='store_true',
                        help="print project name to stdout")

    parser.add_argument('--package-name',
                        '-pn',
                        action='store_true',
                        help="print package name to stdout")

    parser.add_argument('--package-path',
                        '-pp',
                        action='store_true',
                        help="print package path to stdout")

    parser.add_argument('--lambda-function-name',
                        '-lfn',
                        action='store_true',
                        help="print lambda function name to stdout")

    parser.add_argument('--lambda-layer-name',
                        '-lln',
                        action='store_true',
                        help="print lambda layer name to stdout")

    parser.add_argument('--on-venv',
                        action='store_true',
                        help="check if on venv")

    parser.add_argument('--is-a',
                        help="check if project.json is a `deploymentType`")

    args = parser.parse_args()

    if args.project_name:
        print(get_project_name())
        exit(0)

    if args.package_name:
        print(get_package_name())
        exit(0)

    if args.package_path:
        print(get_package_path())
        exit(0)

    if args.lambda_function_name:
        print(get_project_name().replace('.', '_'))
        exit(0)

    if args.lambda_layer_name:
        print(get_project_name().replace('.', '-'))
        exit(0)

    if args.on_venv:
        on_venv = bool(os.getenv('VIRTUAL_ENV'))
        print(on_venv)
        exit(0)

    if args.is_a is not None:
        types = try_get_project_property('deploymentTypes')
        is_a = args.is_a in types
        print(is_a)
        exit(0)

    try:
        env = ENV(map_environment(args.env))
    except ValueError as ex:
        print('Error ~', ex)
        exit(1)

    if args.version:
        print(get_version(args.no_dirty))
        exit(0)

    if args.bump:
        bump_version()
        exit(0)

    if args.increased_version:
        print(get_increased_version())
        exit(0)

    if args.needs_build:
        print(bool(get_increased_version()))
        exit(0)

    if args.change_log:
        change_log = get_change_log()
        for line in change_log:
            print(line)
        exit(0)

    if args.release:
        try:
            release_branch()
        except Exception as ex:
            print(ex)
        finally:
            exit(0)

    print(get_version())
