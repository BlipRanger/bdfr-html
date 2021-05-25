import time
import yaml
import click

# Load in a yaml config file
def load_config(config_file):
    cfg = yaml.safe_load(config_file).get('bdfrhtml')
    return cfg

# Default settings
def generate_default_config():
  cfg = {
    'recover_comments': False,      
    'recover_posts': False, 
    'output_folder': './output',
    'input_folder': './input', 
    'archive_context': False,           
    'delete_media': False,                                  
    'write_links_to_file': 'None',
    'generate_thumbnails': False
  }
  return cfg

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