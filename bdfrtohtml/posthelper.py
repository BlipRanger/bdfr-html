import logging
import subprocess
import requests
from bdfrtohtml import filehelper
import os
import sys

logger = logging.getLogger(__name__)

#Get subreddit name from post
def get_sub_from_post(post):
    if post.get('subreddit') is None:
        link = post['permalink']
        post['subreddit'] = link.split('/')[2]
    return post

# Recover deleted posts via pushshift
def recover_deleted_posts(post):
    if post['selftext'] == '[deleted]':
        post = recover_deleted_post(post)
    return post

# Request a specific post to be recovered
def recover_deleted_post(post):
    try:
        response = requests.get("https://api.pushshift.io/reddit/submission/search?ids={id}".format(id=post['id']))
        data = response.json()['data']
        logger.debug(data)
        logger.debug(len(data))
        if len(data) == 1:
            recovered_post = data[0]
            post['selftext'] = recovered_post['selftext']
            post['author'] = recovered_post['author']
            post['url'] = recovered_post['url']
            post['recovered'] = True
            logging.info(f"Recovered {post.get('id', '')} from pushshift")
    except Exception as e:
        logging.error(e)
    return post


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
            logging.info(f"Recovered {comment.get('id', '')} from pushshift")
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
            subprocess.call([sys.executable, "-m", "bdfr", "clone", "-l", post['permalink'], "--file-scheme", "{POSTID}",
                             context_folder])
        except Exception as e:
            logging.error(e)
        for dirpath, dnames, fnames in os.walk(context_folder):
            for f in fnames:
                if post['id'] in f and f.endswith('.json'):
                    post = filehelper.load_json(os.path.join(dirpath, f))
                    logging.debug(f"Post context created for: {post['id']}")

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

    comment["title"] = "Comment on " + comment["submission_title"]
    comment["savedcomment"] = comment['id']
    comment["id"] = comment['submission']
    comment["comments"] = comment["replies"]
    comment["selftext"] = comment["body"]
    comment["permalink"] = "https://www.reddit.com/r/{subreddit}/comments/{submission}/{title}/{id}".format(
        subreddit=comment["subreddit"], submission=comment["submission"], title=comment["title"], id=comment["id"]
    )
    return comment
