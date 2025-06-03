# ✅ 파일명: config_utils.py

import os
import json

CONFIG_FILE = "wwmm_config.json"

DEFAULT_CONFIG = {
    "ui": {
        "window_size": [800, 600]
    },
    "paths": {
        "wwmi_mods_path": ""
    }
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError:
        config = DEFAULT_CONFIG
        save_config(config)

    updated = False
    for section, defaults in DEFAULT_CONFIG.items():
        if section not in config:
            config[section] = defaults
            updated = True
        else:
            for key, value in defaults.items():
                if key not in config[section]:
                    config[section][key] = value
                    updated = True

    if updated:
        save_config(config)

    return config

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)