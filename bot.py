import config
import praw
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import os
import pymongo

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

reddit = praw.Reddit(client_id=config.id,
                     client_secret=config.secret,
                     user_agent=config.user_agent)
client = pymongo.MongoClient(config.uri)
db = client.todayonredditbot

users = db['users']
users.create_index('id', unique=True)

def start(bot, update):
	try:
		data = {'id': update.message.chat.id, 'subreddits': [], 'nb_posts': 0}
		users.insert_one(data)
		update.message.reply_text('Starting bot...')
	except:
		update.message.reply_text('Starting bot...')

def help(bot, update):
	msg = '/get_top_posts <subreddit> <number of posts> (e.g. /get_top_posts AskReddit 3): return today\'s top subreddit posts\n\n'
	msg +='/get_popular_posts <subreddit> <number of posts> (e.g. /get_popular_posts AskReddit 3): return popular posts from chosen subreddit\n\n'
	msg +='Default subreddit: /r/all\nDefault number of posts: 5'
	update.message.reply_text(msg)

def get_top_posts(bot, update, args):
	subreddit = 'all'
	limit = 5
	
	if(len(args) != 0):
		subreddit = args[0]
	if(len(args) == 2):
		try:
			limit = int(args[1])
		except:
			update.message.reply_text(error_msg('/get_top_posts <subreddit> <number of posts>'))
	
	try:
		for submission in reddit.subreddit(subreddit).top('day', limit=limit):
			update.message.reply_text(post_msg(submission))
	except:
		update.message.reply_text(error_msg('/get_top_posts <subreddit> <number of posts>'))

def get_popular_posts(bot, update, args):
	subreddit = 'all'
	limit = 5

	if(len(args) != 0):
		subreddit = args[0]
	if(len(args) == 2):
		try:
			limit = int(args[1])
		except:
			update.message.reply_text(error_msg('/get_popular_posts <subreddit> <number of posts>'))

	try:
		for submission in reddit.subreddit(subreddit).hot(limit=limit):
			update.message.reply_text(post_msg(submission))
	except:
		update.message.reply_text(error_msg('/get_popular_posts <subreddit> <number of posts>'))

def set_nb_posts(bot, update, args):
	if(len(args) == 1):
		try:
			nb_posts = int(args[0])
			chat_id = {'id': update.message.chat.id}
			users.update(chat_id, {'$set': {'nb_posts': nb_posts}})
			update.message.reply_text('Number of posts set to' + args[0])	
		except:
			update.message.reply_text(error_msg('/set_nb_posts <number of posts>'))	
	else:
		update.message.reply_text(error_msg('/set_nb_posts <number of posts>'))

def post_msg(submission):
	msg = submission.title + '\n'
	msg += submission.url + '\n'
	msg += submission.shortlink
	return msg

def error_msg(usage):
	error = 'Ops, something went wrong :(\n'
	error += 'Usage: ' + usage
	return error

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def main():
	TOKEN = config.token
	PORT = int(os.environ.get('PORT', '5000'))

	updater = Updater(TOKEN)
	dp = updater.dispatcher

	dp.add_handler(CommandHandler("start", start))
	dp.add_handler(CommandHandler("help", help))
	dp.add_handler(CommandHandler("get_top_posts", get_top_posts, pass_args=True))
	dp.add_handler(CommandHandler("get_popular_posts", get_popular_posts, pass_args=True))
	dp.add_handler(CommandHandler("set_nb_posts", set_nb_posts, pass_args=True))
	dp.add_error_handler(error)

	updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
	updater.bot.set_webhook("https://todayonredditbot.herokuapp.com/" + TOKEN)
	updater.idle()

if __name__ == '__main__':
    main()
