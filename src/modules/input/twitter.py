import os
import twitter

from classes import BaseInputModule

from models import Message

class Twitter(BaseInputModule):

    def __init__(self, credentials=None):

        if credentials is None:
            key = os.getenv('TWITTER_KEY')
            secret = os.getenv('TWITTER_SECRET')
            token_key = os.getenv('TWITTER_TOKEN_KEY')
            token_secret = os.getenv('TWITTER_TOKEN_SECRET')

        self._service = twitter.Api(
            consumer_key=key,
            consumer_secret=secret,
            access_token_key=token_key,
            access_token_secret=token_secret
        )
        self._name = self.__class__.__name__.lower()

    def fetch(self, cfg, checkpoint):
        results = self._service.GetListTimeline(
            list_id=cfg['list_id'],
            since_id=checkpoint
        )
        if results == []:
            # No new Tweets
            return None, None

        tweetlist = []
        for tweet in results:
            tweetdict = tweet.AsDict()
            tweet = Message(
                source_module=self._name,
                id=tweetdict['id'],
                body=tweetdict['text'],
                source_identity=tweetdict['user']['screen_name'],
                provenance=[self._name],
            )
            tweetlist.append(tweet)

        return tweetlist, tweetlist[0].AsDict()['id']

    @classmethod
    def validate_cfg(cls, cfg):
        valid, msg = BaseInputModule.validate_cfg(cfg)

        if not valid:
            return valid, msg

        if cfg.get('list_id') is None:
            return False, "Unsupported action, only 'list_id' is supported."

        return True, 'Configuration validated successfully.'
