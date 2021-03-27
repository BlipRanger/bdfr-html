import json
import os
import markdown
from datetime import datetime
import click


workingDir = './posts'
rootDir = os.getcwd()
outputDir = rootDir + '/html'

def jsonToHTML(file_path):
    f = open(file_path,)
    data = json.load(f)
    f.close()
    data['htmlPath'] = writeToHTML(data)
    return data


def findMatchingMedia(name):
    paths = []
    for dirpath, dnames, fnames in os.walk(workingDir):
        for f in fnames:
            if (name) in f and not f.endswith('.json'):
                paths.append(os.path.join(dirpath, f))
    return paths


def buildGallery(paths):
    html = '<div class=photoGrid><div class=row>'
    for p in paths:
        p = '.' + p
        html = html + """<div class=column><a href={path}><img src={path} style="width:100%"></a></div>""".format(path=p)
    html = html + """</div></div>"""
    return html

def formatMatchingMedia(paths):
    if paths is None:
        return ""
    if len(paths) == 1:
        path = paths[0]

        if path.endswith('jpg') or path.endswith('jpeg') or path.endswith('png'):
            path = '.' + path
            return '<a href={path}><img src={path}></a>'.format(path=path)
        elif path.endswith('m4a') or path.endswith('mp4') or path.endswith('mkv'):
            path = '.' + path
            return '<video width="320" height="240" controls><source src="{path}"></video>'.format(path=path)
        elif path.endswith('txt'):
            txt = '<div>'
            with open(path, 'r') as file:
                lines = file.readlines()
            file.close()
            for l in lines[1:]:
                print(l)
                if l == '---\n':
                    return (txt + '</div>')
                else:
                    txt = txt + l
            return markdown.markdown(txt)
    elif(len(paths) > 1):
        return buildGallery(paths)
    return ""


def writeReplies(comment, data):
    html = ''
    if not comment['replies']:
        return ''
    for replies in comment['replies']:
        html = html + writeTopLevelComment(replies, data)
    return html

def writeDatestring(time):
    time = int(time)
    return datetime.utcfromtimestamp(time).strftime('%H:%M:%S - %Y-%m-%d')

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
     id=comment['id'], replies=writeReplies(comment, data), commentLink=data['permalink'] + comment['id'])

def writeHead():
    return """<html>
            <head>
            <link rel='stylesheet' type='text/css' href='style.css'>
            <meta charset="utf-8"/>
            </head><body>"""

def writePost(data):
    return """
        <div class=post>
        <h1>{title}</h1>
        <div class="info">
        <div class="links">
        <a href=".{local_link}">content link</a> <a href="{link}">reddit link</a> | <a href="https://www.reddit.com{url}"></a></div>
        </div>
        <div class=content>{content}</p></div>
        </div>

        """.format(local_link=findMatchingMedia(data['id'])[0], submission=data.get('id', ''), content=formatMatchingMedia(findMatchingMedia(data['id'])), url=data.get('permalink', ''), link=data.get('url',''), title=data.get('title',''))

def writeToHTML(data):
    file_path = './html/' + data['id'] + '.html'
    with open(file_path, 'w') as file:
        html = writeHead()
        html = html + writePost(data) + "<h2>Comments</h2><div class=comments>"
        for c in data['comments']:
            html = html + writeTopLevelComment(c, data)

            html = html + """</div></body>
                    </html>"""    
        file.write(html)
    return file_path



html = writeHead()

for dirpath, dnames, fnames in os.walk(workingDir):
    for f in fnames:
        if f.endswith(".json"):
            data = jsonToHTML(os.path.join(dirpath, f))
            html = html + '<a href={local_path}>{post}</a>'.format(post=writePost(data), local_path=data['htmlPath'])

file_path = 'saved.html'
with open(file_path, 'w') as file:
    html = html + """</body>
            </html>"""    
    file.write(html)