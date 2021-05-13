__author__ = "BlipRanger"
__version__ = "1.3.0"
__license__ = "GNU GPLv3"

import logging
logger = logging.getLogger(__name__)

# #Recover deleted comments via pushshift
# def recoverDeletedComment(comment):
#     response = requests.get("https://api.pushshift.io/reddit/comment/search?ids={id}".format(id=comment.get('id','')))
#     data = response.json()['data']
#     if len(data) == 1:
#         revComment = data[0]
#         comment['author'] = revComment['author']
#         comment['body'] = revComment['body']
#         comment['score'] = revComment['score']
#         comment['recovered'] = 'recovered'
#         logging.debug('Recovered ' + comment.get('id','') + ' from pushshift')
#     return comment

# #Requires bdfr V2
# def archiveContext(link):
#     path = os.path.join(inputFolder, "context/")
#     assure_path_exists(path)
#     data={}
#     try:
#         subprocess.call(["python3.9", "-m", "bdfr", "archive", "-l", link, path])
#         subprocess.call(["python3.9", "-m", "bdfr", "download", "-l", link, "--file-scheme", "{POSTID}", path])
#     except:
#         logging.error("Failed to archive context")
#     for dirpath, dnames, fnames in os.walk(inputFolder + "context"):
#             for f in fnames:
#                 if f.endswith(".json"):
#                     data = helpers.loadJson(os.path.join(dirpath, f))
#                     data['htmlPath'] = writeToHTML(data)
#     shutil.rmtree(inputFolder + "context/")
#     return data['htmlPath']


#Convert comments into posts
def handleComments(comment, context):
    #Filter out posts
    if comment.get('parent_id') is None:
        return comment

    id = comment["id"]
    if context:
        post = getCommentContext(comment)
        saved = next((c for c in post["comments"] if c['id'] == id))
        saved["is_saved"] = True
    else:
        post = comment
        post["title"] = "Comment on " + post["submission_title"]
        post["comments"] = post["replies"]
        post["selftext"] = post["body"]
        post["permalink"] = "https://www.reddit.com/r/{subreddit}/comments/{submission}/{title}/{id}".format(
            subreddit=post["subreddit"], submission=post["submission"], title=post["title"], id=post["id"]
        )  

