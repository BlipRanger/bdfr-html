#!/usr/bin/env python3

__author__ = "BlipRanger"
__version__ = "0.1.2"
__license__ = "MIT"

import os
import subprocess
import time

freq = os.environ['BDFR_FREQ']
inFolder = os.environ['BDFR_IN']
outFolder = os.environ['BDFR_OUT']
recover_comments = os.environ['BDFR_RECOVER_COMMENTS']
archive_context = os.environ['BDFR_ARCHIVE_CONTEXT']
limit = os.environ['BDFR_LIMIT']

idList = os.path.join(outFolder, "idList.txt")

#Start Webserver
#subprocess.Popen(["twistd", "-n", "web", "--path", outFolder, "--port", "tcp:7634"])

while True:
    subprocess.call(["python3.9", "-m", "bdfr", "archive", "--user", "me", "--saved", "-L", limit, "--config", "/config/config.cfg", "--authenticate", inFolder])
    subprocess.call(["python3.9", "-m", "bdfr", "download", "--user", "me", "--saved", "-L", limit, "--config", "/config/config.cfg", "--exclude-id-file", idList, "--authenticate", "--file-scheme", "{{POSTID}}", inFolder])
    subprocess.call(["python3.9", "bdfrToHTML.py", "--input", inFolder, "--output", outFolder, "--recover_comments", recover_comments, "--archive_context", archive_context])
    time.sleep(int(freq)*60)