from picoth import Picoth
import json


if __name__ == "__main__":
    with open("/params.json") as f:
        config = json.load(f)
    manager = Picoth(config)
    manager.run()

