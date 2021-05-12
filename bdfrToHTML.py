#!/usr/bin/env python3

__author__ = "BlipRanger"
__version__ = "0.1.3"
__license__ = "GNU GPLv3"

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
import jinja2

#Logging Setup
level = os.getenv('BDFRH_LOGLEVEL', "INFO")
if level == "DEBUG":
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)


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

    #Don't copy if we already have it
    existingMedia = os.path.join(outputFolder, "media/")
    for dirpath, dnames, fnames in os.walk(existingMedia):
        for f in fnames:
            if (name) in f and not f.endswith('.json'):
                logging.debug("Find Matching Media found: " + dirpath + f)
                paths.append(os.path.join('media/', f))
    if len(paths) > 0:
        logging.info("Existing media found for " + name)
        return paths 

    for dirpath, dnames, fnames in os.walk(folder):
        for f in fnames:
            if (name) in f and not f.endswith('.json'):
                logging.debug("Find Matching Media found: " + dirpath + f)
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
    logging.debug("Parsing selfpost for " + filePath)
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
    logging.debug("Formatting media for " + str(paths))
    if paths is None:
        return ""
    if len(paths) == 1:
        path = paths[0]

        if path.endswith('jpg') or path.endswith('jpeg') or path.endswith('png') or path.endswith('gif'):
            return '<a href={path}><img src={path}></a>'.format(path=path)
        elif path.endswith('m4a') or path.endswith('mp4') or path.endswith('mkv'):
            return '<video max-height="500" controls preload="metadata"><source src="{path}"></video>'.format(path=path)
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
        shutil.copyfile(mediaPath, os.path.join(writeFolder, filename))
    logging.debug('Moved ' + mediaPath + ' to ' + writeFolder +filename)
    return 'media/' + filename

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

#Extract the subreddit name from the permalink
def getSubreddit(permalink):
    strings = permalink.split("/")
    return strings[1] + '/' + strings[2]

#Check for path, create if does not exist
def assure_path_exists(path):
        dir = os.path.dirname(path)
        if not os.path.exists(dir):
                os.makedirs(dir)

#Main function, loops through json files in input folder, extracts archive data into dict, 
#formats/writes archive data and media to html files, creates a single index.html file with 
#links to all archived posts. 
def main():
        
    assure_path_exists(outputFolder)
    if not os.path.isdir(inputFolder):
        raise ValueError('Input folder does not exist') 


    templateLoader = jinja2.FileSystemLoader(searchpath="./templates")
    templateEnv = jinja2.Environment(loader=templateLoader)
    templateEnv.filters["markdown"] = markdown.markdown
    TEMPLATE_FILE = "post.html"
    template = templateEnv.get_template(TEMPLATE_FILE)
    
    postList = []
    for dirpath, dnames, fnames in os.walk(inputFolder):
        for f in fnames:
            if f.endswith(".json"):
                data = loadJson(os.path.join(dirpath, f))
                html = template.render(data)
                filename = os.path.join(outputFolder, data['id']+".html")
                with open(filename, 'w') as file:
                    file.write(html)
                postList.append(data)

    TEMPLATE_FILE = "index.html"
    template = templateEnv.get_template(TEMPLATE_FILE)
    
    

    shutil.copyfile('style.css', os.path.join(outputFolder, 'style.css'))
    logging.info("Run Complete!")


@click.command()
@click.option('--input', default='.', help='The folder where the download and archive results have been saved to')
@click.option('--output', default='./html/', help='Folder where the HTML results should be created.')
@click.option('--recover_comments', default=False, type=bool, help='Should we attempt to recover deleted comments?')
@click.option('--archive_context', default=False, type=bool, help='Should we attempt to archive the contextual post for saved comments?')
@click.option('--delete_input', default=False, type=bool, help='Should we delete the input after creating the output?')
def converter(input, output, recover_comments, archive_context, delete_input):
    global inputFolder
    global outputFolder
    global recoverComments
    global context

    #Set globals (there is probably a better way to do this)
    inputFolder = os.path.join(input, '')
    outputFolder = os.path.join(output, '')
    recoverComments = (recover_comments)
    context = (archive_context)
    delete_input = delete_input

    main()
    
    if delete_input:
        for root, dirs, files in os.walk(inputFolder):
            for file in files:
                os.remove(os.path.join(root, file))


if __name__ == '__main__':
    converter()
