#!/usr/bin/env python3

__author__ = "BlipRanger"
__version__ = "0.1.0"
__license__ = "MIT"

import json
import os
import markdown
from datetime import datetime
import click
import shutil

#Globals
inputFolder = ''
outputFolder = ''

#Loads in the json file data and adds the path of it to the dict
def loadJson(file_path):
    f = open(file_path,)
    data = json.load(f)
    f.close()
    data['htmlPath'] = writeToHTML(data)
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

#Handle the html formatting for images, videos, and text files
#Input: list of paths to media
def formatMatchingMedia(paths):
    if paths is None:
        return ""
    if len(paths) == 1:
        path = paths[0]

        if path.endswith('jpg') or path.endswith('jpeg') or path.endswith('png'):
            return '<a href={path}><img src={path}></a>'.format(path=path)
        elif path.endswith('m4a') or path.endswith('mp4') or path.endswith('mkv'):
            return '<video width="320" height="240" controls><source src="{path}"></video>'.format(path=path)
        elif path.endswith('txt'):
            txt = '<div>'
            with open(outputFolder + path, 'r') as file:
                lines = file.readlines()
            file.close()
            for l in lines[1:]:
                if l == '---\n':
                    return (txt + '</div>')
                else:
                    txt = txt + l
            return markdown.markdown(txt)
    elif(len(paths) > 1):
        return buildGallery(paths)
    return ""

#Copy media from the input folder to the file structure of the html pages
def copyMedia(mediaPath, filename):
    writeFolder = outputFolder + 'media/' 
    assure_path_exists(writeFolder)
    shutil.copyfile(mediaPath, writeFolder + filename)
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

#Generate the html for a comment
def writeTopLevelComment(comment, data):
    if not comment:
        return ''
    return """<div id={id} class="comment">
    <div class="info">
    <a href="https://www.reddit.com{commentLink}"><div class="time">{created}</div></a>
    <div class="score">({score})</div>
    <div class=author>u/{author}</div></div>
    <p>{body}</p><div class=reply>{replies}</div></div>""".format(body=markdown.markdown(comment['body']), 
    created=writeDatestring(comment['created_utc']), score=comment['score'], author=comment['author'],
     id=comment['id'], replies=writeReplies(comment, data), commentLink=data.get('permalink','') + comment['id'])


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

        """.format(time=writeDatestring(data.get('time', '1616957979')), local_link=local_link, submission=data.get('id', ''),
         content=content, url=data.get('permalink', ''), link=data.get('url',''), title=data.get('title',''), user=data.get('author', ''),
         subreddit=getSubreddit(data.get('permalink', '')))

#Function to write a saved comment in a 'post' format
def writeCommentPost(comment):
    if not comment:
        return ''
    #Generate Permalink
    permalink = 'https://www.reddit.com/r/{subreddit}/comments/{submission}/{title}/{id}'.format(id=comment['id'],
     submission=comment['submission'], title=comment['submission_title'], subreddit=comment['subreddit'])

    return """
        <div class=post>
            <h1>Comment on {title}</h1>
            <div class="info">
                <div class="links">
                    <a href="{url}"> Reddit Link</a> 
                </div>
                <time>{time}</time><a href='https://reddit.com/{subreddit}'><span class="subreddit">{subreddit}</span></a><a href='https://reddit.com/u/{user}'><span class="user">u/{user}</span></a>
            </div>
            <div class=content>{content}</div>
            
        </div>

        """.format(time=writeDatestring(comment.get('created_utc', '1616957979')), submission=comment.get('id', ''),
         content=markdown.markdown(comment.get('body', '')), url=permalink, link=permalink, title=comment.get('submission_title',''), user=comment.get('author', ''),
         subreddit=comment.get('subreddit', ''))
             

#Extract the subreddit name from the permalink
def getSubreddit(permalink):
    strings = permalink.split("/")
    return strings[1] + '/' + strings[2]

#Write html file from given post archive info
def writeToHTML(data):
    file_path = data['id'] + '.html'
    with open(outputFolder + file_path, 'w') as file:
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
@click.command()
@click.option('--input', default='.', help='The folder where the download and archive results have been saved to')
@click.option('--output', default='./html/', help='Folder where the HTML results should be created.')
def converter(input, output):
    global inputFolder
    global outputFolder
    inputFolder = input
    outputFolder = output
    assure_path_exists(output)
    html = writeHead()

    for dirpath, dnames, fnames in os.walk(input):
        for f in fnames:
            if f.endswith(".json"):
                data = loadJson(os.path.join(dirpath, f))
                if data.get('parent_id', None) is None:
                    html = html + '<a href={local_path}>{post}</a>'.format(post=writePost(data), local_path=data['htmlPath'])
                else:
                    html = html + '<a href={local_path}>{post}</a>'.format(post=writeCommentPost(data), local_path=data['htmlPath'])

    file_path = output + '/index.html'

    with open(file_path, 'w') as file:
        html = html + """</body>
                </html>"""    
        file.write(html)
    shutil.copyfile('style.css', outputFolder + 'style.css')

if __name__ == '__main__':
    converter()
