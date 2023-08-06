import toml


def read_config(path):
    with open(path, 'r') as f:
        return toml.load(f)


def read_version_field(path):
    config = read_config(path)
    return config["tool"]["poetry"]["version"]
