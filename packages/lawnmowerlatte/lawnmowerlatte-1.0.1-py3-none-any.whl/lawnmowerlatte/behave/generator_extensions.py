import re
import random
import string
import logging as log

from faker import Faker
from hypothesis.strategies import text, characters

from lawnmowerlatte.behave.generator import generator


@generator.register("lorem")
def generate_lorem_ipsem(length=None, capitalized=None):
    lorem_ipsem = """
        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et 
        dolore magna aliqua. Dolor sed viverra ipsum nunc aliquet bibendum enim. In massa tempor nec feugiat. Nunc 
        aliquet bibendum enim facilisis gravida. Nisl nunc mi ipsum faucibus vitae aliquet nec ullamcorper. Amet 
        luctus venenatis lectus magna fringilla. Volutpat maecenas volutpat blandit aliquam etiam erat velit 
        scelerisque in. Egestas egestas fringilla phasellus faucibus scelerisque eleifend. Sagittis orci a 
        scelerisque purus semper eget duis. Nulla pharetra diam sit amet nisl suscipit. Sed adipiscing diam donec 
        adipiscing tristique risus nec feugiat in. Fusce ut placerat orci nulla. Pharetra vel turpis nunc eget lorem 
        dolor. Tristique senectus et netus et malesuada.
        
        Etiam tempor orci eu lobortis elementum nibh tellus molestie. Neque egestas congue quisque egestas. Egestas 
        integer eget aliquet nibh praesent tristique. Vulputate mi sit amet mauris. Sodales neque sodales ut etiam 
        sit. Dignissim suspendisse in est ante in. Volutpat commodo sed egestas egestas. Felis donec et odio 
        pellentesque diam. Pharetra vel turpis nunc eget lorem dolor sed viverra. Porta nibh venenatis cras sed 
        felis eget. Aliquam ultrices sagittis orci a. Dignissim diam quis enim lobortis. Aliquet porttitor lacus 
        luctus accumsan. Dignissim convallis aenean et tortor at risus viverra adipiscing at.
    """

    length = int(length or 200)
    value = ""
    words = list(set(lorem_ipsem.lower().replace(".", "").replace(",", "").split()))
    sentence_counter = 0

    while len(value) < length:
        sentence_counter += 1
        word = random.choice(words)

        if sentence_counter == 1:
            value += word.capitalize()
        else:
            value += word
        if sentence_counter > random.randint(6, 10):
            sentence_counter = 0
            value += word + "."

        value += " "

    if value[length - 3] == ".":
        value = value[0 : length - 3] + "sh."
    if value[length - 3] == " ":
        value = value[0 : length - 3] + "ta."
    elif value[length - 2] == " ":
        value = value[0 : length - 2] + "s."
    else:
        value = value[0 : length - 1] + "."

    if capitalized == "1":
        value = value.upper()

    return value


@generator.register("int")
def generate_int(min=None, max=None, length=None):
    if length is not None:
        length = int(length)
        min = 10 ** (length - 1)
        max = 10**length - 1
    else:
        min = min or 0
        max = max or 65535

    return random.randint(int(min), int(max))


@generator.register("float")
def generate_float(min=None, max=None, dec=None):
    min = min or 0
    max = max or 65535
    dec = dec or 2

    return round(random.uniform(float(min), float(max)), int(dec))


@generator.register("ascii")
def generate_ascii(min=None, capitalized=None, exclude=None):
    default_exclude = "/"
    min = int(min or 32)
    exclude = exclude or default_exclude

    value = text(
        characters(
            max_codepoint=128,
            blacklist_categories=("Cc", "Cs"),
            blacklist_characters=exclude,
        ),
        min_size=min,
    ).example()

    if capitalized == "1":
        value = value.upper()

    return value


@generator.register("hex")
def generate_hex(length=None):
    length = length or 2
    length = int(length)
    characters = string.hexdigits

    s = "".join([random.choice(characters) for _ in range(length)])

    return s


@generator.register("mac")
def generate_mac(mixed=None):
    mac = "00:" + ":".join(
        ["".join([random.choice(string.hexdigits) for _ in range(2)]) for _ in range(5)]
    )

    if mixed != "1":
        mac = mac.lower()

    return mac


@generator.register("base64")
def generate_base64(length=None):
    length = length or 128
    length = int(length)
    characters = string.ascii_letters + string.digits + "+/"

    if length % 4 != 0:
        raise RuntimeError(
            "Base64 text can only be generated in blocks of 4 characters, please specify a multiple of 4"
        )

    s = ""
    for _ in range(length):
        s += random.choice(characters)

    padding = random.randint(0, 24)
    if padding >= 12:
        if padding >= 18:
            s = s[:-2] + "=="
        else:
            s = s[:-1] + "="

    return s


@generator.register("reflector")
def generate_reflector(value=None):
    if value is None:
        raise RuntimeError("Reflector generator cannot be used without a value")
    return value
