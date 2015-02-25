import requests
import json
import config 
import os 

# This file creates the foursquare response as a python dict. Pass this function to the server to execute with the user's query

def create_fs_dict(CLIENT_ID, CLIENT_SECRET, user_query, location):
	url = 'https://api.foursquare.com/v2/venues/search?client_id='+ CLIENT_ID + '&client_secret=' + CLIENT_SECRET + '&v=20150201'
	myparams = {'query': user_query, 'near': location, 'limit': '15', 'categoryId': '4d4b7105d754a06374d81259'}		# categoryId limits responses to only 'food' category
	response = requests.get(url, params = myparams)		# create API response  
	response_obj = response.text						# returns the content (text) of the server's response 
	fs_dict = json.loads(response_obj)					# takes a JSON string & turns it into a Python dict
	if fs_dict['meta']['code'] != 200:					# if the response returns an error (antyhing but a 200 HTTP )
		raise Exception('Foursquare query error')
	return fs_dict 

