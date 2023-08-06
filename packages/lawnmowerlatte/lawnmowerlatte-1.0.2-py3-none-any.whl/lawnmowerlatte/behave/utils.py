import logging as log
from json import JSONDecodeError

from jsonpickle import json

from lawnmowerlatte.behave.lexical_analyzer import parse_path_string
from lawnmowerlatte.behave.exceptions import (
    LexicalAnalzyerDataError,
    LexicalAnalzyerPathError,
)


def compare_hex(value, json_or_str):
    # value: the option value which is returned from dhclient in bytes view. E.g., b'\x7f\xff\xff\xff\x00\xff\x00\x7fstringval'
    # json_or_str: the option value which we specify in tests (in Behave *.feature file). It should be a list
    # E.g., ["testtextABC"] if we check String option
    #
    # Thr example below demonstrates a complex option:
    #       This is hex value of:   [ 2147483647,        0.  255.0.  127,  "stringval"]
    #       This is hex         :   [ \x7f\xff\xff\xff,  \x00\xff\x00\x7f, "stringval"]
    #       This is byte        :   [ 127 255 255 255    0    255 0   127   stringval]
    # Thus, in *.feature file we specify the following list: [127,255,255,255,0,255,0,127,"stringval"]

    # when in Behave test we specify a String, and when dhcp client returns String
    if type(json_or_str) is str and type(value) is str:
        return json_or_str == value

    # when in Behave test we specify a String, dhcp client returns Bytes
    if type(json_or_str) is str and type(value) is bytes:
        return json_or_str == value.decode("utf-8")

    # Otherwise, we try to check the bytes returned by dhcp client.
    # If dhcp client returns something else (I have never faced. Perhaps in case of specific dhcp client or in case when something broken
    # was returned by dhcp client), we throw exception.
    if type(value) is bytes:
        comparison_result = True
        for i in range(len(json_or_str)):
            # Comparing Int specified in a list of *.feature file and the element value from bytes sequence.
            # The value[i] returns a Int of element from bytes sequence. E.g., b'\x7f' is 127. So, we compare the two Integers here
            if type(json_or_str[i]) is int:
                comparison_result = comparison_result and json_or_str[i] == value[i]
            # When element is String and the String element is the last one in a sequence
            elif type(json_or_str[i]) is str and i == (len(json_or_str) - 1):
                try:
                    comparison_result = comparison_result and json_or_str[i] == value[
                        i:
                    ].decode("utf-8")
                except UnicodeDecodeError:
                    comparison_result = False
            else:
                raise Exception(
                    f"Hex - Json comparation exception \nhex = {value}\njson={json_or_str}"
                )
        return comparison_result
    else:
        raise Exception(
            f"This value {value} of {type(value)} data type is not supported."
        )


def parse_context_table(c_context, *args_colomns):
    result = []
    if c_context.table:
        for row in c_context.table:
            row_tuple = ()
            for colomn in args_colomns:
                try:
                    row_tuple += (parse_path_string(c_context, row[colomn]),)
                except LexicalAnalzyerDataError:
                    row_tuple += row[colomn]
            result.append(row_tuple)
    if len(*args_colomns) is 1:
        result = [element[0] for element in result]
    return result


def parse_context_table_to_dict(c_context, key_str, value_str):
    result = {}
    if c_context.table:
        for row in c_context.table:
            try:
                key = parse_path_string(c_context, row[key_str])
            except (LexicalAnalzyerDataError, LexicalAnalzyerPathError):
                key = row[key_str]
            try:
                value = parse_path_string(c_context, row[value_str])
            except (LexicalAnalzyerDataError, LexicalAnalzyerPathError):
                value = row[value_str]
            try:
                result[key] = json.loads(value)
            except JSONDecodeError:
                result[key] = value
    return result


def parse_context_table_to_list_of_dict(c_context):
    result = []
    if c_context.table:
        columns = c_context.table.headings
        for row in c_context.table.rows:
            m = {}
            for column in columns:
                m[column] = parse_path_string(c_context, row[column])
            result.append(m)
    return result


def parse_context_table_to_list_of_dict_preserve_boolean(c_context):
    """
    Acts the same as parse_context_table_to_list_of_dict but converts table values to booleans if possible:
        Each "false","False","True","true" values will be converted to related boolean values
    """
    result = []
    if c_context.table:
        columns = c_context.table.headings
        for row in c_context.table.rows:
            m = {}
            for column in columns:
                m[column] = cast_string_to_bool(
                    parse_path_string(c_context, row[column])
                )
            result.append(m)
    return result


def parse_fixture_string(raw_fixture_tag):
    try:
        fixture_name, raw_params = raw_fixture_tag.split(":")
    except ValueError:
        fixture_name = raw_fixture_tag
        raw_params = None

    params = parse_fixture_params(raw_params)

    return (fixture_name, params)


def parse_fixture_params(raw_params):
    params = {}
    if raw_params is not None:
        for raw_param in raw_params.split(";"):
            log.debug(f"Found key value pair: {raw_param}")
            key, value = raw_param.split("=")
            if "," in value:
                value = value.split(",")
                log.debug(f"Value is a list")
                if len(value) > 0 and value[-1] == "":
                    log.debug(f"Found trailing comma, removed last element")
                    value.pop()
            params[key] = value

        return params
    else:
        return None


def skip_scenario_based_on_fixture_tags(skipped_images, tags):
    """
    Based on the list of tags provided, look for fixtures and compare it to the list of skipped images
    Return True if the tag list provided indicates that the scenario can be skipped
    """
    # Check all effective tags and aggregate the fixture services and run_if_built values
    fixture_services = []

    """
    Fixture Service Configuration
        Below is an outline of how to construct a new fixture service configuration for a new fixture.
        
        ---- 
        "{fixture_name}": {
            "remap": {
                // A list of key/values which dictate how to map the service name into a Docker image name
                // Note that this is the "services" parameter in the fixture tag
                // It is not _necessarily_ the docker-compose service name, it depends on the fixture
                "{compose_service_to_remap}": "{remapped_as_docker_image}",
            },
            "ignore": [
                // A list of services which are ignored when considering whether it should run or not
                // Note that this is the "services" parameter in the fixture tag
                // It is not _necessarily_ the docker-compose service name, it depends on the fixture
                "{compose_service_to_ignore}",
            ],
            "always": [
                // A list of Docker images which are always assumed to be running, even if not stated in the services
                // Note that this is the Docker image itself, not the service name
                // This value does not get remapped
                "{docker_image_to_assume}",
            ]
        },
    """

    fixture_service_configuration = {
        "fixture.managed.s4": {
            "remap": {
                "core": "standalone_core_flat",
                "data": "standalone_data_flat",
                "dhcp": "standalone_dhcp_flat",
                "dist": "standalone_dist_flat",
                "dns": "standalone_dns_flat",
                "dnskey": "standalone_dnskeyd_flat",
                "monitor": "standalone_monitor_flat",
                "xfr": "standalone_xfr_flat",
                "logging": "standalone_logging_flat",
            },
            "ignore": [
                "mailhog",
                "mongo",
                "web",
                "php",
                "db",
                "solr",
                "rabbitmq",
                "redis",
                "zoo",
                "kafka",
            ],
        },
        "fixture.standalone.local": {
            "remap": {
                "core": "standalone_core_flat",
                "data": "standalone_data_flat",
                "dhcp": "standalone_dhcp_flat",
                "dist": "standalone_dist_flat",
                "dns": "standalone_dns_flat",
                "dnskey": "standalone_dnskeyd_flat",
                "monitor": "standalone_monitor_flat",
                "xfr": "standalone_xfr_flat",
                "xfr_dist": "standalone_xfr_flat",
                "xfr_other": "standalone_xfr_flat",
                "replica": "standalone_data_flat",
                "monitor_c1": "standalone_monitor_flat",
                "monitor_c2": "standalone_monitor_flat",
                "monitor_c3": "standalone_monitor_flat",
                "monitor_remote": "standalone_monitor_flat",
                "dhcp_backup": "standalone_dhcp_flat",
                "dhcp_remote": "standalone_dhcp_flat",
                "dist_remote": "standalone_dist_flat",
                "dist_multiple_core_hosts": "standalone_dist_flat",
                "dhcp_remote_backup": "standalone_dhcp_flat",
                "dns_remote": "standalone_dns_flat",
                "cdns": "standalone_dns_flat",
                "core_remote": "standalone_core_flat",
                "ccore": "standalone_core_flat",
                "ccore2": "standalone_core_flat",
                "cd1": "standalone_data_flat",
                "cd2": "standalone_data_flat",
                "cd3": "standalone_data_flat",
                "cd4": "standalone_data_flat",
                "cd5": "standalone_data_flat",
                "cddr1": "standalone_data_flat",
                "cddr2": "standalone_data_flat",
                "cddr3": "standalone_data_flat",
                "logging": "standalone_logging_flat",
            },
            "ignore": [
                "mailhog.proxy",
                "chromedriver",
                "bind",
                "bindcustomport",
                "openvas",
                "influx",
                "elk",
                "opentsdb",
                "graphite",
                "prometheus",
                "nginx_sni",
                "xfrgenerate",
                "fixed_ip",
                "zoo",
                "kafka",
            ],
        },
        "fixture.nexus.local": {"always": ["nexusd", "standalone_data_flat"]},
        "fixture.common_go.local": {
            "remap": {"common_go": "common-go"},
            "always": ["common-go"],
            "ignore": ["zoo", "kafka"],
        },
        "fixture.monprod_v3.local": {"always": ["standalone_monitor_flat"]},
        "fixture.clustered_ha": {"alias": "fixture.standalone.local"},
        "fixture.standalone.bootstrap_server": {"alias": "fixture.standalone.local"},
    }

    for tag in tags:
        if tag.startswith("run_if_built="):
            fixture_services.extend(tag.split("=", 1)[1].split(","))
            continue

        if not tag.startswith("fixture."):
            continue

        # Parse the fixture name and params
        fixture_name, params = parse_fixture_string(tag)
        if params:
            services = params.get("services", [])
        else:
            services = []

        if isinstance(services, str):
            log.debug("Casting single service to a list")
            services = [services]

        log.debug(f"Scanning {fixture_name} fixture with services: {services}")

        # Check tag against configuration and add any images to the list
        for fixture_config_key, fixture_config in fixture_service_configuration.items():
            if "alias" in fixture_config.keys():
                # If the fixture_config is an alias of another, replace it here
                fixture_config = fixture_service_configuration[fixture_config["alias"]]

            if fixture_name.startswith(fixture_config_key):
                for always in fixture_config.get("always", []):
                    # Always add any images in the always list
                    fixture_services.append(always)

                for service in services:
                    if service in fixture_config.get("ignore", []):
                        # Ignore services in the ignore list
                        pass
                    elif service in fixture_config.get("remap", {}).keys():
                        # Add remapped image
                        fixture_services.append(fixture_config["remap"][service])
                    else:
                        # Handle the default case and add the image
                        # Don't remove this, this handles cases unrecognized services
                        fixture_services.append(service)

    # Check fixture services against the skipped images provided and generate a list of built images
    built_images = [image for image in fixture_services if image not in skipped_images]

    # If the scenario specifies images
    if not fixture_services:
        log.debug("No fixture_services specified, running scenario")
        return False
    # If there are any images required which were not in the skipped list, generate a log
    elif built_images:
        log.debug(
            f"Scenario relies on images which are not in the provided skipped images: {built_images}"
        )
        return False
    else:
        log.debug(
            f"Scenario relies only on images which in the provided skipped images: {fixture_services}"
        )
        return True


def cast_string_to_bool(val):
    """
    Cast string value to boolean if possible. If not, then returns original value unchanged
    """
    if isinstance(val, str):
        if val.lower() == "true":
            return True
        elif val.lower() == "false":
            return False

    return val
