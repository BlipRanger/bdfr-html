from setuptools import setup

setup(
    name='bdfrtohtml',
    packages=['bdfrtohtml'],
    version='1.4.1',
    description='Convert the output of BDFR to HTML',
    author='BlipRanger',
    author_email='blipranger@shrubbery.co',
    url='https://github.com/BlipRanger/bdfr-html',
    download_url='https://github.com/BlipRanger/bdfr-html/releases/tag/v1.3.0',
    keywords=['bdfr', 'reddit', 'downloader'],
    classifiers=[],
    package_data={
        "": ["templates/*.html", "templates/*.css"],
    },
    install_requires=[
    'click==7.1.2',
    'Markdown==3.3.4',
    'appdirs>=1.4.4',
    'bs4>=0.0.1',
    'dict2xml>=1.7.0',
    'ffmpeg-python>=0.2.0',
    'praw>=7.2.0',
    'pyyaml>=5.4.1',
    'requests>=2.25.1',
    'youtube-dl>=2021.3.14',
    'bdfr==2.2',
    'jinja2==3.0.0',
    'pillow>=8.0.0'
    ]
)
