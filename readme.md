# Tweet instagram stories

Python script to tweet your latest instagram stories

example: https://twitter.com/plhery_stories

### Get started

- Create a Twitter app with write access on https://app.twitter.com
- Install python3 & ffmpeg
- Install instagram_private_api and spyder-exe's tweepy fork
`pip3 install instagram_private_api git+https://github.com/Spyder-exe/tweepy.git`
- Run `python3 generate-instagram-cookie-jar -u your-username -p your-password`
This will auth you to instagram and store your cookies, which will work for 90 days
- Run `python3 generate-twitter-consumer-key -k your-app-key -p your-app-secret`
This will show you a link to log into twitter and generate api credentials
- Replace your instagram username/id in tweet-insta-stories.py
- Run `python3 tweet-insta-stories` to tweet your latest stories
- Set a crontab to run this every 10 minutes

Note: to delete your tweets after 5 days, uncomment the last line (warning: this will delete ALL you 5days+ tweets, not only your stories)
### TODO

- Run this in a serverless (e.g lambda) environment (ffmpeg may be a problem)
- Use a real DB
- Improve video upload behaviour

##Licence

TweetInstaStories was released under [Apache License 2.0](LICENSE)
