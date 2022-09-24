import json

def load():
    with open("config.json", "r") as config_file:
        return json.load(config_file)

def dump(config):
    with open("config.json", "w") as config_file:
        json.dump(config, config_file, indent=4)

def update(key, value):
    config = load()
    config[key] = value
    dump(config)