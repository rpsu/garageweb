import os.path, threading, datetime
from flask import jsonify
from dotenv import dotenv_values

# Load .env files
config = {
    **dotenv_values(".env.default"),  # load what came with the repo
    **dotenv_values(".env"),  # load overrides from the local
}
print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print("config from dotenv: " + jsonify(config))

 