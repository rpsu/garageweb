import os.path, re
from datetime import datetime
from dotenv import dotenv_values

print("File: " + os.path.basename(__file__))
print("Time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print("Loading config.")
# Load .env files
config = {
    **dotenv_values(".env.default"),  # load what came with the repo
    **dotenv_values(".env"),  # load overrides from the local
}
for k, v in config.items():
    if v == 'False':
        config[k] = False
    elif v == 'True':
        config[k] = True
    elif re.search("\d", config.get(k)) is not None:
        config[k] = int(config[k])

print("Config loaded: " + str(len(config)) + " items.")
line = 1
for k, v in config.items():
    print(str(line) + ": " + str(k) + " => [" + str(type(v)) + "] " + str(v))
    line = line + 1

print("Done.")

 