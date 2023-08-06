""" This module generates next sematic version based on current version and release type """


def get_cur_version_from_file_name(file_name):
    """
    parse and return semantic version from python package file name, or 'None' type if error
    expected format surrounds semantic version with dashes, i.e:  pkg_name-0.0.0-py3-none-any.whl
    """
    cur_ver = None
    try:
        file_name_split = file_name.rsplit("-")
        cur_ver = file_name_split[1]
    except Exception as exc:
        raise ValueError("unable to get current version from file name:", file_name) from exc
    return cur_ver


def get_version_given_existing_version(cur_ver, release_type):
    """ return the next semantic version based on current version and release type """
    major = None
    minor = None
    patch = None
    try:
        cur_ver_split = cur_ver.rsplit(".")
        major = int(cur_ver_split[0])
        minor = int(cur_ver_split[1])
        patch = int(cur_ver_split[2])
    except Exception as exc:
        raise ValueError("unable to parse current version as provided:", cur_ver) from exc
    new_ver = None
    if release_type == "MAJOR": # reset patch and minor, increment major
        new_patch = 0
        new_minor = 0
        new_major = major+1
        new_ver = str(new_major)+"."+str(new_minor)+"."+str(new_patch)
    elif release_type == "MINOR": # reset patch, increment minor, use existing major
        new_patch = 0
        new_minor = minor+1
        new_ver = str(major)+"."+str(new_minor)+"."+str(new_patch)
    elif release_type == "PATCH": # increment patch, use existing minor and major
        new_patch = patch+1
        new_ver = str(major)+"."+str(minor)+"."+str(new_patch)
    else:
        raise ValueError("unknown release type, please use PATCH, MINOR or MAJOR")
    return new_ver


def get_next_version_given_file_name(file_name, release_type):
    """ get the current version from file name, then determine next version for release type """
    cur_ver = get_cur_version_from_file_name(file_name)
    new_ver = get_version_given_existing_version(cur_ver, release_type)
    return new_ver
