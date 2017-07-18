import praw
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging

config = {}
execfile("config.py", config)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

reddit = praw.Reddit(client_id=config['CLIENT_ID'],
                     client_secret=config['CLIENT_SECRET'],
                     user_agent=config['USER_AGENT'])

def start(bot, update):
	update.message.reply_text('Starting bot...')

def help(bot, update):
	msg = '/get_top_posts: return today\'s top 5 /r/all posts\n'
	msg +='/get_popular_posts: return popular posts from /r/all'
	update.message.reply_text(msg)

def get_top_posts(bot, update):
	for submission in reddit.subreddit('all').top('day', limit=5):
		msg = ''
		msg += submission.title + '\n'
		msg += submission.url + '\n'
		msg += submission.shortlink + '\n\n'
		update.message.reply_text(msg)

def get_popular_posts(bot, update):
	for submission in reddit.subreddit('all').hot(limit=5):
		msg = ''
		msg += submission.title + '\n'
		msg += submission.url + '\n'
		msg += submission.shortlink + '\n\n'
		update.message.reply_text(msg)

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def main():
	updater = Updater(config['TOKEN'])
	dp = updater.dispatcher

	dp.add_handler(CommandHandler("start", start))
	dp.add_handler(CommandHandler("help", help))
	dp.add_handler(CommandHandler("get_top_posts", get_top_posts))
	dp.add_handler(CommandHandler("get_popular_posts", get_popular_posts))

	updater.start_polling()
	updater.idle()

if __name__ == '__main__':
    main()
