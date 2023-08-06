import re
import logging as log
from behave.runner import Context

from lawnmowerlatte.behave.exceptions import (
    LexicalAnalzyerTokenizationError,
    LexicalAnalzyerPathError,
    LexicalAnalzyerDataError,
    LexicalAnalzyerParameterError,
)


def tokenize(text):
    token_pattern = r"""
    (?P<identifier>([a-zA-Z0-9_!"#\$%&'\(\)\*\+,\-\./:;<=>\?@\[\]\^_`|~]+))
    |(?P<open_curly>[{])
    |(?P<close_curly>[}])
    |(?P<whitespace>\s+)
    |(?P<backslash>[\\])
    """

    token_re = re.compile(token_pattern, re.VERBOSE)
    pos = 0

    while True:
        m = token_re.match(text, pos)
        if not m:
            break
        pos = m.end()
        tokname = m.lastgroup
        tokvalue = m.group(tokname)
        yield tokname, tokvalue
    if pos != len(text):
        raise LexicalAnalzyerTokenizationError(
            "tokenizer stopped on character {} at pos {} of {}".format(
                text[pos], pos, len(text)
            )
        )


def sub_tokens(context, input):
    output_buffer = ""
    path_buffer = ""
    is_path = False
    is_escaped = False

    for t in tokenize(input):
        # If escaped...
        if is_escaped:
            # Clear the flag
            is_escaped = False

            # If curly braces, omit the backslash and add the char
            if t[0] in ["open_curly", "close_curly"]:
                output_buffer += t[1]
            # Otherwise, add the backslash and the char
            else:
                output_buffer += "\\" + t[1]

            # Skip processing this character
            continue

        # If we're inside a path definition...
        elif is_path:
            # If the path is ending...
            if t[0] == "close_curly":
                # Clear the flag
                is_path = False

                # Retrieve the variable from path
                output_buffer += str(get_path_variable(context, path_buffer))

                # Reset the buffer
                path_buffer = ""
            # If whitespace exists in the path definition, it is not a path!
            elif t[0] == "whitespace":
                # Clear the flag
                is_path = False

                # Append gobbled text
                output_buffer += "{" + path_buffer

                # Reset the path
                path_buffer = ""
            else:
                # Otherwise add the character
                path_buffer += t[1]

            continue

        # If we're not escaped or in a path
        else:
            # If it's a open curly brace
            if t[0] == "open_curly":
                # Set the flag
                is_path = True
            # If it's a backslash
            elif t[0] == "backslash":
                # Set the flag
                is_escaped = True
            # If it's a regular command
            else:
                # Add the character to the output
                output_buffer += t[1]

    # At the end of the loop...
    # If the previous character was an escape
    if is_escaped:
        # Clear the flag
        is_escaped = False
        # Add the backslash
        output_buffer += "\\"

    return output_buffer


def get_path_variable(context, path):
    if path == "":
        return context

    # Strip leading and trailing curly braces (just in case)
    if path[0] == "{" and path[-1] == "}":
        path = path[1:-1]

    # Regex matches all valid curly notations
    #   Group 1: Assignment name
    #       Optional
    #       Allows a variable name to store anything retrieved
    #       Separated by an `=`
    #   Group 2: Path to retrieve or generate data
    #       May contain slashes which indicate nesting. Supports object, dict and lists
    #       May start with an `*` indicating use of a named generator function
    #   Group 3: Keyword parameters for use with functions
    #       Only used if the path ends in a function
    #       Separated by a `:`
    path_regex = "(?:([A-Za-z0-9_]+)=)?((?:[A-Za-z0-9_\-*\\\]+\/)*(?:[A-Za-z0-9_\-\*]+))(?::((?:[A-Za-z0-9_]+=[^,]+,)*(?:[A-Za-z0-9_]+=[^,]+)))?"
    path_parts = re.match(path_regex, path)

    if path_parts is None:
        raise LexicalAnalzyerPathError("Unexpected path: {}".format(path))

    assignment, path, parameters = path_parts.groups()

    if parameters:
        parameters = {
            k: v for k, v in [pair.split("=") for pair in parameters.split(",")]
        }
    else:
        parameters = {}

    if path[0] == "*":
        keyword = path[1:]
        value = context.generator.generate(keyword, parameters)
    else:
        path = re.split(r"(?<!\\)/", path)
        pointer = context

        for next in path:
            pointer = get_child_node(pointer, next)

        if callable(pointer):
            pointer = pointer(**parameters)
        elif parameters:
            raise LexicalAnalzyerParameterError(
                f"Parameters ({parameters}) were passed to a non-callable entity ({pointer} {type(pointer)})"
            )

        value = pointer

    if assignment:
        set_path_variable(context, assignment, value)

    return value


def get_child_node(container, pointer):
    next_node = None

    if "\\" in pointer:
        pointer = pointer.replace("\\", "")

    if pointer == "":
        return container

    # If the current container is a function, call it without parameters and use the result
    try:
        if callable(container):
            container = container()
    except KeyError:
        pass

    if isinstance(container, dict):
        try:
            next_node = container.get(pointer)
        except KeyError:
            raise LexicalAnalzyerDataError(
                "Dict has no entry for key: {} not in {}".format(pointer, container)
            )

    elif isinstance(container, list):
        pop = False

        if len(container) <= 0:
            raise LexicalAnalzyerDataError("List has no entries: {}".format(container))

        if pointer[0] == "*":
            pop = True
            pointer = pointer[1:]

        try:
            pointer = int(pointer)
        except ValueError:
            pointer = 0

        try:
            if pop:
                next_node = container.pop(pointer)
            else:
                next_node = container[pointer]

        except IndexError:
            raise LexicalAnalzyerDataError(
                "List has no entry for index: {} in {}".format(pointer, container)
            )

    elif isinstance(container, Context):
        try:
            next_node = container.__getattr__(pointer)
        except AttributeError:
            raise LexicalAnalzyerDataError(
                "Pointer not in Context: {} not in {}".format(pointer, container)
            )
    elif isinstance(container, str):
        pop = False

        if pointer[0] == "*":
            pop = True
            pointer = pointer[1:]

        # Try to treat the pointer as an index, otherwise try to use the string as an object
        try:
            pointer = int(pointer)

            try:
                if pop:
                    next_node = container.pop(pointer)
                else:
                    next_node = container[pointer]

            except IndexError:
                raise LexicalAnalzyerDataError(
                    "List has no entry for index: {} in {}".format(pointer, container)
                )
        except ValueError:
            try:
                next_node = container.__getattribute__(pointer)
            except AttributeError:
                raise LexicalAnalzyerDataError(
                    "Pointer is not an attribute of object: {} not in {}".format(
                        pointer, container
                    )
                )
            except:
                raise LexicalAnalzyerDataError(
                    "Unhandled error looking for pointer in object: {} in {}".format(
                        pointer, container
                    )
                )

    elif isinstance(container, object):
        try:
            next_node = container.__getattribute__(pointer)
        except AttributeError:
            raise LexicalAnalzyerDataError(
                "Pointer is not an attribute of object: {} not in {}".format(
                    pointer, container
                )
            )
        except:
            raise LexicalAnalzyerDataError(
                "Unhandled error looking for pointer in object: {} in {}".format(
                    pointer, container
                )
            )

    else:
        raise LexicalAnalzyerDataError(
            "Unhandled datatype: {}:{}".format(type(container), container)
        )

    return next_node


def parse_path_string(context, input):
    if input is not None:
        return sub_tokens(context, input)
    else:
        return None


def set_path_variable(context, path, value):
    path = path.split("/")

    pointer = get_path_variable(context, "/".join(path[:-1]))
    index = path[-1]

    if isinstance(pointer, dict):
        pointer[index] = value
    elif isinstance(pointer, list):
        try:
            pointer[int(index)] = value
        except ValueError:
            pointer.append(value)
    elif isinstance(pointer, object):
        pointer.__setattr__(index, value)
        # Because the context class intercepts calls to dir(), we
        # can't see any variables that we add to an object here. To
        # work around that, we also add a special set which tracks all
        # of the variables that we have added so that we can find them
        # later.
        try:
            pvars = getattr(pointer, "_pvars")
        except (KeyError, AttributeError):
            pvars = set()
            pointer.__setattr__("_pvars", pvars)
        pvars.add(index)

    path = "/".join(path)
    log.debug(f"Assigned variable: {path}='{value}' ({value.__class__.__name__})")
