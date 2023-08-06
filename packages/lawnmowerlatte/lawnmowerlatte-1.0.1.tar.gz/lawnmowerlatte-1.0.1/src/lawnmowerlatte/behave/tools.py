import json
import re
import logging as log
from pprint import pformat
from nose.tools import assert_in
from sarge import capture_both as sarge_capture_both

import semver


def breakpoint():
    """Python debug breakpoint."""

    from code import InteractiveConsole
    from inspect import currentframe

    caller = currentframe().f_back

    def pprint(*args, **kwargs):
        log.critical(pformat(*args, **kwargs))

    env = {}
    env.update(caller.f_globals)
    env.update(caller.f_locals)
    env["pprint"] = pprint
    env["print"] = log.critical

    shell = InteractiveConsole(env)
    shell.interact(
        "* Break: {} ::: Line {}\n"
        "* Continue with Ctrl+D...".format(caller.f_code.co_filename, caller.f_lineno)
    )


def load_file(filename):
    with open(filename, "r") as f:
        data = f.read()
    return data


def load_json(json_file):
    data = load_file(json_file)
    json_data = json.loads(data)

    return json_data


def store_json(data, file):
    with open(file, "w") as f:
        json.dump(data, f, sort_keys=True, indent=4, separators=(",", ": "))


def get_setting_from_dict(settings, keyword):
    assert_in(keyword, list(settings.keys()) + list(settings.values()))
    if keyword in settings.keys():
        setting = settings[keyword]
    else:
        setting = keyword
    return setting


def random_hex(length=1):
    import string
    import random

    string.printable = "0123456789abcdef"
    hex = ""
    for i in range(0, length):
        hex += random.choice(string.printable)

    return hex


def send_ipmi_chassis(host, user, password, command):
    ipmi_cmd = "ipmitool -I lanplus -U {} -P {} -H {} chassis {}".format(
        user, password, host, command
    )
    ipmi_return = capture_both(ipmi_cmd)
    return ipmi_return


def dict_merge(a, b):
    # Merge dict B into dict A, overwriting at the most specific level only
    # Special note that lists are not merged, they are replaced
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                dict_merge(a[key], b[key])
            elif a[key] == b[key]:
                # Same leaf value, do nothing
                pass
            else:
                # Value is different, overwrite with b
                a[key] = b[key]
        else:
            a[key] = b[key]
    return a


def price_is_right(version, version_list):
    version_list.sort(key=lambda s: [int(u) for u in s.split(".")])
    log.debug(f"Versions found: {version_list}")
    effective_version = version
    log.debug(f"Setting effective version to: {effective_version}")
    if effective_version not in version_list:
        log.debug(
            f"This version was not found in the version list, looking for suitable version (Price is Right rules)"
        )
        for version_item in version_list:
            if semver.compare(version, version_item) > 0:
                log.debug(f"Found a possible version: {version_item}")
                effective_version = version_item
    log.debug(f"Final effective version: {effective_version}")
    return effective_version


def detect_compose_container_name(full_container):
    """
    Returns the container name without numbering or unique slugs
    :param full_container: Full detected container name
    :return: Short name of container
    """

    container = full_container
    log.debug(f"Detecting compose container name: {container}")

    # Detect slugs introduced in docker-compose 1.23.0
    parts = container.rsplit("_", 1)

    if len(parts) == 1:
        log.debug(
            f"Container name does not appear to be created by docker-compose: ${container}"
        )
        return None

    tail = parts[1]

    if re.match("[0-9a-fA-F]{12}", tail):
        container = container.rsplit("_", 1)[0]

    # Detect trailing numbering
    parts = container.rsplit("_", 1)
    tail = parts[1]

    if re.match("[0-9]+", tail):
        if tail != "1":
            log.warning(
                "docker-compose container with number other than 1 detected, this information will be discarded"
            )

        container = container.rsplit("_", 1)[0]

    # Detect leading 'compose'
    parts = full_container.split("_", 1)
    head = parts[0]

    if head == "compose":
        container = parts[1]

    return container


def load_data(context):
    if context.table is not None:
        data = context.table
    else:
        data = context.setup_data
    return data


def vardump(expression):
    import sys

    frame = sys._getframe(1)
    output = f"{expression} = {repr(eval(expression, frame.f_globals, frame.f_locals))}"
    log.debug(output)
    # return output


def exec(command, error_string=None, allow_failure=False, verbose=False):
    error_string = error_string or "Command failed"
    human_readable = " ".join(command)

    log.debug(f"Running command: {human_readable}")

    output = capture_both(command)

    try:
        return_code = output.returncode
    except:
        return_code = "Not found"

    if verbose:
        log.info(
            f"{human_readable}"
            f"\nstdout: {output.stdout.text}"
            f"\nstderr: {output.stderr.text}"
            f"\nreturncode: {return_code}"
        )

    assert return_code != "Not found", (
        f"No return code: {human_readable}"
        f"\nstdout: {output.stdout.text}"
        f"\nstderr: {output.stderr.text}"
        f"\nreturncode: {return_code}"
    )

    assert return_code == 0 or allow_failure, (
        f"{error_string}: {human_readable}"
        f"\nstdout: {output.stdout.text}"
        f"\nstderr: {output.stderr.text}"
        f"\nreturncode: {return_code}"
    )

    return output


def capture_both(cmd, **kwargs):
    """
    Act as a proxy for sarge.capture_both
    Allows us to run debugging on all commands triggered
    This is disabled by default to avoid log spew, but can be enabled for diagnostic purposes
    """
    extended_logs = False

    if extended_logs:
        log.debug(f"Running command via sarge: {' '.join(cmd)}")

    output = sarge_capture_both(cmd, **kwargs)

    try:
        return_code = output.returncode

        if return_code == 0:
            log_fn = log.info
        else:
            log_fn = log.warning
    except:
        return_code = "None"
        log_fn = log.error

    if extended_logs:
        log_fn(
            f"\ncommand: {' '.join(cmd)}"
            f"\nstdout: {output.stdout.text}"
            f"\nstderr: {output.stderr.text}"
            f"\nreturncode: {return_code}"
        )

    return output
