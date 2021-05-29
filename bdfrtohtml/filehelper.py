import shutil
import markdown
import subprocess
import jinja2
import json
import os
import logging
from bdfrtohtml import util
import pkgutil

logger = logging.getLogger(__name__)

templateLoader = jinja2.ChoiceLoader([jinja2.FileSystemLoader(searchpath="./bdfrtohtml/templates"), jinja2.PackageLoader('bdfrtohtml', 'templates')])
templateEnv = jinja2.Environment(loader=templateLoader)
templateEnv.add_extension('jinja2.ext.debug')
templateEnv.filters["markdown"] = markdown.markdown
templateEnv.filters["float_to_datetime"] = util.float_to_datetime


# Import all json files into single list.
def import_posts(folder):
    post_list = []
    for dirpath, dnames, fnames in os.walk(folder):
        for f in fnames:
            if f.endswith(".json"):
                data = load_json(os.path.join(dirpath, f))
                if data.get("id") is not None:
                    post_list.append(data)
                    logging.debug('Imported  ' + os.path.join(dirpath, f))
    return post_list


# Write index page
def write_index_file(post_list, output_folder):
    template = templateEnv.get_template("index.html")
    with open(os.path.join(output_folder, "index.html"), 'w', encoding="utf-8") as file:
        file.write(template.render(posts=post_list))
    logging.debug('Wrote ' + os.path.join(output_folder, "index.html"))


# Check for path, create if does not exist
def assure_path_exists(path):
    path = os.path.join(path, '')
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)
        logging.debug("Created " + dir)
    return dir


# Loads in the json file data and adds the path of it to the dict
def load_json(file_path):
    f = open(file_path, )
    data = json.load(f)
    f.close()
    logging.debug('Loaded ' + file_path)
    return data


# Copy media from the input folder to the file structure of the html pages
def copy_media(source_path, output_path):
    if output_path.endswith('mp4'):
        try:
            # This fixes mp4 files that won't play in browsers
            command = ['ffmpeg', '-nostats', '-loglevel', '0', '-i', source_path, '-c:v', 'copy',
                       '-c:a', 'copy', '-y', output_path]
            logging.debug("Running " + str(command))
            subprocess.call(command)
        except Exception as e:
            logging.error('FFMPEG failed: ' + str(e))
    else:
        shutil.copyfile(source_path, output_path)
    logging.debug('Moved ' + source_path + ' to ' + output_path)


# Search the input folder for media files containing the id value from an archive
def find_matching_media(post, input_folder, output_folder):
    paths = []
    media_folder = os.path.join(output_folder, 'media/')

    # Don't copy if we already have it
    existing_media = os.path.join(output_folder, "media/")
    for dirpath, dnames, fnames in os.walk(existing_media):
        for f in fnames:
            if post['id'] in f and not f.endswith('.json') and not f.endswith('.html'):
                logging.debug("Find Matching Media found: " + dirpath + f)
                paths.append(os.path.join('media/', f))
    if len(paths) > 0:
        logging.debug("Existing media found for " + post['id'])
        post['paths'] = paths
        return
    for dirpath, dnames, fnames in os.walk(input_folder):
        for f in fnames:
            if post['id'] in f and not f.endswith('.json'):
                logging.debug("Find Matching Media found: " + dirpath + f)
                logging.debug("Copying from")
                copy_media(os.path.join(dirpath, f), os.path.join(media_folder, f))
                paths.append(os.path.join('media/', f))
    post['paths'] = paths
    return post


# Creates the html for a post using the jinja2 template and writes it to a file
def write_post_to_file(post, output_folder):
    template = templateEnv.get_template("page.html")
    post['filename'] = post['id'] + ".html"
    post['filepath'] = os.path.join(output_folder, post['id'] + ".html")

    with open(post['filepath'], 'w', encoding="utf-8") as file:
        file.write(template.render(post=post))
    logging.debug('Wrote ' + post['filepath'])


# Write a list of successful ids to a file
def write_list_file(posts, output_folder):
    filepath = os.path.join(output_folder, "idList.txt")
    with open(filepath, 'w', encoding="utf-8") as file:
        for post in posts:
            file.write(post['id'] + '\n')


# Delete the contents of the input folder
def empty_input_folder(input_folder):
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            os.remove(os.path.join(root, file))
            logger.debug("Removed: " + os.path.join(root, file))
        for dir in dirs:
            shutil.rmtree(os.path.join(root, dir))
            logger.debug("Removed: " + os.path.join(root, dir))

def populate_css_file(output):
    css_output_path = os.path.join(output, 'style.css')
    css_input_path = './templates/style.css'
    if os.path.exists(css_input_path):
        shutil.copyfile(css_input_path, css_output_path)
    else:
        try:
            data = pkgutil.get_data(__name__, 'templates/style.css')
            with open(css_output_path, 'wb') as file:
                file.write(data)
        except Exception as e:
            logger.error(e)
           
