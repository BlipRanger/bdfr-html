import shutil
import markdown
import subprocess
import jinja2
import json
import os
import logging
from bdfrtohtml import util
import pkgutil
from PIL import Image

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
                    logging.debug(f'Imported  {os.path.join(dirpath, f)}')
    logging.info(f"Loaded {len(post_list)} json files.")
    return post_list


# Write index page
def write_index_file(post_list, output_folder, index_mode):
    template = templateEnv.get_template("index.html")
    with open(os.path.join(output_folder, "index.html"), 'w', encoding="utf-8") as file:
        file.write(template.render(posts=post_list, index_mode=index_mode))
    logging.debug(f'Wrote {os.path.join(output_folder, "index.html")}')


# Check for path, create if does not exist
def assure_path_exists(path):
    path = os.path.join(path, '')
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)
        logging.debug(f"Created {dir}")
    return dir


# Loads in the json file data and adds the path of it to the dict
def load_json(file_path):
    f = open(file_path, )
    data = json.load(f)
    f.close()
    logging.debug(f'Loaded {file_path}')
    return data


# Copy media from the input folder to the file structure of the html pages
def copy_media(source_path, output_path):
    if output_path.endswith('mp4'):
        try:
            # This fixes mp4 files that won't play in browsers
            command = ['ffmpeg', '-nostats', '-loglevel', '0', '-i', source_path, '-c:v', 'copy',
                       '-c:a', 'copy', '-y', output_path]
            logging.debug(f"Running {command}")
            subprocess.call(command)
        except Exception as e:
            logging.error('FFMPEG failed: ' + str(e))
    else:
        shutil.copyfile(source_path, output_path)
    logging.debug(f'Moved {source_path} to {output_path}')


# Search the input folder for media files containing the id value from an archive
def find_matching_media(post, input_folder, output_folder):
    paths = []
    media_folder = os.path.join(output_folder, 'media/')

    # Don't copy if we already have it
    existing_media = os.path.join(output_folder, "media/")
    for dirpath, dnames, fnames in os.walk(existing_media):
        for f in fnames:
            if post['id'] in f and not f.endswith('.json') and not f.endswith('.html'):
                logging.debug(f"Existing media found: {os.path.join(dirpath + f)}")
                paths.append(os.path.join('media/', f))
    if len(paths) > 0:
        logging.debug(f"Existing media found for {post['id']}")
        post['paths'] = paths
        return
    for dirpath, dnames, fnames in os.walk(input_folder):
        for f in fnames:
            if post['id'] in f and not f.endswith('.json'):
                logging.debug(f"New matching media found: {os.path.join(dirpath + f)}")
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
    logging.debug(f"Wrote {post['filepath']}")


# Write a list of successful ids to a file
def write_list_file(posts, output_folder):
    filepath = os.path.join(output_folder, "idList.txt")
    with open(filepath, 'w', encoding="utf-8") as file:
        for post in posts:
            file.write(post['id'] + '\n')

# Write a list of post urls to a file
def write_url_file(posts, output_folder, mode):
    filepath = os.path.join(output_folder, "urls.txt")
    with open(filepath, 'w', encoding="utf-8") as file:
        for post in posts:
            url = post.get('url')
            if url and mode == 'Webpages':
                if url.endswith('/'):
                    file.write(url + '\n')
            if url and mode == 'All':
                file.write(url + '\n')

# Delete the contents of the input folder
def empty_input_folder(input_folder):
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            os.remove(os.path.join(root, file))
            logger.debug(f"Deleted: {os.path.join(root, file)}")
        for dir in dirs:
            shutil.rmtree(os.path.join(root, dir))
            logger.debug(f"Deleted: {os.path.join(root, dir)}")

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

def generate_thumbnail(post, output_folder):

    thumbnail_folder = os.path.join(output_folder, "thumbnails/")
    assure_path_exists(thumbnail_folder)

    source_file = post.get('paths')
    if source_file is not None and len(source_file) == 1:
        source_file = os.path.join(output_folder, source_file[0])
        if source_file.endswith('mp4') or source_file.endswith('m4a'):
            filename = os.path.split(source_file)[1]
            filename = os.path.splitext(filename)[0] + "_thumb.jpg"
            output_path = os.path.join(thumbnail_folder, filename)
            if os.path.isfile(output_path):
                logging.debug(f"Using existing video thumbnail: {filename}")
                post['thumbnail'] = filename
                return post
            try:
                # Generate a thumbnail from the first frame
                command = ['ffmpeg', '-nostats', '-loglevel', '0', '-i', source_file, '-ss', 
                        '00:00:00', '-frames:v', '1', '-y', output_path]
                logging.debug(f"Running {command}")
                subprocess.call(command)
            except Exception as e:
                logging.error('FFMPEG thumbnail failed: ' + str(e))
            post['thumbnail'] = filename
            logging.debug(f'Generated {output_path}')
    return post


def generate_light_content(post, output_folder):
    thumbnail_content=['.m4a', '.mp4', '.jpg', '.jpeg', '.png', '.gif']
    thumbnail_folder = os.path.join(output_folder, "thumbnails/")
    light_folder = os.path.join(output_folder, 'light/')
    assure_path_exists(thumbnail_folder)
    assure_path_exists(light_folder)

    source_file = post.get('paths')
    if source_file is not None and len(source_file) > 0:
        ext = os.path.splitext(source_file[0])[1]
        if ext in thumbnail_content:
            source_file = source_file[0]

            if source_file.endswith('mp4') or source_file.endswith('m4a'):
                if post.get('thumbnail') is None:
                    post = generate_thumbnail(post, output_folder)
                source_file = os.path.join(thumbnail_folder, post.get('thumbnail'))
            else:
                source_file = os.path.join(output_folder, source_file)

            ext = os.path.splitext(source_file)[1]
            output_filename = post['id'] + '_light' + ext
            output_filepath = os.path.join(light_folder, output_filename)
            if os.path.isfile(output_filepath):
                logging.debug(f"Using existing thumbnail: {source_file}")
                post['light_content'] = os.path.join('light/', output_filename)
                return post

            logging.debug(f"Created: {source_file}")
            image = Image.open(source_file)
            image.thumbnail((300,300))
            image.save(output_filepath)
            post['light_content'] = os.path.join('light/', output_filename)
    return post
