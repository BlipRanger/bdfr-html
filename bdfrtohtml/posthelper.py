__author__ = "BlipRanger"
__version__ = "1.3.0"
__license__ = "GNU GPLv3"

import logging
import subprocess
import requests
from bdfrtohtml import filehelper
import os
logger = logging.getLogger(__name__)

#Request a specific comment to be recovered
def recoverDeletedComment(comment):
    try:
        response = requests.get("https://api.pushshift.io/reddit/comment/search?ids={id}".format(id=comment['id']))
        data = response.json()['data']
        if len(data) == 1:
            revComment = data[0]
            comment['author'] = revComment['author']
            comment['body'] = revComment['body']
            comment['score'] = revComment['score']
            comment['recovered'] = True
            logging.info('Recovered ' + comment.get('id','') + ' from pushshift')
    except Exception as e:
        logging.error(e)
    return comment

#Recover deleted comments via pushshift
def recoverDeletedComments(post):
    for comment in post['comments']:
        if comment['body'] == "[deleted]":
            comment = recoverDeletedComment(comment)
        for reply in comment['replies']:
            if reply['body'] == "[deleted]":
                reply = recoverDeletedComment(reply)
    return post


#Requires bdfr V2
def getCommentContext(post, inputFolder):
    id = post.get("savedcomment")

    contextFolder = os.path.join(inputFolder,"context/")
    filehelper.assure_path_exists(contextFolder)

    if id is not None:
        try:
            subprocess.call(["python", "-m", "bdfr", "archive", "-l", post['permalink'], contextFolder])
            subprocess.call(["python", "-m", "bdfr", "download", "-l", post['permalink'], "--file-scheme", "{POSTID}", contextFolder])
        except Exception as e:
            logging.error(e)
        print(post['id'])
        for dirpath, dnames, fnames in os.walk(contextFolder):
            for f in fnames:
                print(f)
                if post['id'] in f and f.endswith('.json'):
                    print("Loaded")
                    post = filehelper.loadJson(os.path.join(dirpath, f))

        
        saved = next((c for c in post["comments"] if c['id'] == id))
        saved["is_saved"] = True  
    return post


#Convert comments into posts
def handleComments(comment, context):
    #Filter out posts
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

