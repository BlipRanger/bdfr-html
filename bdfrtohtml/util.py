import logging
import time
import yaml
import click
import requests

# Load in a yaml config file
def load_config(config_file):
    cfg = yaml.safe_load(config_file).get('bdfrhtml')
    return cfg

# Default settings
def generate_default_config():
    cfg = {
        'bdfr': {
            'limit': 1000,                          
            'run_bdfr': True,               
            'frequency': 60
        },                        
        'bdfrhtml': {
            'recover_comments': False,      
            'recover_posts': False, 
            'output_folder': './output',
            'input_folder': './input', 
            'archive_context': False,           
            'delete_media': False,                                  
            'write_links_to_file': 'None',
            'generate_thumbnails': False,
            'index_mode': 'default'
        }
    }
    return cfg

#Either download or write hardcode some default bdfr configs (a bit messy)
def get_bdfr_config():
    r = requests.get("https://raw.githubusercontent.com/aliparlakci/bulk-downloader-for-reddit/master/bdfr/default_config.cfg")
    logging.info("Downloading default config file from github")
    if r.status_code == 200:
        logging.info("Successfully acquired bdfr config from github")
        return bytes.decode(r.content)
    else:
        logging.info("Could not download, generated bdfr config instead")
        return """[DEFAULT]
        client_id = U-6gk4ZCh3IeNQ
        client_secret = 7CZHY6AmKweZME5s50SfDGylaPg
        scopes = identity, history, read, save
        backup_log_count = 3
        max_wait_time = 120
        time_format = ISO"""        
        
# Used in the jinja2 template
def float_to_datetime(value):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(value))

# Args > config file > defaults
def process_click_arguments(cfg, context: click.Context):
    defaults = generate_default_config()
    for arg_key in context.params.keys():
        if arg_key in cfg or arg_key in defaults: 
            if context.params[arg_key] is not None:
                cfg[arg_key] = context.params[arg_key]
            elif cfg[arg_key] is None:
                cfg[arg_key] = defaults[arg_key]
    return cfg