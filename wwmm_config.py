# wwmm_config.py
import os
import json

CONFIG_FILE = "wwmm_config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {"wwmi_path": ""}

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)

def get_wwmi_mods_path():
    config = load_config()
    return os.path.join(config.get("wwmi_path", ""), "Mods")