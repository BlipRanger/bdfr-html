#!/usr/bin/env python3

__author__ = "BlipRanger"
__version__ = "0.1.2"
__license__ = "MIT"

import json
import os
import markdown
from datetime import datetime
import click
import shutil
import requests
import logging
import subprocess
import time

#Logging Setup
logging.basicConfig(level=logging.INFO)


#Globals
inputFolder = ''
outputFolder = ''
recoverComments = False
context = False

#Loads in the json file data and adds the path of it to the dict
def loadJson(file_path):
    f = open(file_path,)
    data = json.load(f)
    f.close()
    logging.debug('Loaded ' + file_path)
    return data

#Search the input folder for media files containing the id value from an archive
#Inputs: id name, folder to search
def findMatchingMedia(name, folder):
    paths = []
    for dirpath, dnames, fnames in os.walk(folder):
        for f in fnames:
            if (name) in f and not f.endswith('.json'):
                paths.append(copyMedia(os.path.join(dirpath, f), f))
    return paths

#Construct a rudamentary html image gallery from a list of image paths
#Note: Could be improved
def buildGallery(paths):
    html = '<div class=photoGrid><div class=row>'
    for p in paths:
        html = html + """<div class=column><a href={path}><img src={path} style="width:100%"></a></div>""".format(path=p)
    html = html + """</div></div>"""
    return html

#Extract/convert markdown from saved selfpost
def parseSelfPost(filePath):
    txt = '<div>'
    with open(filePath, 'r') as file:
        content = file.read()
    file.close()
    #Strip first and last lines
    content = content[content.find('\n')+1:content.rfind('\n')]
    return markdown.markdown(content)

#Handle the html formatting for images, videos, and text files
#Input: list of paths to media
def formatMatchingMedia(paths):
    if paths is None:
        return ""
    if len(paths) == 1:
        path = paths[0]

        if path.endswith('jpg') or path.endswith('jpeg') or path.endswith('png') or path.endswith('gif'):
            return '<a href={path}><img src={path}></a>'.format(path=path)
        elif path.endswith('m4a') or path.endswith('mp4') or path.endswith('mkv'):
            return '<video max-height="500" controls><source src="{path}"></video>'.format(path=path)
        elif path.endswith('txt'):
            return parseSelfPost(os.path.join(outputFolder, path))
    elif(len(paths) > 1):
        return buildGallery(paths)
    return ""

#Copy media from the input folder to the file structure of the html pages
def copyMedia(mediaPath, filename):
    writeFolder = os.path.join(outputFolder, 'media/')
    assure_path_exists(writeFolder)
    if filename.endswith('mp4'):
        try:
            #This fixes mp4 files that won't play in browsers
            os.system("ffmpeg -nostats -loglevel 0 -i {input} -c:v copy -c:a copy -y {output}".format(input=mediaPath, output=(writeFolder + filename)))
        except:
            logging.error('FFMPEG failed')
    else:
        shutil.copyfile(mediaPath, writeFolder + filename)
    logging.debug('Moved ' + mediaPath + ' to ' + writeFolder +filename)
    return 'media/' + filename

#Handle writing replies to comments
#Uses the writeTopLevelComment function to unroll comment/reply chains
def writeReplies(comment, data):
    html = ''
    if not comment['replies']:
        return ''
    for replies in comment['replies']:
        html = html + writeTopLevelComment(replies, data)
    return html

#Convert unix time string to datetime
def writeDatestring(time):
    time = int(time)
    return datetime.utcfromtimestamp(time).strftime('%H:%M:%S - %Y-%m-%d')

#Recover deleted comments via pushshift
def recoverDeletedComment(comment):
    response = requests.get("https://api.pushshift.io/reddit/comment/search?ids={id}".format(id=comment.get('id','')))
    data = response.json()['data']
    if len(data) == 1:
        revComment = data[0]
        comment['author'] = revComment['author']
        comment['body'] = revComment['body']
        comment['score'] = revComment['score']
        comment['recovered'] = 'recovered'
        logging.debug('Recovered ' + comment.get('id','') + ' from pushshift')
    return comment

#Requires bdfr V2
def archiveContext(link):
    path = os.path.join(inputFolder, "context/")
    assure_path_exists(path)
    data={}
    try:
        subprocess.call(["python3.9", "-m", "bdfr", "archive", "-l", link, path])
        subprocess.call(["python3.9", "-m", "bdfr", "download", "-l", link, "--file-scheme", "{POSTID}", path])
    except:
        logging.error("Failed to archive context")
    for dirpath, dnames, fnames in os.walk(inputFolder + "context"):
            for f in fnames:
                if f.endswith(".json"):
                    data = loadJson(os.path.join(dirpath, f))
                    data['htmlPath'] = writeToHTML(data)
    shutil.rmtree(inputFolder + "context/")
    return data['htmlPath']


#Generate the html for a comment
def writeTopLevelComment(comment, data):
    if not comment:
        return ''
    if recoverComments and (comment.get('author', '') == 'DELETED' or comment.get('body', '') == '[removed]'):
        comment = recoverDeletedComment(comment) 
    return """<div id={id} class="comment">
    <div class="info {recovered}">
    <a href="https://www.reddit.com{commentLink}"><div class="time">{created}</div></a>
    <div class="score">({score})</div>
    <div class=author>u/{author}</div></div>
    <p>{body}</p><div class=reply>{replies}</div></div>""".format(body=markdown.markdown(comment['body']), 
    created=writeDatestring(comment['created_utc']), score=comment['score'], author=comment['author'],
     id=comment['id'], replies=writeReplies(comment, data), commentLink=data.get('permalink','') + comment['id'],
     recovered=comment.get('recovered', ''))


#Generate the html for the html head/page start
def writeHead():
    return """<html>
            <head>
            <style>body {background-color: rgb(35, 35, 35);}</style>
            <link rel='stylesheet' type='text/css' href='style.css'>
            <meta charset="utf-8"/>
            </head><body>"""

#Write the html body of a given post 
#Input: dict created from the json file
def writePost(data):
    matchingMedia = findMatchingMedia(data['id'], inputFolder)
    content = formatMatchingMedia(matchingMedia)

    if len(matchingMedia) == 0:
        local_link = ''
    else:
        local_link = matchingMedia[0]

    return """
        <div class=post>
            <h1>{title}</h1>
            <div class="info">
                <div class="links">
                    <a href="{local_link}"> link</a> <a href="{link}">Content link</a> <a href="https://www.reddit.com{url}"> Reddit Link</a> 
                </div>
                <time>{time}</time><a href='https://reddit.com/{subreddit}'><span class="subreddit">{subreddit}</span></a><a href='https://reddit.com/u/{user}'><span class="user">u/{user}</span></a>
            </div>
            <div class=content>{content}</div>
            
        </div>

        """.format(time=writeDatestring(data.get('created_utc', '1616957979')), local_link=local_link, submission=data.get('id', ''),
         content=content, url=data.get('permalink', ''), link=data.get('url',''), title=data.get('title',''), user=data.get('author', ''),
         subreddit=getSubreddit(data.get('permalink', '')))

#Function to write a saved comment in a 'post' format
def writeCommentPost(comment):
    if not comment:
        return ''
    if recoverComments and (comment.get('author', '') == 'DELETED' or comment.get('body', '') == '[removed]'):
        comment = recoverDeletedComment(comment) 

    #Generate Permalink
    permalink = 'https://www.reddit.com/r/{subreddit}/comments/{submission}/{title}/{id}'.format(id=comment['id'],
     submission=comment['submission'], title=comment['submission_title'], subreddit=comment['subreddit'])

    contextLink = ''
    if context:
        contextLink = archiveContext(permalink)

    return """
        <div class="post">
            <h1>Comment on {title}</h1>
            <div class="info {recovered}">
                <div class="links">
                    <a href="{url}"> Reddit Link</a><a href={contextLink}>Context Link</a> 
                </div>
                <time>{time}</time><a href='https://reddit.com/r/{subreddit}'><span class="subreddit">{subreddit}</span></a><a href='https://reddit.com/u/{user}'><span class="user">u/{user}</span></a>
            </div>
            <div class=content>{content}</div>
            
        </div>

        """.format(time=writeDatestring(comment.get('created_utc', '1616957979')), submission=comment.get('id', ''),
         content=markdown.markdown(comment.get('body', '')), url=permalink, link=permalink, title=comment.get('submission_title',''), user=comment.get('author', ''),
         subreddit=comment.get('subreddit', ''), recovered=comment.get('recovered', ''), contextLink=contextLink)
             

#Extract the subreddit name from the permalink
def getSubreddit(permalink):
    strings = permalink.split("/")
    return strings[1] + '/' + strings[2]

#Write html file from given post archive info
def writeToHTML(data):
    file_path = data['id'] + '.html'
    path = os.path.join(outputFolder, file_path)
    with open(path, 'w') as file:
        html = writeHead()
        if data.get('parent_id', None) is None:
            html = html + writePost(data) + "<h2>Comments</h2><div class=comments>"
            for c in data['comments']:
                html = html + writeTopLevelComment(c, data)

                html = html + """</div></body>
                        </html>"""    
        else:
            html = html + writeCommentPost(data) + "<h2>Comments</h2><div class=comments>"
            for c in data['replies']:
                html = html + writeTopLevelComment(c, data)

                html = html + """</div></body>
                        </html>"""
        file.write(html)
    return file_path

#Check for path, create if does not exist
def assure_path_exists(path):
        dir = os.path.dirname(path)
        if not os.path.exists(dir):
                os.makedirs(dir)

#Main function, loops through json files in input folder, extracts archive data into dict, 
#formats/writes archive data and media to html files, creates a single index.html file with 
#links to all archived posts. 
def main():
    
    #Begin main process
    datalist = []

    file_path = os.path.join(outputFolder, 'idList.txt')
    if os.path.isfile(file_path):
        with open(file_path, 'r') as f:
            datalist = list(f)
    
    assure_path_exists(outputFolder)
    if not os.path.isdir(inputFolder):
        raise ValueError('Input folder does not exist') 
    html = writeHead()
    postCount = 0
    pageCount = 1
    for dirpath, dnames, fnames in os.walk(inputFolder):
        for f in fnames:
            if f.endswith(".json"):
                data = loadJson(os.path.join(dirpath, f))
                #Only do this if we haven't already
                if data['id'] not in datalist:
                    data['htmlPath'] = writeToHTML(data)
                    if postCount == 25:
                        file_path = os.path.join(outputFolder, 'page{pageCount}.html'.format(pageCount=pageCount))
                        with open(file_path, 'w') as file:
                            html = html + """<div class=footer><div class=previousPage><a href='page{previous}.html'>Previous Page</a></div>
                            <div class=nextPage><a href='page{next}.html'>Next Page</a></div></div>
                            </body>
                    </html>""".format(previous=pageCount-1, next=pageCount+1)
                            file.write(html)
                        html = writeHead()
                        pageCount = pageCount + 1
                        postCount = 0
                    if data.get('parent_id', None) is None:
                        html = html + '<a href={local_path}>{post}</a>'.format(post=writePost(data), local_path=data['htmlPath'])
                    else:
                        html = html + '<a href={local_path}>{post}</a>'.format(post=writeCommentPost(data), local_path=data['htmlPath'])
                    postCount = postCount + 1
                    datalist.append(data['id'] + "\n")

    file_path = os.path.join(outputFolder, 'page{pageCount}.html'.format(pageCount=pageCount))
    with open(file_path, 'w') as file:
        html = html + """<div class=footer><div class=previousPage><a href='page{previous}.html'>Previous Page</a></div>
                         <div class=nextPage><a href='page{next}.html'>Next Page</a></div></div>
                         </body>
                </html>""".format(previous=pageCount-1, next=pageCount+1)
        file.write(html)
    html = writeHead()


    file_path = os.path.join(outputFolder, 'index.html')
    with open(file_path, 'w') as file:
        html = html + """
        <meta http-equiv="refresh" content="0; URL='page1.html'" /></div></body>
                </html>"""    
        file.write(html)

    file_path = os.path.join(outputFolder, 'idList.txt')
    with open(file_path, 'w') as file:
        file.writelines(datalist)

    shutil.copyfile('style.css', os.path.join(outputFolder, 'style.css'))
    logging.info("Run Complete!")


@click.command()
@click.option('--input', default='.', help='The folder where the download and archive results have been saved to')
@click.option('--output', default='./html/', help='Folder where the HTML results should be created.')
@click.option('--recover_comments', default=False, help='Should we attempt to recover deleted comments?')
@click.option('--archive_context', default=False, help='Should we attempt to archive the contextual post for saved comments?')
@click.option('--watch_folder', default=False, help='After the first run, watch the input folder for changes and rerun when detected')
@click.option('--watch_freq', default=1, help='How often should we recheck the watched input folder in minutes. Requires watch_folder be enabled')

def converter(input, output, recover_comments, archive_context, watch_folder, watch_freq):
    global inputFolder
    global outputFolder
    global recoverComments
    global context

    #Set globals (there is probably a better way to do this)
    inputFolder = os.path.join(input, '')
    outputFolder = os.path.join(output, '')
    recoverComments = recover_comments
    context = archive_context

    #Simple watch function
    if watch_folder:
        oldContent = []
        logging.info("Watching...")
        while True:
            content = []
            for dirpath, dnames, fnames in os.walk(inputFolder):
                for f in fnames:
                    content.append(f)
                for d in dnames:
                    content.append(d)
            if content != oldContent:
                logging.info("Content found!")
                main()
            else:
                logging.info("Nothing new, sleeping for " + str(watch_freq) + " minutes.")
                time.sleep(watch_freq * 60)
            oldContent = content
    else:
        main()


if __name__ == '__main__':
    converter()
