# __main__.py

__author__ = "BlipRanger"
__version__ = "1.3.0"
__license__ = "GNU GPLv3"

import os
import click
import shutil
import logging
from bdfrtohtml import filehelper
from bdfrtohtml import posthelper
import logging
logger = logging.getLogger(__name__)


@click.command()
@click.option('--input', default='./', help='The folder where the download and archive results have been saved to')
@click.option('--output', default='./html/', help='Folder where the HTML results should be created.')
@click.option('--recover_comments', default=False, type=bool, help='Should we attempt to recover deleted comments?')
@click.option('--archive_context', default=False, type=bool, help='Should we attempt to archive the contextual post for saved comments?')
@click.option('--delete_input', default=False, type=bool, help='Should we delete the input after creating the output?')
def main(input, output, recover_comments, archive_context, delete_input):

    output = filehelper.assurePathExists(output)
    input = filehelper.assurePathExists(input) 
    filehelper.assurePathExists(os.path.join(output, "media/"))


    #Load all of the json files
    allPosts = filehelper.importPosts(input)

    #Find the media for the files and append that to the entry
    for post in allPosts:
        try:
            posthelper.handleComments(post, archive_context)
            if recover_comments: 
                post = posthelper.recoverDeletedComments(post)
            if archive_context: 
                post = posthelper.getCommentContext(post, input)

            filehelper.findMatchingMedia(post, input, output)
            filehelper.writePostToFile(post, output)
        except Exception as e:
            logging.error("Processing post " + post["id"] + " has failed due to: " + str(e))

    filehelper.writeIndexFile(allPosts, output)
    filehelper.writeListFile(allPosts, output)
    shutil.copyfile('style.css', os.path.join(output, 'style.css'))

    if delete_input:
        filehelper.emptyInputFolder(input)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
