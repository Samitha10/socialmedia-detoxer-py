import tomllib  # Use 'tomli' for Python versions below 3.11

with open("config/server.toml", "rb") as f:
    config = tomllib.load(f)
    print(config)
