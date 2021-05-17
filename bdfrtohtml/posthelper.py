__author__ = "BlipRanger"
__version__ = "1.3.0"
__license__ = "GNU GPLv3"

import logging
import subprocess
import requests
from bdfrtohtml import filehelper
import os

logger = logging.getLogger(__name__)


# Request a specific comment to be recovered
def recover_deleted_comment(comment):
    try:
        response = requests.get("https://api.pushshift.io/reddit/comment/search?ids={id}".format(id=comment['id']))
        data = response.json()['data']
        if len(data) == 1:
            rev_comment = data[0]
            comment['author'] = rev_comment['author']
            comment['body'] = rev_comment['body']
            comment['score'] = rev_comment['score']
            comment['recovered'] = True
            logging.info('Recovered ' + comment.get('id', '') + ' from pushshift')
    except Exception as e:
        logging.error(e)
    return comment


# Recover deleted comments via pushshift
def recover_deleted_comments(post):
    for comment in post['comments']:
        if comment['body'] == "[deleted]":
            comment = recover_deleted_comment(comment)
        for reply in comment['replies']:
            if reply['body'] == "[deleted]":
                reply = recover_deleted_comment(reply)
    return post


# Requires bdfr V2
# Use BDFR to download both the archive and media for a given post
def get_comment_context(post, input_folder):
    id = post.get("savedcomment")

    context_folder = os.path.join(input_folder, "context/")
    filehelper.assure_path_exists(context_folder)

    if id is not None:
        try:
            subprocess.call(["python", "-m", "bdfr", "archive", "-l", post['permalink'], context_folder])
            subprocess.call(["python", "-m", "bdfr", "download", "-l", post['permalink'], "--file-scheme", "{POSTID}",
                             context_folder])
        except Exception as e:
            logging.error(e)
        print(post['id'])
        for dirpath, dnames, fnames in os.walk(context_folder):
            for f in fnames:
                print(f)
                if post['id'] in f and f.endswith('.json'):
                    print("Loaded")
                    post = filehelper.load_json(os.path.join(dirpath, f))

        for comment in post["comments"]:
            if comment["id"] == id:
                comment["is_saved"] = True
                break
            for reply in comment["replies"]:
                if reply["id"] == id:
                    reply["is_saved"] = True
                    break

    return post


# Convert comments into posts
def handle_comments(comment):
    # Filter out posts
    if comment.get('parent_id') is None:
        return comment

    post = comment
    post["title"] = "Comment on " + post["submission_title"]
    post["savedcomment"] = comment['id']
    post["id"] = comment['submission']
    post["comments"] = post["replies"]
    post["selftext"] = post["body"]
    post["permalink"] = "https://www.reddit.com/r/{subreddit}/comments/{submission}/{title}/{id}".format(
        subreddit=post["subreddit"], submission=post["submission"], title=post["title"], id=post["id"]
    )
