from flask import Flask, render_template, redirect, request, g, url_for, flash, make_response 
from flask import session as fsess
# import model
import jinja2
import os
import foursquareapi
import config

app = Flask(__name__)
app.secret_key = config.APP_SECRET_KEY
app.jinja_env.undefined = jinja2.StrictUndefined 

fs_client_id = config.FS_CLIENT_ID 			
fs_client_secret = config.FS_CLIENT_SECRET

@app.route("/")
def index():
	"""Render the page where users can search for a restaurant """
	return render_template("index.html")

@app.route("/restaurant_results")
def show_rest_info():
	"""When the user submits their search, gather the user input 
	to create the query request to the Foursquare (FSQ) API. 
	Return the response as a python dictionary and pass it to the 
	template"""
	
	# pull out parameters from request
	search_restaurant = request.args.get('rest-name')
	search_location = request.args.get('search-location')
	print (search_restaurant, search_location)
	# create a python dict from the Foursquare API JSON response 
	
	try:
		fs_dict = foursquareapi.search_FSQ_venues(fs_client_id, fs_client_secret, search_restaurant, search_location) 	# Look in foursquareapi module and run the create_fs_dict function with the parameters here
		# parse that python dict to get just the part of the request w/needed venues info
		fs_venues_list = fs_dict['response']['venues']
		# print "FS Venues List: ", fs_venues_list

		# if FSQ query returned no search results  
		if fs_venues_list == []:								
			flash("Your search came up empty. Please try another search.") 
		
		return render_template("restaurant_results.html", 
		fs_venues_list=fs_venues_list)

	except:
		# if the user entered a location FSQ cannot geocode				
		fs_venues_list = []
		flash("Please enter a city name.") 
		return redirect('/')

@app.route("/save_restaurant")		# FIXME: change name of this route to save_to_db()
def save_restaurant():					# Do I need to make a call to the foursquare API again here to get the restaurant info to populate my tables? 
	"""Saves the restaurant and the bookmark as new records in the db"""
	
	# pulls the needed fields from the request object
	name = request.args["name"]
	fsq_id = request.args["fsqId"]
	lat = request.args["lat"]
	lng = request.args["lng"]
	cuisine = request.args["cuisine"]
	print request.args

	# FIXME: Needed for the new bookmark record: 
	# this_user_id = model.session.query(model.User).get(id)
	# this_restaurant_id = 

	print "Name: ", name
	print "FSQ ID: ", fsq_id
	print "Lat: ", lat 
	print "Lng: ", lng 
	print "Cuisine: ", cuisine 

	# new_bookmark = model.Bookmark(user_id=this_user_id, 
	# 	restaurant_id=this_restaurant_id)

	# new_restaurant = model.Restaurant(fsq_id=fsq_id, name = name, 
	# 					lat=lat, lng=lng, cuisine=cuisine)

	# model.session.add_all(new_bookmark, new_restaurant)
	# model.session.commit()

	 # 	TO ADD: 
	 # if bookmark is not in the db & restaurant in NOT in the db:
	 # 	save bookmark
	 # 	save restaurant
	 # if bookmark is in the db & restaurant IS in the db:
	 # 	save bookmark 
	 # if bookmark is in the db 
	 # 	flash "You have already added this bookmark."

	return fsq_id
 	# return "<name=%s fsq_id=%d lat=%d lng=%d cuisine=%s>" % (name,
 	# fsq_id,  lat, lng, cuisine)

	# return "Added %s restaurant to the restaurants table" % (saved_restaurant)

if __name__ == "__main__":
    app.run(debug = True)

# Work on login after map

# @app.route("/login")
# def display_login():
# 	# Displays login page
# 	return render_template("login.html")

# @app.route("/login", methods=['POST'])
# def login_user():
# 	# Makes POST request to get user input to log into account
# 	print "login function running"
# 	email = request.form['email']
# 	password = request.form['password']
# 	print (email, password)
# 	# login = model.login(email, password)	# need to create login function in model to tie this back to 
# 	return redirect("/login") 

# def save_object(obj_instance):
# 	try:
# 		session.add(obj_instance)
# 		session.commit()
# 		return 200
# 	except:
# 		return 500