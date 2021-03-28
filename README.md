# bdfr-html
Converts the output of the [bulk downloader](https://github.com/aliparlakci/bulk-downloader-for-reddit/tree/v2) (V2) for reddit to a set of HTML pages. 

Requires that you run both the archive and the download portions of the bulk downloader script and that the names of the download files contain the id of the posts.
Currently only supports the json version of the archive output. 

**Usage**

`python3 bdfrToHTML.py --input ./location/of/archive/and/downloads --output /../html`
