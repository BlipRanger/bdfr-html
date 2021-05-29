# bdfr-html
BDFR-HTML is a companion script that turns the output of the incredibly useful [bulk downloader for reddit](https://github.com/aliparlakci/bulk-downloader-for-reddit) into a set of HTML pages with an index which can be easily viewed in a browser. It also provides a number of other handy tools such as the ability to grab the context for saved comments or pull down deleted posts from Pushshift. The HTML pages are rendered using jinja2 templates and can be easily modified to suit your needs. The script currently requires that you run both the archive and the download portions of the BDfR bulk downloader script and that the names of the downloaded files contain the post id (this is default). This can be automated using the included start.py or docker container.

## Table of Contents
- [bdfr-html](#bdfr-html)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Docker](#docker)
  - [Contributing](#contributing)
  - [Planned Features](#planned-features)
  - [Screenshots](#screenshots)

## Installation

You can simply clone this repo and run the script in this folder or you can try your hand at installing the package using setuptools using the following command:
` python setup.py install`
(This is still a work in progress)

## Usage

To run the script with defaults:
`python -m bdfrtohtml` (the default is to look in the folder 'input' and write to the folder 'output')

`python -m bdfrtohtml --input_folder ./location/of/archivedFiles --output_folder /../html/`

**Options**
```
  --input_folder TEXT                           The folder where the download and archive results have been saved to.
  --output_folder TEXT                          Folder where the HTML results should be created.
  --recover_comments BOOLEAN                    Should we attempt to recover deleted comments?
  --recover_posts BOOLEAN                       Should we attempt to recover deleted posts?
  --generate_thumbnails BOOLEAN                 Generate thumbnails for video posts? (deprecated by index_mode)
  --archive_context BOOLEAN                     Should we attempt to archive the contextual post for saved comments?
  --delete_media BOOLEAN                        Should we delete the input media after creating the output?
  --index_mode [default|lightweight|oldreddit]  What type of templated index page should be generated?
  --write_links_to_file [None|Webpages|All]     Should we write the links from posts to a text file for external consuption?
  --config FILENAME                             Read in a config file
  --help                                        Show this message and exit.
```

**start.py**
The start.py is what (currently) powers the docker container's automation and steps through running both bdfr and bdfr-html in sequence at timed intervals. 
Instead of running bdfrtohtml alone, you can run `python start.py` in a cloned copy of this repo to start up the automated process.
The configuration for both bdfrtohtml and the start.py script itself can be found in the [config folder](https://github.com/BlipRanger/bdfr-html/tree/main/bdfrtohtml/config).
This script also includes multi-user support which can be found in the config file.

## Docker

For ease of use of both bdfr and bdfr-html in an automated fashion, there is included a docker-compose file which will spin up both an automation container and a web server container. The automation container will run bdfr and then subsequently bdfr-html, producing a volume or mounted folder containing the generated html files. The web server container shares the output volume and hosts the generated files. Currently this is tasked to only save "Saved" user content, however this might be changed in the future. If you would prefer to populate bdfr-html with your own reddit json/media files from bdfr, you can use a similar docker-compose file, but mount the folder where you have saved your content to the folder (bdfrtohtml/input by default) and set the config variable `RUN_BDFR` to false. 

Since BDFR 2.1.1 you should be able to properly hit the Oauth within the docker container. The proper port for validation has is exposed in the docker-compose file. 
If you are running the docker container on a different machine, replace `locahost` in the returned Oauth url with the address of the docker host. 

To run the compose file, simply clone this repo and run `docker-compose up`. 

The config file of the docker container can be mounted and modified just like the one mentioned above for the start.py script.  

## Contributing
I am open to any and all help or criticism on this project! Please feel free to create issues as you encounter them and I'll work to get them fixed. I have a set idea of the scope of this project, but I am always open to new feature suggestions or improvements to my code. Also, if you have code you'd like to contribute, just open a PR and I'll take a look!


## Planned Features

- Better documentation, including a lessons learned page
- The ability to output more data/metrics
- Docker support for automatically archiving subreddits/users
- PyPi + Dockerhub package support

## Screenshots

**Example Post**

![Post](/docs/screenshots/bdfr-html-post.jpg?raw=true "Example Post")

**Default Index Page**

![Default Index Page](/docs/screenshots/bdfr-html-default-index.jpg?raw=true "Default Index Page")

**Lightweight Index Page**

![Lightweight Index Page](/docs/screenshots/bdfr-html-lightweight-index.jpg?raw=true "Lightweight Index Page")

**Old Reddit-Like Index Page**

![Old Reddit-like Index Page](/docs/screenshots/bdfr-html-oldreddit-index.jpg?raw=true "Old Reddit Index Page")
