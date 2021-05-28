#!/usr/bin/env python3
import os
import subprocess
import time
import yaml
import shutil
import logging

LOGLEVEL = os.environ.get('BDFRH_LOGLEVEL', 'INFO').upper()
logging.basicConfig(level=LOGLEVEL)

# Load in a yaml config file
def load_config(config_file):
    with open(config_file,'r') as stream:
        cfg = yaml.safe_load(stream)
    return cfg

# Check for path, create if does not exist
def assure_path_exists(path):
    path = os.path.join(path, '')
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)
        logging.debug(f"Created {dir}")
    return dir

def create_or_copy_config(config_filepath):
    if not os.path.exists(config_filepath):
        assure_path_exists("config/user_configs")
        shutil.copyfile("config/default_bdfr_config.cfg", config_filepath)

config_path = "config/config.yml"
config = load_config(config_path)
bdfr_cfg = config['bdfr']
bdfrhtml_cfg = config['bdfrhtml']

if bdfr_cfg.get('users') is not None:
    while True:
        for user in bdfr_cfg.get('users'):
            bdfr_config_file = os.path.join("config/user_configs/", (user + '.cfg'))
            create_or_copy_config(bdfr_config_file)

            input_folder = os.path.join(bdfrhtml_cfg['input_folder'], (user + '/'))
            output_folder = os.path.join(bdfrhtml_cfg['output_folder'], (user + '/'))
            idList = os.path.join(output_folder, "idList.txt")

            if bdfr_cfg['run_bdfr']:
                logging.info(f"Now running BDFR for {user}")
                subprocess.call(["python", "-m", "bdfr", "archive", "--user", "me", "--saved", "-L", str(bdfr_cfg['limit']),
                                "--authenticate", input_folder, "--config", bdfr_config_file])
                subprocess.call(["python", "-m", "bdfr", "download", "--user", "me", "--saved", "-L", str(bdfr_cfg['limit']),
                                "--exclude-id-file", idList, "--authenticate", "--file-scheme", "{POSTID}", input_folder, "--config", bdfr_config_file])
            subprocess.call(["python", "-m", "bdfrtohtml", "--config", config_path, "--input_folder", input_folder, "--output_folder", output_folder])
        logging.info(f"Runs complete, now waiting for {int(bdfr_cfg['frequency'])} minutes before next run.")
        time.sleep(int(bdfr_cfg['frequency']*60))
        
else:
    idList = os.path.join(bdfrhtml_cfg['output_folder'], "idList.txt")
    input_folder = bdfrhtml_cfg['input_folder']
    output_folder =  bdfrhtml_cfg['output_folder']
    default_config = "config/user_configs/default_config.cfg"
    create_or_copy_config(default_config)

    while True:
        if bdfr_cfg['run_bdfr']:
            logging.info(f"Now running BDFR for saved posts.")
            subprocess.call(["python", "-m", "bdfr", "archive", "--user", "me", "--saved", "-L", str(bdfr_cfg['limit']),
                            "--authenticate", input_folder, "--config", default_config])
            subprocess.call(["python", "-m", "bdfr", "download", "--user", "me", "--saved", "-L", str(bdfr_cfg['limit']),
                            "--exclude-id-file", idList, "--authenticate", "--file-scheme", "{POSTID}", input_folder, "--config", default_config])
        subprocess.call(["python", "-m", "bdfrtohtml", "--config", config_path])
        logging.info(f"Runs complete, now waiting for {int(bdfr_cfg['frequency'])} minutes before next run.")
        time.sleep(int(bdfr_cfg['frequency'])*60)
