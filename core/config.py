import json
import os

CONFIG_FILE = "settings.json"


def salvar_config(data):

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:

        json.dump(data, f, indent=4)


def carregar_config():

    if not os.path.exists(CONFIG_FILE):

        return {}

    try:

        with open(CONFIG_FILE, "r", encoding="utf-8") as f:

            return json.load(f)

    except:

        return {}
