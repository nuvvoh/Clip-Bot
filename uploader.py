import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from instagrapi import Client
import tweepy
import config

class MultiPlatformUploader:
    def __init__(self):
        self.youtube = None
        self.instagram = None
        self.twitter = None
    
    def setup_youtube(self):
        """Setup YouTube API client"""
        SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
        
        flow = InstalledAppFlow.from_client_config(
            {
                "installed": {
                    "client_id": config.YOUTUBE_CLIENT_ID,
                    "client_secret": config.YOUTUBE_CLIENT_SECRET,
                    "redirect_uris": ["http://localhost"],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token"
                }
            },
            SCOPES
        )
        
        credentials = flow.run_local_server(port=0)
        self.youtube = build('youtube', 'v3', credentials=credentials)
    
    def setup_instagram(self):
        """Setup Instagram client"""
        self.instagram = Client()
        self.instagram.login(config.INSTAGRAM_USERNAME, config.INSTAGRAM_PASSWORD)
    
    def setup_twitter(self):
        """Setup Twitter API client"""
        auth = tweepy.OAuth1UserHandler(
            config.TWITTER_API_KEY,
            config.TWITTER_API_SECRET,
            config.TWITTER_ACCESS_TOKEN,
            config.TWITTER_ACCESS_SECRET
        )
        self.twitter = tweepy.API(auth)
        self.twitter_v2 = tweepy.Client(
            bearer_token=config.TWITTER_BEARER_TOKEN,
            consumer_key=config.TWITTER_API_KEY,
            consumer_secret=config.TWITTER_API_SECRET,
            access_token=config.TWITTER_ACCESS_TOKEN,
            access_token_secret=config.TWITTER_ACCESS_SECRET
        )
    
    def upload_to_youtube(self, video_path, title, description, tags=None):
        """Upload video to YouTube Shorts"""
        if not self.youtube:
            self.setup_youtube()
        
        body = {
            'snippet': {
                'title': title[:100],
                'description': f"{description}\n\n#Shorts #GTAVI #GTA6",
                'tags': tags or ['GTA VI', 'GTA 6', 'Gaming', 'Shorts'],
                'categoryId': '20'
            },
            'status': {
                'privacyStatus': 'public',
                'selfDeclaredMadeForKids': False
            }
        }
        
        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
        request = self.youtube.videos().insert(
            part='snippet,status',
            body=body,
            media_body=media
        )
        
        response = request.execute()
        return f"https://youtube.com/shorts/{response['id']}"
    
    def upload_to_instagram(self, video_path, caption):
        """Upload video to Instagram Reels"""
        if not self.instagram:
            self.setup_instagram()
        
        caption_with_tags = f"{caption}\n\n#GTAVI #GTA6 #Gaming #Reels"
        media = self.instagram.clip_upload(video_path, caption_with_tags)
        return f"https://instagram.com/p/{media.code}"
    
    def upload_to_twitter(self, video_path, text):
        """Upload video to Twitter/X"""
        if not self.twitter:
            self.setup_twitter()
        
        media = self.twitter.media_upload(video_path)
        tweet_text = f"{text}\n\n#GTAVI #GTA6 #Gaming"
        
        tweet = self.twitter_v2.create_tweet(
            text=tweet_text,
            media_ids=[media.media_id]
        )
        return f"https://twitter.com/i/status/{tweet.data['id']}"
    
    def upload_all(self, video_path, title, description):
        """Upload to all platforms"""
        results = {}
        
        print("Uploading to YouTube...")
        try:
            results['youtube'] = self.upload_to_youtube(video_path, title, description)
            print(f"✓ YouTube: {results['youtube']}")
        except Exception as e:
            print(f"✗ YouTube failed: {e}")
            results['youtube'] = None
        
        print("Uploading to Instagram...")
        try:
            results['instagram'] = self.upload_to_instagram(video_path, description)
            print(f"✓ Instagram: {results['instagram']}")
        except Exception as e:
            print(f"✗ Instagram failed: {e}")
            results['instagram'] = None
        
        print("Uploading to Twitter...")
        try:
            results['twitter'] = self.upload_to_twitter(video_path, title)
            print(f"✓ Twitter: {results['twitter']}")
        except Exception as e:
            print(f"✗ Twitter failed: {e}")
            results['twitter'] = None
        
        return results
