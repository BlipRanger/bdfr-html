#!/usr/bin/env python3
import os
import subprocess
import time
import yaml


# Load in a yaml config file
def load_config(config_file):
    with open(config_file,'r') as stream:
        cfg = yaml.safe_load(stream)
    return cfg

config_path = "config/config.yml"
config = load_config(config_path)
bdfr_cfg = config['bdfr']
bdfrhtml_cfg = config['bdfrhtml']


idList = os.path.join(bdfrhtml_cfg['output_folder'], "idList.txt")

while True:
    if bdfr_cfg['run_bdfr']:
        subprocess.call(["python", "-m", "bdfr", "archive", "--user", "me", "--saved", "-L", str(bdfr_cfg['limit']),
                         "--authenticate", bdfrhtml_cfg['input_folder']])
        subprocess.call(["python", "-m", "bdfr", "download", "--user", "me", "--saved", "-L", str(bdfr_cfg['limit']),
                         "--exclude-id-file", idList, "--authenticate", "--file-scheme", "{POSTID}", bdfrhtml_cfg['input_folder']])
    subprocess.call(["python", "-m", "bdfrtohtml", "--config", config_path])
    time.sleep(int(bdfr_cfg['frequency'])*60)
