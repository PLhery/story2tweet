import codecs
import time
import os
import urllib.request
import tweepy
import subprocess

from collections import namedtuple
from pprint import pprint
from urllib.parse import urlparse
from xml.dom.minidom import parseString
from instagram_private_api import Client
from pathlib import Path

INSTA_USERNAME = 'plhery'
INSTA_ID = '4801677468'

def absPath(path):
    return str(Path(__file__).resolve().parent.joinpath(path))

def fetch_user_stories():
    with open(absPath('settings/instagram_cookie_jar.txt')) as file_data:
        cookie = codecs.decode(file_data.read().encode(), 'base64')

    insta_api = Client(INSTA_USERNAME, '', cookie=cookie)
    return insta_api.user_story_feed(INSTA_ID)

def parse_stories_feed(user_feed_info):
    Story = namedtuple('Story', ['type', 'taken_at', 'media_url', 'audio_url'])

    media_urls = []
    for media in user_feed_info['reel']['items']:
        taken_ts = int(media.get('taken_at', 0))

        if 'video_versions' in media:
            video_manifest = parseString(media['video_dash_manifest'])
            video_period = video_manifest.documentElement.getElementsByTagName('Period')
            representations = video_period[0].getElementsByTagName('Representation')
            video_url = representations[0].getElementsByTagName('BaseURL')[0].childNodes[0].nodeValue
            audio_element = representations.pop()
            if audio_element.getAttribute("mimeType") == "audio/mp4":
                audio_url = audio_element.getElementsByTagName('BaseURL')[0].childNodes[0].nodeValue
                media_urls.append(Story('video', taken_ts, video_url, audio_url))
            else:
                media_urls.append(Story('video', taken_ts, video_url, None))
        else:
            media_urls.append(Story('picture', taken_ts, media['image_versions2']['candidates'][0]['url'], None))
    return media_urls


def download_and_process_story(story):
    _, file_extension = os.path.splitext(urlparse(story.media_url).path)
    filename = absPath('tmp/media' + file_extension)

    urllib.request.urlretrieve(story.media_url, filename)

    # DOWNLOAD & MERGE THE AUDIO (requires ffmpeg)
    if story.audio_url is not None:
        _, audio_extension = os.path.splitext(urlparse(story.audio_url).path)
        audioname = absPath('tmp/audio' + audio_extension)
        urllib.request.urlretrieve(story.audio_url, audioname)

        newfilename = absPath('tmp/processed' + file_extension)
        cmd = ['ffmpeg', '-loglevel', 'fatal', '-y', '-i', filename, '-i', audioname, '-c:v', 'copy', '-c:a', 'copy', newfilename]
        exit_code = subprocess.call(cmd, stdout=None, stderr=subprocess.STDOUT)
        if exit_code != 0:
            print("[W] FFmpeg exit code not '0' but '{:d}'.".format(exit_code))
        return newfilename

    return filename

def getTwapi():
    with open(absPath('settings/twitter_tokens.txt')) as file_data:
        ckey, csecret, tkey, tsecret = file_data.read().split('\n')
    twauth = tweepy.OAuthHandler(ckey, csecret)
    twauth.set_access_token(tkey, tsecret)
    return tweepy.API(twauth)

def tweet_media(filepath):
    twapi = getTwapi()
    print('uploading {}.. '.format(filepath))
    try:
        upload_result = twapi.media_upload(filename=filepath)
        if hasattr(upload_result, 'processing_info') and upload_result.processing_info['state'] == 'pending':
            print('media state pending - will wait 10 seconds')
            time.sleep(10) # hacky but tweepy doesn't provide the media status endpoint
        print('sending the tweet...')
        twapi.update_status(media_ids=[upload_result.media_id_string])
    except tweepy.error.TweepError as err:
        print("Unexpected twitter error:", err)
    print('done!')


def read_last_tweeted_story_time():
    if not os.path.exists(absPath('settings/last_tweeted_story.txt')):
        return 0
    with open(absPath('settings/last_tweeted_story.txt')) as file:
        timestamp = int(file.read())
    return timestamp


def save_last_tweeted_story_time(story):
    with open(absPath('settings/last_tweeted_story.txt'), 'w') as file:
        file.write(str(story.taken_at))

def delete_old_tweets():
    print('Checking old tweets...')
    twapi = getTwapi()
    timeline = twapi.user_timeline(count=200)
    for tweet in timeline:
        if time.time() - tweet.created_at.timestamp() > 60 * 60 * 24 * 5:
            print('Deleting tweet {}'.format(tweet.id_str))
            twapi.destroy_status(tweet.id_str)
    return

if __name__ == '__main__':
    user_feed_info = fetch_user_stories()
    stories = parse_stories_feed(user_feed_info)
    print('{:d} new stories found'.format(len(stories)))
    pprint(stories)
    last_story_time = read_last_tweeted_story_time()
    for story in stories:
        if last_story_time >= story.taken_at:
            print('Tweet for story {} already sent, skipping'.format(story.taken_at))
            continue
        filename = download_and_process_story(story)
        tweet_media(filename)
        save_last_tweeted_story_time(story)
    # delete_old_tweets()