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

bot = Bot(config.token)

@sched.scheduled_job('cron', day_of_week='mon-sun', hour=19, timezone='America/Bahia')
def scheduled_job():
	for user in users.find({'notification': True}):
		subreddits = user['subreddits']
		if(len(subreddits) > 0 and user['nb_posts'] > 0):
			for subreddit in subreddits:
				bot.send_message(user['id'], text='Today on ' + subreddit)
				for submission in reddit.subreddit(subreddit).hot(limit=user['nb_posts']):
					msg = submission.title + '\n'
					msg += submission.url + '\n'
					msg += submission.shortlink
					bot.send_message(user['id'], text=msg)
			msg = 'You are receiving this messages because you turned notification on. '
			msg += 'If you no longer want to receive this, just send /set_notification.'
			bot.send_message(user['id'], msg)

sched.start()