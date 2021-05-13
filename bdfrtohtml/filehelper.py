import shutil
import markdown
import subprocess
import jinja2
import json
import os
import logging
logger = logging.getLogger(__name__)

templateLoader = jinja2.FileSystemLoader(searchpath="./templates")
templateEnv = jinja2.Environment(loader=templateLoader)
templateEnv.add_extension('jinja2.ext.debug')
templateEnv.filters["markdown"] = markdown.markdown

#Import all json files into single list. 
def importPosts(folder):
    postList = []
    for dirpath, dnames, fnames in os.walk(folder):
        for f in fnames:
            if f.endswith(".json"):
                data = loadJson(os.path.join(dirpath, f))
                postList.append(data)
    return postList

#Write index page
def writeIndexFile(postList, outputFolder):
    template = templateEnv.get_template("index.html")
     
    with open(os.path.join(outputFolder, "index.html"), 'w', encoding="utf-8") as file:
        file.write(template.render(posts=postList))

#Check for path, create if does not exist
def assurePathExists(path):
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)

#Loads in the json file data and adds the path of it to the dict
def loadJson(file_path):
    f = open(file_path,)
    data = json.load(f)
    f.close()
    logging.debug('Loaded ' + file_path)
    return data

#Copy media from the input folder to the file structure of the html pages
def copyMedia(sourcePath, outputPath):

    if outputPath.endswith('mp4'):
        try:
            #This fixes mp4 files that won't play in browsers
            command = 'ffmpeg -i "{input}" -c:v copy -c:a copy -y "{output}"'.format(input=sourcePath, output=outputPath)
            print(command)
            print(subprocess.check_output(command))
            os.system("ffmpeg -nostats -loglevel 0 -i '{input}' -c:v copy -c:a copy -y '{output}'".format(input=sourcePath, output=outputPath))
        except:
            logging.error('FFMPEG failed')
    else:
        shutil.copyfile(sourcePath, outputPath)
    logging.debug('Moved ' + sourcePath + ' to ' + outputPath)


#Search the input folder for media files containing the id value from an archive
#Inputs: id name, folder to search
def findMatchingMedia(post, inputFolder, outputFolder):
    paths = []
    mediaFolder = os.path.join(outputFolder, 'media/')
    
    #Don't copy if we already have it
    existingMedia = os.path.join(outputFolder, "media/")
    for dirpath, dnames, fnames in os.walk(existingMedia):
        for f in fnames:
            if post['id'] in f and not f.endswith('.json') and not f.endswith('.html'):
                logging.info("Find Matching Media found: " + dirpath + f)
                paths.append(os.path.join('media/', f))
    if len(paths) > 0:
        logging.info("Existing media found for " + post['id'])
        post['paths'] = paths
        return
    for dirpath, dnames, fnames in os.walk(inputFolder):
        for f in fnames:
            if post['id'] in f and not f.endswith('.json'):
                logging.debug("Find Matching Media found: " + dirpath + f)
                copyMedia(os.path.join(dirpath, f), os.path.join(mediaFolder, f))
                paths.append(os.path.join('media/', f))
    post['paths'] = paths
    return 

def writePostToFile(post, outputFolder):

    template = templateEnv.get_template("page.html")
    post['filename'] =  post['id']+".html"
    post['filepath'] =  os.path.join(outputFolder, post['id']+".html")
    
    with open(post['filepath'], 'w', encoding="utf-8") as file:
        file.write(template.render(post=post))