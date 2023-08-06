import logging as log
import json


def format_compose_files(compose_files):
    params = []
    [params.extend(["-f", file]) for file in compose_files]

    return params


def generate_compose_prefix(context):
    command = [context.env["compose"]]
    command.extend(["-p", context.compose_project])
    command.extend(format_compose_files(context.compose_files))

    log.debug(f"Generated docker-compose base command: {' '.join(command)}")

    return command
