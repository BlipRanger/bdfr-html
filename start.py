#!/usr/bin/env python3
import os
import subprocess
import time
import yaml


# Load in a yaml config file
def load_config(config_file):
    with open(config_file,'r') as stream:
        cfg = yaml.safe_load(stream).get('bdfrhtml')
    return cfg

config = load_config("config.yml")
bdfr_cfg = config['bdfr']
bdfrhtml_cfg = config['bdfrhtml']


idList = os.path.join(bdfr_cfg['output_folder'], "idList.txt")


while True:
    if bdfr_cfg['run_bdfr']:
        subprocess.call(["python3.9", "-m", "bdfr", "archive", "--user", "me", "--saved", "-L", bdfr_cfg['limit'],
                         "--authenticate", bdfrhtml_cfg['input_folder']])
        subprocess.call(["python3.9", "-m", "bdfr", "download", "--user", "me", "--saved", "-L", bdfr_cfg['limit'],
                         "--exclude-id-file", idList, "--authenticate", "--file-scheme", "{POSTID}", bdfrhtml_cfg['input_folder']])
    subprocess.call(["python3.9", "-m", "bdfrtohtml", "--config", "config.yml"])
    time.sleep(int(bdfrhtml_cfg['frequency'])*60)
