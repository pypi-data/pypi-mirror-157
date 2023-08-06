import json
import re
import random
import logging as log
import time
from faker import Faker


class Generator(object):
    country_codes = [
        "BD",
        "BE",
        "BF",
        "BG",
        "BA",
        "BB",
        "WF",
        "BL",
        "BM",
        "BN",
        "BO",
        "BH",
        "BI",
        "BJ",
        "BT",
        "JM",
        "BV",
        "BW",
        "WS",
        "BR",
        "BS",
        "JE",
        "BY",
        "BZ",
        "RU",
        "RW",
        "RS",
        "LT",
        "RE",
        "LU",
        "LR",
        "RO",
        "LS",
        "GW",
        "GU",
        "GT",
        "GS",
        "GR",
        "GQ",
        "GP",
        "JP",
        "GY",
        "GG",
        "GF",
        "GE",
        "GD",
        "GB",
        "GA",
        "GN",
        "GM",
        "GL",
        "GI",
        "GH",
        "OM",
        "JO",
        "HR",
        "HT",
        "HU",
        "HK",
        "HN",
        "HM",
        "AD",
        "PR",
        "PS",
        "PW",
        "PT",
        "SJ",
        "PY",
        "IQ",
        "SH",
        "PF",
        "PG",
        "PE",
        "PK",
        "PH",
        "PN",
        "PL",
        "PM",
        "ZM",
        "EH",
        "EE",
        "EG",
        "ZA",
        "EC",
        "AL",
        "AO",
        "SB",
        "ET",
        "SO",
        "ZW",
        "SA",
        "ES",
        "ER",
        "ME",
        "MD",
        "MG",
        "MF",
        "MA",
        "MC",
        "UZ",
        "MM",
        "ML",
        "MO",
        "MN",
        "MH",
        "MK",
        "MU",
        "MT",
        "MW",
        "MV",
        "MQ",
        "MP",
        "MS",
        "MR",
        "AU",
        "UG",
        "UA",
        "MX",
        "AT",
        "FR",
        "IO",
        "AF",
        "AX",
        "FI",
        "FJ",
        "FK",
        "FM",
        "FO",
        "NI",
        "NL",
        "NO",
        "NA",
        "VU",
        "NC",
        "NE",
        "NF",
        "NG",
        "NZ",
        "NP",
        "NR",
        "NU",
        "CK",
        "CI",
        "CH",
        "CO",
        "CN",
        "CM",
        "CL",
        "CC",
        "CA",
        "CG",
        "CF",
        "CD",
        "CZ",
        "CY",
        "CX",
        "CR",
        "CV",
        "CU",
        "SZ",
        "SY",
        "KG",
        "KE",
        "SR",
        "KI",
        "KH",
        "SV",
        "KM",
        "ST",
        "SK",
        "KR",
        "SI",
        "KP",
        "KW",
        "SN",
        "SM",
        "SL",
        "SC",
        "KZ",
        "KY",
        "SG",
        "SE",
        "SD",
        "DO",
        "DM",
        "DJ",
        "DK",
        "DE",
        "YE",
        "DZ",
        "US",
        "LV",
        "UY",
        "YT",
        "UM",
        "KN",
        "LB",
        "LC",
        "LA",
        "TV",
        "TW",
        "TT",
        "TR",
        "LK",
        "LI",
        "TN",
        "TO",
        "TL",
        "TM",
        "TJ",
        "TK",
        "TH",
        "TF",
        "TG",
        "TD",
        "TC",
        "LY",
        "VA",
        "VC",
        "AE",
        "VE",
        "AG",
        "VG",
        "AI",
        "VI",
        "IS",
        "IR",
        "AM",
        "IT",
        "VN",
        "AS",
        "AR",
        "IM",
        "IL",
        "AW",
        "IN",
        "TZ",
        "AZ",
        "IE",
        "ID",
        "PA",
        "MY",
        "QA",
        "MZ",
    ]

    ca_province = [
        "ON",
        "AB",
        "NL",
        "MB",
        "NB",
        "BC",
        "YT",
        "SK",
        "QC",
        "PE",
        "NS",
        "NT",
        "NU",
    ]

    usa_states = [
        "WA",
        "DE",
        "DC",
        "WI",
        "WV",
        "HI",
        "FL",
        "WY",
        "NH",
        "NJ",
        "NM",
        "TX",
        "LA",
        "NC",
        "ND",
        "NE",
        "TN",
        "NY",
        "PA",
        "CA",
        "NV",
        "VA",
        "CO",
        "AK",
        "AL",
        "AR",
        "VT",
        "IL",
        "GA",
        "IN",
        "IA",
        "MA",
        "AZ",
        "ID",
        "CT",
        "ME",
        "MD",
        "OK",
        "OH",
        "UT",
        "MO",
        "MN",
        "MI",
        "RI",
        "KS",
        "MT",
        "MS",
        "SC",
        "KY",
        "OR",
        "SD",
    ]

    def __init__(self):
        self.faker = Faker()

        self.assignments = {
            "name": self.generate_name,
            "username": self.generate_username,
            "hostname": self.generate_hostname,
            "country_code": self.generate_country_code,
            "country_codes_all": self.generate_country_codes_all,  # This is all possible values, not random
            "ca_province_all": self.generate_ca_province_all,  # This is all possible values, not random
            "usa_state": self.generate_usa_state,
            "usa_states_all": self.generate_usa_states_all,  # This is all possible values, not random
            "ipv4": self.generate_ipv4,
            "ipv6": self.generate_ipv6,
            "slug": self.generate_slug,
            "org": self.generate_org,
            "email": self.generate_email,
            "cidrv4": self.generate_cidrV4,
            "cidrv6": self.generate_cidrV6,
        }

        self.allow_repeat = [
            "country_codes",
        ]

        self.history = {}

    def generate(self, assignment_type, parameters):
        assignment_type = assignment_type.lower()
        log.debug(
            f"Generating data of type '{assignment_type}' with parameters {parameters}"
        )

        if assignment_type not in self.assignments.keys():
            raise RuntimeError(f"Type {assignment_type} not found in Generator class")

        allow_repeat = parameters.pop("allow_repeat", "false").lower() in [
            "true",
            "t",
            "1",
        ]
        value = self.assignments[assignment_type](**parameters)

        if assignment_type not in self.allow_repeat and not allow_repeat:
            # Regenerate if the value has already been used
            retry = 0
            max_retries = 100

            if assignment_type not in self.history.keys():
                self.history[assignment_type] = []

            while value in self.history[assignment_type]:
                value = self.assignments[assignment_type](**parameters)
                retry += 1
                if retry > max_retries:
                    raise RuntimeError(
                        f"Exceeded {max_retries} retries while generating {assignment_type} variable"
                    )

            self.history[assignment_type].append(value)

        try:
            preview = str(value)
        except:
            preview = "[no preview available]"

        if len(preview) > 1000:
            preview = preview[:1000] + "[truncated]"

        log.debug(f"Generated value of '{preview}'")
        return value

    def register(self, keyword, allow_repeat=False):
        def register_decorator(fn):
            def fn_wrapper(**kwargs):
                return fn(**kwargs)

            assert (
                keyword not in self.assignments.keys()
            ), f"Keyword {keyword} already registered"
            assert callable(fn), f"Function {fn} is not callable"

            self.assignments[keyword] = fn
            if allow_repeat:
                self.allow_repeat.append(keyword)

            log.debug(f"Successfully registered {keyword} as {fn}")

            return fn_wrapper

        return register_decorator

    def generate_name(self):
        name = self.faker.name()

        return name

    def generate_username(self, name=None, max_length=None):
        name = name or self.faker.name()

        if name == "use_last":
            name = self.history["name"][-1]

        username = re.sub("[^a-z0-9_]", "_", name.lower())

        if (max_length is not None) and (len(username) > int(max_length)):
            username = username[0 : int(max_length)]

        return username

    def generate_hostname(self, name=None):
        name = name or self.faker.domain_word()

        if name == "use_last":
            name = self.history["hostname"][-1]

        hostname = re.sub("[^a-z0-9\-]", "", name.lower())
        return hostname

    def generate_country_code(self):
        return random.choice(self.country_codes)

    def generate_country_codes_all(self, form=None):
        if form is None:
            return self.country_codes
        elif form.upper() == "JSON":
            return str(self.country_codes).replace("'", '"')
        else:
            return self.country_codes

    def generate_ca_province_all(self, form=None):
        if form is None:
            return self.ca_province
        elif form.upper() == "JSON":
            return str(self.ca_province).replace("'", '"')
        else:
            return self.ca_province

    def generate_usa_state(self):
        return random.choice(self.usa_states)

    def generate_usa_states_all(self, form=None):
        if form is None:
            return self.usa_states
        elif form.upper() == "JSON":
            return str(self.usa_states).replace("'", '"')
        else:
            return self.usa_states

    def generate_ipv4(self, network=None, private=False, cc=None):
        if private in [None, "None"]:
            private = None
        else:
            private = bool(private)

        if cc is not None:
            random_ip = dns_spoof.get_ipv4_by_cc(cc)
            return random_ip
        else:
            random_ip = self.faker.ipv4(private=private)

            # Network support is limited to classful IPs
            # Network IP is used if octet is not 0
            if network is not None:
                random_ip_parts = random_ip.split(".")
                network_parts = network.split(".")
                result_parts = []
                for i in range(4):
                    if network_parts[i] == "0":
                        result_parts.append(random_ip_parts[i])
                    else:
                        result_parts.append(network_parts[i])
                return ".".join(result_parts)
            else:
                return random_ip

    def generate_ipv6(self, network=None, cc=None):
        if cc is not None:
            random_ip = dns_spoof.get_ipv6_by_cc(cc)
            return random_ip
        else:
            return self.faker.ipv6(network=network)

    def generate_slug(self, max_length=None, min_length=None):
        slug = self.faker.slug()

        if min_length is not None:
            while len(slug) < min_length:
                slug = self.faker.slug()

        if (max_length is not None) and (len(slug) > int(max_length)):
            slug = slug[0 : int(max_length)]

        return slug

    def generate_org(self):
        org = f"{self.faker.company()}, {self.faker.company_suffix()}"

        return org

    def generate_email(self):
        return self.faker.email()

    def generate_cidrV4(self, suffix=32):
        suffix = int(suffix)
        ip = f"{self.faker.ipv4()}"
        if suffix == 32:
            return f"{ip}/{suffix}"
        ip_list = ip.split(".")
        i = 3
        s = suffix
        while s < 32:
            ip_list[i] = "0"
            s += 8
            i -= 1
        ip = ".".join(ip_list)
        cidr = f"{ip}/{suffix}"

        return cidr

    def generate_cidrV6(self):
        mask = random.randint(8, 128)
        cidr = f"{self.faker.ipv6()}/{mask}"

        return cidr


generator = Generator()
register = generator.register
