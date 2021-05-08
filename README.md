# bdfr-html
Converts the output of the [bulk downloader for reddit (V2)](https://github.com/aliparlakci/bulk-downloader-for-reddit)  to a set of HTML pages. 

Currently requires that you run both the archive and the download portions of the BDfR bulk downloader script and that the names of the downloaded files contain the post id (this is default).
Currently only supports the json version of the archive output from BDfR V2. 

**Usage**

`python3 bdfrToHTML.py --input ./location/of/archive/and/downloads --output /../html/`

**Additional Features**

- Use the --archive_context option to pull the related contextual post for downloaded comments (requires BDfR in the same folder).
- Use the --recover_comments option to have the script attempt to pull deleted comments from Pushshift. 

**Planned Features**

- Using Pushshift to pull deleted post contents 
- Adding an optional archiver to archive webpages linked in posts
- Docker support with built in webserver and BDfR
- Possible static-site generation
