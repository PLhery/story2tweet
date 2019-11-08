import codecs
import argparse
from pathlib import Path

from instagram_private_api import Client

parser = argparse.ArgumentParser()
parser.add_argument('-u', '--username', dest='username', type=str, required=True)
parser.add_argument('-p', '--password', dest='password', type=str, required=True)
args = parser.parse_args()

def onlogin_callback(api):
    with open(Path(__file__).resolve().parent.joinpath('settings/instagram_cookie_jar.txt'), 'w') as outfile:
        outfile.write(codecs.encode(api.settings['cookie'], 'base64').decode())
        print('File instagram_cookie_jar.json saved')

insta_api = Client(args.username, args.password, on_login=onlogin_callback)