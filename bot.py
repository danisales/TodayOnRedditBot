import praw
import telegram
import logging

config = {}
execfile("config.py", config)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

reddit = praw.Reddit(client_id=config['CLIENT_ID'],
                     client_secret=config['CLIENT_SECRET'],
                     user_agent=config['USER_AGENT'])

bot = telegram.Bot(config['TOKEN'])