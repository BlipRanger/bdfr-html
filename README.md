# bdfr-html
BDFR-HTML is a companion script that the output of the incredibly useful [bulk downloader for reddit](https://github.com/aliparlakci/bulk-downloader-for-reddit) into a set of HTML pages with an index which can be easily viewed in a browser. It also provides a number of other handy tools such as the ability to grab the context for saved comments or deleted posts from Pushshift. The HTML pages are rendered using jinja2 templates and can be easily modified to suit your needs. The script currently requires that you run both the archive and the download portions of the BDfR bulk downloader script and that the names of the downloaded files contain the post id (this is default).

**Table**

## Installation

Simply clone this repo and run the script as you see fit. I am currently in the process of packaging it to be avalaible on PyPi in the future. 

`python -m bdfrtohtml --input ./location/of/archive/and/downloads --output /../html/`

Use `python -m bdfrtohtml --help` for a list of options

**Docker-Compose**

For ease of use for both bdfr and bdfr-html in an automated fashion, I have included a docker-compose file which will spin up both an automation container and a web server container. The automation container will run bdfr and then subsequently bdfr-html, producing a volume or mounted folder containing the generated html files. The web server container shares the output volume and hosts the generated files. Currently this is tasked to only save "Saved" user content, however this might be changed in the future. If you would prefer to populate bdfr-html with your own reddit json/media files from bdfr, you can use a similar docker-compose file, but mount the folder where you have saved your content to the `BDFR_IN` folder (/input by default) and set the env variable `RUN_BDFR` to false (default). 

Since BDFR 2.1.1 you should be able to properly hit the Oauth within the docker container. The proper port for validation has is exposed in the docker-compose file. 
If you are running the docker container on a different machine, replace `locahost` in the returned url with the address of the docker host. 

To run the compose file, simply clone this repo and run `docker-compose up`. 

**Additional Features**

- Use the --archive_context option to pull the related contextual post for downloaded comments.
- Use the --recover_comments and --recover_posts options to have the script attempt to pull deleted comments and posts from Pushshift. 
- The script now actively avoids reprocessing inputs by storing a list of processed ids in the output folder.
- Produces an ID file of processed posts which can be fed to bdfr to avoid re-downloading content. 
- Templated HTML using jinja2 which can be easily modified to suit your needs.
- Use --write_links_to_file option to write a list of urls for webpages and/or media referenced by posts to a file to use in other processes
- Posts are sorted in chronological order

**Planned Features**

- Improved HTML templates
- Config file instead of just arguments
- Better docs
- Additional possible docker-compose configs
