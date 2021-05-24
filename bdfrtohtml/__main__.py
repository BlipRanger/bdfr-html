# __main__.py

__author__ = "BlipRanger"
__version__ = "1.3.1"
__license__ = "GNU GPLv3"

import os
import click
import shutil
from bdfrtohtml import filehelper
from bdfrtohtml import posthelper
import logging
import copy

logger = logging.getLogger(__name__)


@click.command()
@click.option('--input', default='./', help='The folder where the download and archive results have been saved to')
@click.option('--output', default='./html/', help='Folder where the HTML results should be created.')
@click.option('--recover_comments', default=False, type=bool, help='Should we attempt to recover deleted comments?')
@click.option('--recover_posts', default=False, type=bool, help='Should we attempt to recover deleted posts?')
@click.option('--generate_thumbnails', default=True, type=bool, help='Generate thumbnails for video posts?')
@click.option('--archive_context', default=False, type=bool,
              help='Should we attempt to archive the contextual post for saved comments?')
@click.option('--delete_input', default=False, type=bool, help='Should we delete the input after creating the output?')
@click.option('--write_links_to_file', default='None', type=click.Choice(['None', 'Webpages', 'All'], case_sensitive=False), 
              help='Should we write the links from posts to a text file for external consuption?')
def main(input, output, recover_comments, recover_posts, generate_thumbnails, archive_context, delete_input, write_links_to_file):
    output = filehelper.assure_path_exists(output)
    input = filehelper.assure_path_exists(input)
    filehelper.assure_path_exists(os.path.join(output, "media/"))

    # Load all of the json files
    all_posts = filehelper.import_posts(input)
    posts_to_write = []

    # Find the media for the files and append that to the entry
    for entry in all_posts:
        post = copy.deepcopy(entry)
        try:
            post = posthelper.handle_comments(post)
            if recover_comments:
                post = posthelper.recover_deleted_comments(post)
            if archive_context:
                post = posthelper.get_comment_context(post, input)
            if recover_posts:
                post = posthelper.recover_deleted_posts(post)
                
            post = posthelper.get_sub_from_post(post)
            filehelper.find_matching_media(post, input, output)
            filehelper.write_post_to_file(post, output)
            posts_to_write.append(post)
        except Exception as e:
            logging.error(f"Processing post {post['id']} has failed due to: {str(e)}")

    posts_to_write = sorted(posts_to_write, key=lambda d: d['created_utc'], reverse=True)
    filehelper.write_index_file(posts_to_write, output)
    filehelper.write_list_file(posts_to_write, output)
    shutil.copyfile('./templates/style.css', os.path.join(output, 'style.css'))

    if write_links_to_file != "None":
        filehelper.write_url_file(posts_to_write, output, write_links_to_file)
    if archive_context:
        filehelper.empty_input_folder(os.path.join(input, "context/"))
    if delete_input:
        filehelper.empty_input_folder(input)
    if generate_thumbnails:
        filehelper.generate_thumbnails(posts_to_write, output)


    logging.info("BDFR-HTML run complete.")


if __name__ == '__main__':
    LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
    logging.basicConfig(level=LOGLEVEL)
    main()
