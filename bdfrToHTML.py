import json
import os
import markdown
from datetime import datetime
import click
import shutil


inputFolder = ''
outputFolder = ''

def jsonToHTML(file_path):
    f = open(file_path,)
    data = json.load(f)
    f.close()
    data['htmlPath'] = writeToHTML(data)
    return data


def findMatchingMedia(name, folder):
    paths = []
    for dirpath, dnames, fnames in os.walk(folder):
        for f in fnames:
            if (name) in f and not f.endswith('.json'):
                paths.append(copyMedia(os.path.join(dirpath, f), f))
    return paths


def buildGallery(paths):
    html = '<div class=photoGrid><div class=row>'
    for p in paths:
        html = html + """<div class=column><a href={path}><img src={path} style="width:100%"></a></div>""".format(path=p)
    html = html + """</div></div>"""
    return html

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
                print(l)
                if l == '---\n':
                    return (txt + '</div>')
                else:
                    txt = txt + l
            return markdown.markdown(txt)
    elif(len(paths) > 1):
        return buildGallery(paths)
    return ""

def copyMedia(mediaPath, filename):
    writeFolder = outputFolder + 'media/' 
    assure_path_exists(writeFolder)
    shutil.copyfile(mediaPath, writeFolder + filename)
    return 'media/' + filename

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
        <a href="{local_link}">link</a> <a href="{link}">reddit link</a> <a href="https://www.reddit.com{url}"> Content Link</a> </div>
        </div>
        <time>{time}</time><span class="subreddit">{subreddit}</span><span class="user">{user}</span>
        <div class=content>{content}</p></div>
        </div>

        """.format(time=writeDatestring(data.get('time', '1616957979')), local_link=local_link, submission=data.get('id', ''),
         content=content, url=data.get('permalink', ''), link=data.get('url',''), title=data.get('title',''), user=data.get('author', ''),
         subreddit=getSubreddit(data.get('permalink', '')))

def getSubreddit(permalink):
    strings = permalink.split("/")
    return strings[1] + '/' + strings[2]

def writeToHTML(data):
    file_path = data['id'] + '.html'
    with open(outputFolder + file_path, 'w') as file:
        html = writeHead()
        html = html + writePost(data) + "<h2>Comments</h2><div class=comments>"
        for c in data['comments']:
            html = html + writeTopLevelComment(c, data)

            html = html + """</div></body>
                    </html>"""    
        file.write(html)
    return file_path

def assure_path_exists(path):
        dir = os.path.dirname(path)
        if not os.path.exists(dir):
                os.makedirs(dir)

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
                data = jsonToHTML(os.path.join(dirpath, f))
                html = html + '<a href={local_path}>{post}</a>'.format(post=writePost(data), local_path=data['htmlPath'])

    file_path = output + '/index.html'

    with open(file_path, 'w') as file:
        html = html + """</body>
                </html>"""    
        file.write(html)
    shutil.copyfile('style.css', outputFolder + 'style.css')

if __name__ == '__main__':
    converter()
