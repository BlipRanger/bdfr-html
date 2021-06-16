# __main__.py

__author__ = "BlipRanger"
__version__ = "1.4.1"
__license__ = "GNU GPLv3"

import os
import click
import shutil
from bdfrtohtml import filehelper
from bdfrtohtml import posthelper
from bdfrtohtml import automation
from bdfrtohtml import util
import logging
import copy

logger = logging.getLogger(__name__)

@click.group(invoke_without_command=True)
@click.option('--input_folder', default=None, help='The folder where the download and archive results have been saved to')
@click.option('--output_folder', default=None, help='Folder where the HTML results should be created.')
@click.option('--recover_comments', type=bool, help='Should we attempt to recover deleted comments?')
@click.option('--recover_posts', type=bool, help='Should we attempt to recover deleted posts?')
@click.option('--generate_thumbnails', type=bool, help='Generate thumbnails for video posts?')
@click.option('--archive_context', type=bool,
              help='Should we attempt to archive the contextual post for saved comments?')
@click.option('--delete_media', type=bool, help='Should we delete the input media after creating the output?')
@click.option('--index_mode', type=click.Choice(['default', 'lightweight', 'oldreddit']), help='Generate an index with no playing media and shrunk images?')
@click.option('--write_links_to_file', type=click.Choice(['None', 'Webpages', 'All'], case_sensitive=False), 
              help='Should we write the links from posts to a text file for external consuption?')
@click.option('--config', type=click.File('r'), help='Read in a config file')
@click.pass_context
def main(context: click.Context, **_):

    if context.invoked_subcommand is not None:
        return
    if context.params.get('config'):
        config = util.load_config(context.params.get('config'))
    else:
        config = util.generate_default_config()["bdfrhtml"]
    config = util.process_click_arguments(config, context)
    logging.debug(config)

    output = filehelper.assure_path_exists(config['output_folder'])
    input = filehelper.assure_path_exists(config['input_folder'])
    filehelper.assure_path_exists(os.path.join(output, "media/"))
    

    # Load all of the json files
    all_posts = filehelper.import_posts(input)
    posts_to_write = []

    # Find the media for the files and append that to the entry
    for entry in all_posts:
        post = copy.deepcopy(entry)
        try:
            post = posthelper.handle_comments(post)
            if config['recover_comments']:
                post = posthelper.recover_deleted_comments(post)
            if config['archive_context']:
                post = posthelper.get_comment_context(post, input)
            if config['recover_posts']:
                post = posthelper.recover_deleted_posts(post)
                
            post = posthelper.get_sub_from_post(post)
            filehelper.find_matching_media(post, input, output)

            if config['generate_thumbnails']:
                filehelper.generate_thumbnail(post, output)
            if config['index_mode'] != "default":
                filehelper.generate_light_content(post, output)
                
            filehelper.write_post_to_file(post, output)
            posts_to_write.append(post)
        except Exception as e:
            logging.error(f"Processing post {post['id']} has failed due to: {str(e)}")

    posts_to_write = sorted(posts_to_write, key=lambda d: d['created_utc'], reverse=True)

    filehelper.write_index_file(posts_to_write, output, config['index_mode'])
    filehelper.write_list_file(posts_to_write, output)
    filehelper.populate_css_file(output)


    if config['write_links_to_file'] != "None":
        filehelper.write_url_file(posts_to_write, output, config['write_links_to_file'])
    if config['archive_context']:
        filehelper.empty_input_folder(os.path.join(input, "context/"))
    if config['delete_media']:
        filehelper.empty_input_folder(input)


    logging.info("BDFR-HTML run complete.")

@main.command("automate")
@click.option('--generate_config', type=bool, default=False, help='Just generate the config files for automation')
def run_automation(generate_config):
    if generate_config:
        automation.generate_configs()
    else:
        automation.automate()


if __name__ == '__main__':
    LOGLEVEL = os.environ.get('BDFRH_LOGLEVEL', 'INFO').upper()
    logging.basicConfig(level=LOGLEVEL)
    main()
