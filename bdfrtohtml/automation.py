#!/usr/bin/env python3
import os
import subprocess
import time
import yaml
import shutil
import logging
import bdfrtohtml
import sys

LOGLEVEL = os.environ.get('BDFRH_LOGLEVEL', 'INFO').upper()
logging.basicConfig(level=LOGLEVEL)

# Load in a yaml config file or make one and load it in
def load_config(config_file):
    if not os.path.exists(config_file):
        generate_bdfrhtml_config_file()
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

# Make sure we have a config file for bdfr
def create_or_copy_config(config_filepath):
    source_config = generate_bdfr_config_file()
    assure_path_exists("config/user_configs")
    if not os.path.exists(config_filepath):
        shutil.copyfile(source_config, config_filepath)
    return True

# In the case of an existing sample index file, remove it
def remove_default_index(output_folder):
    filepath = os.path.join(output_folder, 'index.html')
    if os.path.exists(filepath):
        os.remove(filepath)

# Create a default config file for bdfr if there isn't one
def generate_bdfr_config_file():
    assure_path_exists("./config/")
    source_config = "config/default_bdfr_config.cfg"
    if not os.path.exists(source_config):
        content = bdfrtohtml.util.get_bdfr_config()
        with open(source_config, "w") as cfg:
            cfg.write(content)
    return source_config

# Create a default bdfrhtml config file if there isn't one
def generate_bdfrhtml_config_file():
    assure_path_exists("./config/")
    config_file = "config/config.yml"
    config = bdfrtohtml.util.generate_default_config()
    with open(config_file, "w") as cfg:
            yaml.dump(config, cfg, default_flow_style=False)    
    return config_file

# Make both config files
def generate_configs():
    generate_bdfrhtml_config_file()
    generate_bdfr_config_file()

# The automated process of downloading and merging posts
def automate():
    config_path = "config/config.yml"
    config = load_config(config_path)

    bdfr_cfg = config['bdfr']
    bdfrhtml_cfg = config['bdfrhtml']
    input_folder = bdfrhtml_cfg['input_folder']
    output_folder =  bdfrhtml_cfg['output_folder']
    if bdfr_cfg.get('users') is not None:
        merge_users = bdfr_cfg.get('merge_users', False)
        if merge_users: remove_default_index(output_folder)
        
        while True:
            for user in bdfr_cfg.get('users'):
                bdfr_config_file = os.path.join("config/user_configs/", (user + '.cfg'))

                if not merge_users:
                    input_folder = os.path.join(bdfrhtml_cfg['input_folder'], (user + '/'))
                    output_folder = os.path.join(bdfrhtml_cfg['output_folder'], (user + '/'))
                idList = os.path.join(output_folder, "idList.txt")
                create_or_copy_config(bdfr_config_file)
                clone_command =[sys.executable, "-m", "bdfr", "clone", "--user", "me", "--saved", "-L", str(bdfr_cfg['limit']),
                                "--exclude-id-file", idList, "--authenticate", "--file-scheme", "{POSTID}", input_folder, "--config", bdfr_config_file]

                if bdfr_cfg['run_bdfr']:
                    logging.info(f"Now running BDFR for {user}")
                    subprocess.call(clone_command)
                if not merge_users:                     
                    subprocess.call([sys.executable, "-m", "bdfrtohtml", "--config", config_path, "--input_folder", input_folder, "--output_folder", output_folder])
            if merge_users:                     
                subprocess.call([sys.executable, "-m", "bdfrtohtml", "--config", config_path, "--input_folder", input_folder, "--output_folder", output_folder])
            logging.info(f"Runs complete, now waiting for {int(bdfr_cfg['frequency'])} minutes before next run.")
            time.sleep(int(bdfr_cfg['frequency']*60))
            
    else:
        idList = os.path.join(bdfrhtml_cfg['output_folder'], "idList.txt")
        default_config = "config/user_configs/default_config.cfg"
        create_or_copy_config(default_config)
        clone_command =[sys.executable, "-m", "bdfr", "clone", "--user", "me", "--saved", "-L", str(bdfr_cfg['limit']),
                        "--exclude-id-file", idList, "--authenticate", "--file-scheme", "{POSTID}", input_folder, "--config", default_config]

        while True:
            if bdfr_cfg['run_bdfr']:
                logging.info(f"Now running BDFR for saved posts.")
                subprocess.call(clone_command)
            subprocess.call([sys.executable, "-m", "bdfrtohtml", "--config", config_path])
            logging.info(f"Runs complete, now waiting for {int(bdfr_cfg['frequency'])} minutes before next run.")
            time.sleep(int(bdfr_cfg['frequency'])*60)
