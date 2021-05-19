# __main__.py

__author__ = "BlipRanger"
__version__ = "1.3.0"
__license__ = "GNU GPLv3"

import os
import click
import shutil
from bdfrtohtml import filehelper
from bdfrtohtml import posthelper
import logging

logger = logging.getLogger(__name__)


@click.command()
@click.option('--input', default='./', help='The folder where the download and archive results have been saved to')
@click.option('--output', default='./html/', help='Folder where the HTML results should be created.')
@click.option('--recover_comments', default=False, type=bool, help='Should we attempt to recover deleted comments?')
@click.option('--archive_context', default=False, type=bool,
              help='Should we attempt to archive the contextual post for saved comments?')
@click.option('--delete_input', default=False, type=bool, help='Should we delete the input after creating the output?')
def main(input, output, recover_comments, archive_context, delete_input):
    output = filehelper.assure_path_exists(output)
    input = filehelper.assure_path_exists(input)
    filehelper.assure_path_exists(os.path.join(output, "media/"))

    # Load all of the json files
    all_posts = filehelper.import_posts(input)

    # Find the media for the files and append that to the entry
    for post in all_posts:
        try:
            posthelper.handle_comments(post)
            if recover_comments:
                post = posthelper.recover_deleted_comments(post)
            if archive_context:
                post = posthelper.get_comment_context(post, input)

            filehelper.find_matching_media(post, input, output)
            filehelper.write_post_to_file(post, output)
        except Exception as e:
            logging.error("Processing post " + post["id"] + " has failed due to: " + str(e))

    filehelper.write_index_file(all_posts, output)
    filehelper.write_list_file(all_posts, output)
    shutil.copyfile('./templates/style.css', os.path.join(output, 'style.css'))

    if delete_input:
        filehelper.empty_input_folder(input)
    logging.info("BDFRToHTML run complete.")


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
