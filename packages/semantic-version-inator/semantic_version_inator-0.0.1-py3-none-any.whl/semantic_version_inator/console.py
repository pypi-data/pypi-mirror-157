""" console entry point script """


import sys
from semantic_version_inator import next_semantic_version


def get_next_ver_file_name(): #pragma: no cover
    """
    console entry point script to call next_semantic_version.get_next_version_given_file_name
    requires a file name (string) and release type (string) with value of PATCH, MINOR or MAJOR
    parse semantic version from python package file name i.e:  pkg_name-0.0.0-py3-none-any.whl
    prints next semantic version based on inputs, or 'None' type if an error occurs
    """
    if len(sys.argv) != 3:
        raise ValueError("file name and release type values required")

    ver = next_semantic_version.get_next_version_given_file_name(sys.argv[1], sys.argv[2])
    print(ver)


def get_next_ver(): #pragma: no cover
    """
    console entry point script to call next_semantic_version.get_next_version_given_file_name
    requires version number (string) and release type (string) with value of PATCH, MINOR or MAJOR
    parse semantic version from semantic existing version string, i.e.:  0.0.0
    prints next semantic version based on inputs, or 'None' type if an error occurs
    """
    if len(sys.argv) != 3:
        raise ValueError("version number and release type values required")

    ver = next_semantic_version.get_version_given_existing_version(sys.argv[1], sys.argv[2])
    print(ver)
