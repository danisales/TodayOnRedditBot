from apscheduler.schedulers.blocking import BlockingScheduler
from telegram.ext import Updater
from telegram.bot import Bot
import pymongo
import praw
import config

sched = BlockingScheduler()
reddit = praw.Reddit(client_id=config.id,
                     client_secret=config.secret,
                     user_agent=config.user_agent)

client = pymongo.MongoClient(config.uri)
db = client.todayonredditbot
users = db['users']
users.create_index('id', unique=True)

bot = Bot(config.token)

@sched.scheduled_job('cron', day_of_week='mon-sun', hour=17)
def scheduled_job():
	for user in users.find({'notification': True}):
		for subreddit in user['subreddits']:
			for submission in reddit.subreddit(subreddit).hot(limit=user['nb_posts']):
				msg = submission.title + '\n'
				msg += submission.url + '\n'
				msg += submission.shortlink
				bot.send_message(user['id'], text=msg)

sched.start()