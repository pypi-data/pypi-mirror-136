import argparse

from .apps.config import ConfigApp
from .apps.get import DownloadApp

ACTIVATED_APPS = {
    'config': ConfigApp,
    'get': DownloadApp,
}

def main():
    arg_parser = get_app_arg_parser()
    parsed_namespace = arg_parser.parse_args()
    arguments = vars(parsed_namespace)
    application = ACTIVATED_APPS[arguments['sub-app']]()
    application.start_execution(arg_parser, **arguments)

def get_app_arg_parser():
    app_parser = argparse.ArgumentParser(description=(
        'download songs with yt-dlp and auto-tag them with beets. use the get '
        'sub-app to *get* music, and use the config sub-app to *config*ure '
        'yt-dlp\'s and beets\' behaviour'
    ))
    subparser = app_parser.add_subparsers(title='Sub-application Choice')
    subparser.required = True
    subparser.dest = 'sub-app'
    for _, class_ in ACTIVATED_APPS.items():
        class_.add_sub_parser_arguments(subparser)
    return app_parser

if __name__ == '__main__':
    main()
