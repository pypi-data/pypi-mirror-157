import re


def camel_to_kebab(name):
    pattern = re.compile(r"(?<!^)(?=[A-Z])")
    return pattern.sub("-", name).lower()


def camel_to_snake(name):
    pattern = re.compile(r"(?<!^)(?=[A-Z])")
    return pattern.sub("_", name).lower()
