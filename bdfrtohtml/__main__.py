# __main__.py

__author__ = "BlipRanger"
__version__ = "1.3.0"
__license__ = "GNU GPLv3"

import os
import markdown
from datetime import datetime
import click
import shutil
import logging

from bdfrtohtml import filehelper
from bdfrtohtml import posthelper
import logging
logger = logging.getLogger(__name__)


@click.command()
@click.option('--input', default='.', help='The folder where the download and archive results have been saved to')
@click.option('--output', default='./html/', help='Folder where the HTML results should be created.')
@click.option('--recover_comments', default=False, type=bool, help='Should we attempt to recover deleted comments?')
@click.option('--archive_context', default=False, type=bool, help='Should we attempt to archive the contextual post for saved comments?')
@click.option('--delete_input', default=False, type=bool, help='Should we delete the input after creating the output?')
def converter(input, output, recover_comments, archive_context, delete_input):

    filehelper.assure_path_exists(output)
    filehelper.assure_path_exists(os.path.join(output, "media/"))
    filehelper.assure_path_exists(input)

    #Load all of the json files
    allPosts = filehelper.importPosts(input)

    #Find the media for the files and append that to the entry
    for post in allPosts:
        filehelper.findMatchingMedia(post, input, output)
        posthelper.handleComments(post, archive_context)
        filehelper.writePostToFile(post, output)

    filehelper.writeIndexFile(allPosts, output)

    shutil.copyfile('style.css', os.path.join(output, 'style.css'))

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    converter()
