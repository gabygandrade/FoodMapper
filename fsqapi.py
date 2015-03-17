import requests
import json
import config 
import os 

fsq_client_id = config.FSQ_CLIENT_ID 			
fsq_client_secret = config.FSQ_CLIENT_SECRET

def search_venues(CLIENT_ID, CLIENT_SECRET, user_query, location):
	"""Creates an HTTP request to the Foursquare API with the user's query and location, 
	return the JSON response, and then convert it to a python dictionary"""
	
	url = 'https://api.foursquare.com/v2/venues/search?client_id='+ CLIENT_ID + '&client_secret=' + CLIENT_SECRET + '&v=20150201'
	myparams = {'query': user_query, 'near': location, 'limit': '10', 'categoryId': '4d4b7105d754a06374d81259'}		# categoryId limits responses to only 'food' category
	response = requests.get(url, params = myparams)		# create API request the given parameters
	response_obj = response.text						# returns the text of the server's response 
	fs_dict = json.loads(response_obj)					# takes a JSON string & turns it into a Python dict
	
	if fs_dict['meta']['code'] != 200:					# if the response returns an error (anything but a 200 HTTP )
		raise Exception('Foursquare query error')
	return fs_dict 

# test = search_venues(fsq_client_id, fsq_client_secret, 'food truck', 'sf')
# obj = test['response']['venues'][0]
