import csv
from DBController import DBController
from Extractor import Extractor
from Utils import Utils
from Contract import Contract

class TableParser:

	filepath = 'test.csv'
	csvfile = open(filepath, 'r', encoding='cp1252')
	csv_reader = csv.DictReader(csvfile, delimiter=';', quotechar='"')

	@staticmethod
	def getTweetFromEntry(entry):

		return {

			Contract.ADD_TO_TABLE_KEY: Contract.TABLE_TWEET,
			Contract.ID_COLUMN: Utils.getRandom8ByteInt(),
			Contract.AUTHOR_COLUMN: entry[Contract.HANDLE_ENTRY],
			Contract.TEXT_COLUMN: entry[Contract.TEXT_ENTRY],
			Contract.TIME_COLUMN: Extractor.extractTime(entry),
			Contract.RATING_COLUMN: Extractor.calculateRatingForTweet(entry)  
		}

	@staticmethod	
	def getHashTagsFromHTTexts(hashtagTexts):
		hashtags = []

		for ht in hashtagTexts:
			hashtags.append(
				{
					Contract.ADD_TO_TABLE_KEY: Contract.TABLE_HASHTAG,
					Contract.TEXT_LOWER_CASE_COLUMN: ht,
					Contract.COUNT_COLUMN: 1
				}
			)
		
		return hashtags

	@staticmethod	
	def getWeekFromEntry(entry):
		return {
			Contract.ADD_TO_TABLE_KEY: Contract.TABLE_WEEK,
			Contract.START_DATE_COLUMN: Extractor.getWeekStart(entry),
			Contract.END_DATE_COLUMN: Extractor.getWeekEnd(entry)
		}

	@staticmethod
	def getUsedIns(week, hashtags):
		
		usedIns = []
		startDate = week[Contract.START_DATE_COLUMN]

		for ht in hashtags:
			usedIns.append(
				{
					Contract.ADD_TO_TABLE_KEY: Contract.TABLE_USED_IN,
					Contract.HASHTAG_TEXT_COLUMN: ht,
					Contract.WEEK_START_DATE_COLUMN: startDate,
					Contract.COUNT_COLUMN: 1
				}
			)

		return usedIns


	@staticmethod
	def getPostedIn(week, tweet):
		return {
			Contract.ADD_TO_TABLE_KEY: Contract.TABLE_POSTED_IN,
			Contract.TWEET_ID_COLUMN: tweet[Contract.ID_COLUMN],
			Contract.WEEK_START_DATE_COLUMN: week[Contract.START_DATE_COLUMN]
		}

	@staticmethod
	def getContains(tweet, hashtags):
		
		contains = []
		tweetid = tweet[Contract.ID_COLUMN]

		for ht in hashtags:
			contains.append(
				{
					Contract.ADD_TO_TABLE_KEY: Contract.TABLE_CONTAINS,
					Contract.HASHTAG_TEXT_COLUMN: ht,
					Contract.TWEET_ID_COLUMN: tweetid
				}
			)

		return contains

	@staticmethod
	def getUsedTogetherWithFromHTTexts(hashtagTexts):
		
		pairs = Utils.getUniquePairs(hashtagTexts)
		usedTogetherWiths = []

		for pair in pairs:
			usedTogetherWiths.append(
				{
					Contract.ADD_TO_TABLE_KEY: Contract.TABLE_USED_TOGETHER_WITH,
					Contract.PRIMARY_HASHTAG_COLUMN: pair[0],
					Contract.TOGETHER_WITH_HASHTAG_COLUMN: pair[1],
					Contract.COUNT_COLUMN: 1
				}
			)

		return usedTogetherWiths

	@staticmethod
	def parseRow(row, dbController):

		hashtagTexts = Extractor.extractHashtags(row)

		tweet = TableParser.getTweetFromEntry(row)
		week = TableParser.getWeekFromEntry(row)
		hashtags = TableParser.getHashTagsFromHTTexts(hashtagTexts)

		usedIns = TableParser.getUsedIns(week, hashtagTexts)
		postedIn = TableParser.getPostedIn(week, tweet)
		contains = TableParser.getContains(tweet, hashtagTexts)
		usedTogetherWiths = TableParser.getUsedTogetherWithFromHTTexts(hashtagTexts)

		dbController.addMultiple(tweet, week, hashtags, usedIns, postedIn, contains, usedTogetherWiths)

	@staticmethod
	def parseTables():
		dbController = DBController()

		for row in TableParser.csv_reader:
		    TableParser.parseRow(row, dbController)

		dbController.close()

TableParser.parseTables()


