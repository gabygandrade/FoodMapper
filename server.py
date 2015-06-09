from flask import Flask, render_template, redirect, request, g, url_for, flash, make_response, jsonify
from flask import session
from db import model
import jinja2
import os
import fsqapi
import config
import json

app = Flask(__name__)
app.secret_key = config.APP_SECRET_KEY
app.jinja_env.undefined = jinja2.StrictUndefined 

fsq_client_id = config.FSQ_CLIENT_ID 			
fsq_client_secret = config.FSQ_CLIENT_SECRET

@app.route("/")
def display_home_page():
	"""Renders the home page"""
	return render_template("index.html")

@app.route("/welcome")
def display_welcome():
	"""User welcome page showing options"""
	
	logged_in_user_id = session['user_id']
	logged_in_username = session['username']

	pending_recs = model.session.query(model.Recommendation).filter(
	model.Recommendation.recipient_id == logged_in_user_id, model.Recommendation.pending==True).all()

	return render_template("welcome.html", username = logged_in_username, recommendations=pending_recs)

@app.route("/login", methods=['POST'])
def login_user():
	"""Makes POST request to get user input and add user info to the session"""
	
	# Pull needed info out of request object
	username = request.form['username']
	# email = request.form['email']
	password = request.form['password']

	all_users = model.session.query(model.User)
	
	# Add the info from the request object as keys to the session dict
	try:
		user = all_users.filter(model.User.username==username, model.User.password==password).one()
		session['username'] = user.username
		# session['user_email'] = user.email
		session['user_id'] = user.id
		session['logged_in'] = True
		# flash ("You are logged in")
		# print session
		return redirect("/welcome") 
	except:
		# flash("That email or password is incorrect. Please try again")
		return render_template("login.html")

# @app.route("/signup", methods=['POST'])
# def sign_up():
# 	"""Makes POST request to create a new user in the db and initiative a new session"""
# 	username = request.form['username']
# 	email = request.form['email']
# 	password = request.form['password']

# 	# check if this info matches a username already in the db
# 	existing_username = session.query(User).filter(User.username==username).one()

# 	if existing_username:
# 		flash("A user already exists with this username. Please choose another username.")
# 	else:
# 	# if it does't, add the new user to the db and session & log the user in
# 	new_user = model.User(username=username, email=email, password=password)
# 	model.session.add(new_user)
# 	model.session.commit()

# 	logged_in_user = model.session.query(User).filter(model.User.username==username, model.User.password==password).one()

# 	session['username'] = logged_in_user.username
# 	session['user_id'] = logged_in_user.id
# 	session['logged_in'] = True

# 	return redirect("/welcome") 

@app.route("/logout")
def logout():
	"""Logs user out and clears session"""
	session.clear()
	# print session 
	# flash ("You have been logged out")
	return redirect("/") 

@app.route("/restaurant-results")
def show_restaurant_info():
	"""When the user submits their search, gather the user input 
	to create the query request to the Foursquare (FSQ) API. 
	Return the response as a python dictionary and pass it to the 
	template"""

	search_restaurant = request.args.get('search-restaurant')
	search_location = request.args.get('search-location')

	if search_restaurant and search_location:
		try:
			fsq_dict = fsqapi.search_venues(fsq_client_id, fsq_client_secret, search_restaurant, search_location) 	# Look in foursquareapi module and create fsq dict function with the parameters here
			# parse that python dict to get just the part of the request w/needed venues info
			fsq_venues_list = fsq_dict['response']['venues']
			# print "FSQ Venues List: ", fsq_venues_list

			# if FSQ query returned no search results
			if fsq_venues_list == []:								
				flash("We're sorry, your search came up empty. Please try another search.") 
			
			return render_template("restaurant_results.html", fsq_venues=fsq_venues_list)
		except Exception as e:
			flash("There was an error with your search. Please check your spelling.")
			print "FSQ QUERY ERROR IS: ", e.message
			return redirect(request.referrer)	 
	
	elif not search_restaurant:
		flash("Please enter a cuisine or restaurant name.")
	
	elif not search_location:
		flash("Please enter a location.")
	
	return redirect(request.referrer)	

@app.route("/save-db", methods=['POST'])	
def save_to_db():
	"""Saves the restaurant and the bookmark as new records in the db"""
	
	logged_in_user_id = session['user_id']

	# pulls the needed fields from the request object
	name = request.form["name"]
	fsq_id = request.form["id"]
	lat = request.form["lat"]
	lng = request.form["lng"]
	cuisine = request.form["cuisine"]
	address = request.form["address"]
	city = request.form["city"]
	state = request.form["state"]
	url = request.form["url"]
	phone = request.form["phone"]
	icon_url = request.form["iconurl"]

	# print "request object: ", request.form

	saved_restaurant = model.session.query(model.Restaurant).filter(model.Restaurant.fsq_id==fsq_id).first()
	saved_bookmark = model.session.query(model.Bookmark).filter(model.Bookmark.user_id==logged_in_user_id, 			
		model.Bookmark.restaurant.has(model.Restaurant.fsq_id==fsq_id)).first()

	#If the restaurant DOESN'T exist in the db (& thus implicitly the bookmark doesn't exist)
	if not saved_restaurant: 
		# save a new restaurant to the restaurants table
		new_restaurant = model.Restaurant(fsq_id=fsq_id, name=name, 
						lat=lat, lng=lng, cuisine=cuisine, address=address, city=city, state=state, url=url, phone=phone, icon_url = icon_url)
		model.session.add(new_restaurant)
		model.session.commit()

		# refresh to refer to the SQLAlchemy reference for the new_restaurant
		model.session.refresh(new_restaurant) 

		# save a new bookmark to the bookmarks table
		new_bookmark = model.Bookmark(user_id=logged_in_user_id, restaurant_id=new_restaurant.id)		
		model.session.add(new_bookmark)
		model.session.commit()

		return jsonify({"message": "You added %s to your bookmarks!" % new_restaurant.name}) 

	# the bookmark ALREADY exists for the user (& thus the restaurant also already exists) - ie. the restaurant id is already associated with that user 
	elif saved_bookmark:
		return jsonify({"message": "You already bookmarked this restaurant!"}) 

	# elif the restaurant DOES exist BUT the bookmark doesn't exist for this user - ie. the restaurant id is not associated with a bookmark for this user
	elif saved_restaurant and not saved_bookmark:
		new_bookmark = model.Bookmark(user_id=logged_in_user_id, restaurant_id=saved_restaurant.id)		
		model.session.add(new_bookmark)
		model.session.commit()
		return jsonify({"message": "You added %s to your bookmarks!" % saved_restaurant.name})	

@app.route("/user_info")
def get_user_info():
	"""Send user info to the modal so it can populate the modal that the user sees
	when they click recommend"""
	# query for all the usernames in the database
	all_usernames = model.session.query(model.User.username)

	logged_in_username = session['username']

	# create a list with all usernames except for the user who is currently logged in
	usernames = [user.username for user in all_usernames if user.username!=logged_in_username]

	# send this list as JSON
	return jsonify({"username": usernames})

@app.route("/map")
def show_map():
	"""Render map"""
	return render_template("map.html")	

@app.route("/bookmark-info")
def return_bookmark_info():
	"""Return information about the user's bookmarks to populate map and list"""

	logged_in_user_id = session['user_id']

	data = model.session.query(model.Bookmark).filter(model.Bookmark.user_id==logged_in_user_id).all()

	restaurant_info = {}
	for bkm in data:
		restaurant_info[bkm.id] = {}						
		restaurant_info[bkm.id]["fsq_id"] = bkm.restaurant.fsq_id
		restaurant_info[bkm.id]["name"] = bkm.restaurant.name
		restaurant_info[bkm.id]["lat"] = bkm.restaurant.lat
		restaurant_info[bkm.id]["lng"] = bkm.restaurant.lng
		restaurant_info[bkm.id]["cuisine"] = bkm.restaurant.cuisine
		restaurant_info[bkm.id]["address"] = bkm.restaurant.address
		restaurant_info[bkm.id]["phone"] = bkm.restaurant.phone
		restaurant_info[bkm.id]["url"] = bkm.restaurant.url
		restaurant_info[bkm.id]["icon_url"] = bkm.restaurant.icon_url
		if len(bkm.bookmarkrecs) > 0:
			bkmrecs = bkm.bookmarkrecs
			# recommender_list = []
			for item in bkmrecs:
				restaurant_info[bkm.id]["recommender_username"] = item.recommendation.recommender.username
	# print restaurant_info

	return jsonify(restaurant_info)

@app.route("/delete-bookmark", methods=["POST"])
def delete_bookmark(): 
	"""Delete the user's selected bookmark """
	logged_in_user_id = session['user_id']

	# get the bookmark id for the bookmark the user wants to delete 
	bkm_id_to_delete = request.form['bookmarkId']
	
	bkm_to_delete = model.session.query(model.Bookmark).filter(model.Bookmark.user_id==logged_in_user_id, 
		model.Bookmark.id==bkm_id_to_delete).first()
	# print "Bookmark to delete ", bkm_to_delete
	
	restaurant_to_delete = bkm_to_delete.restaurant.name
	# print "Restaurant name to delete ", restaurant_to_delete
	
	# delete the restaurant from the db 
	model.session.delete(bkm_to_delete)
	model.session.commit()

	# return "This string!"
	return jsonify({"message": "You deleted %s from your bookmarks." % restaurant_to_delete}) 

@app.route("/recommend", methods=['POST'])
def recommend_restaurant():
	"""Send information to server for one user to recommend a restaurant to another"""

	recommender_id = session['user_id']

	#get the user id of the recipient (from request obj), as well as rest of info needed to save to db 
	recipient_username = request.form['usernameRecipient']
	name = request.form["name"]
	fsq_id = request.form["fsqId"]
	lat = request.form["lat"]
	lng = request.form["lng"]
	cuisine = request.form["cuisine"]
	address = request.form["address"]
	city = request.form["city"]
	state = request.form["state"]
	url = request.form["url"]
	phone = request.form["phone"]
	icon_url = request.form["icon_url"]

	# print "Request object: ", request.form

	# query for the recipient 
	recipient = model.session.query(model.User).filter(model.User.username==recipient_username).first()
	
	print "***recipient: ", recipient
	print "***recipient id: ", recipient.id

	# query to check if that restaurant is already in restaurants table
	saved_restaurant = model.session.query(model.Restaurant).filter(model.Restaurant.fsq_id==fsq_id).first()

	# query to check if the recipient already has that restaurant bookmarked 
	saved_bookmark = model.session.query(model.Bookmark).filter(model.Bookmark.user_id==recipient.id, 			
		model.Bookmark.restaurant.has(model.Restaurant.fsq_id==fsq_id)).first()

	saved_recommendation = model.session.query(model.Recommendation).filter(model.Recommendation.recommender_id==recommender_id, 
		model.Recommendation.recipient_id==recipient.id, model.Recommendation.restaurant.has(model.Restaurant.fsq_id==fsq_id)).first()
	# print "*********Saved recommendation: ", saved_recommendation

	if not saved_restaurant:
		# save the restaurant to db
		new_restaurant = model.Restaurant(fsq_id=fsq_id, name=name, 
						lat=lat, lng=lng, cuisine=cuisine, address=address, city=city, 
						state=state, url=url, phone=phone, icon_url = icon_url)
		model.session.add(new_restaurant)
		model.session.commit()

		# refresh to refer to the SQLAlchemy reference for the new_restaurant
		model.session.refresh(new_restaurant) 

		# save a new recommendation 
		new_recommendation = model.Recommendation(restaurant_id=new_restaurant.id, 
			recommender_id=recommender_id, recipient_id=recipient.id, pending=True)		
		model.session.add(new_recommendation)
		model.session.commit()

		return jsonify({"message": "You recommended %s to %s!" % (new_restaurant.name, recipient_username)}) 

	elif saved_recommendation:
		return jsonify({"message": "You already recommended %s to %s!" % (saved_restaurant.name, recipient_username)}) 

	elif saved_bookmark:
		return jsonify({"message": "%s already has this restaurant bookmarked." % recipient_username}) 

	else:
		new_recommendation = model.Recommendation(restaurant_id=saved_restaurant.id, 
		recommender_id=recommender_id, recipient_id=recipient.id, pending=True)		
		model.session.add(new_recommendation)
		model.session.commit()
		return jsonify({"message": "You recommended %s to %s!" % (saved_restaurant.name, recipient_username)}) 

@app.route("/recommendations")
def show_recommendations():
	"""Create a dict with all the information about a user's recommendations, and 
	send it as JSON to show notifications"""
	
	logged_in_user_id = session['user_id']
	logged_in_username = session['username']

	recommendations = model.session.query(model.Recommendation).filter(
		model.Recommendation.recipient_id == logged_in_user_id, model.Recommendation.pending==True).all()

	# for rec in recommendations:
	# 	print rec.id
	# 	print rec.restaurant.name
	# 	print rec.recommender.username  
	# 	print rec.recipient.username

	# creat a dict with all needed info to render restaurant info & edit recommendation
	rec_data = {}
	for rec in recommendations:
		rec_data[rec.id] = {}						# item.id == bookmark id 
		rec_data[rec.id]["bkm_id"] = rec.id
		rec_data[rec.id]["rest_id"] = rec.restaurant.id
		rec_data[rec.id]["recommender_username"] = rec.recommender.username
		rec_data[rec.id]["recipient_username"] = rec.recipient.username
		rec_data[rec.id]["rest_name"] = rec.restaurant.name
		rec_data[rec.id]["rest_cuisine"] = rec.restaurant.cuisine
		rec_data[rec.id]["rest_address"] = rec.restaurant.address
		rec_data[rec.id]["rest_city"] = rec.restaurant.city
		rec_data[rec.id]["rest_state"] = rec.restaurant.state
		rec_data[rec.id]["rest_url"] = rec.restaurant.url
		rec_data[rec.id]["rec_pending"] = rec.pending

	# print rec_data

	return render_template("recommendations.html", recommendations = rec_data, username = logged_in_username)

@app.route("/accept-recommendation")
def accept_recommendation():
	"""Route to accept the recommendation and add to the db as appropriate"""
	logged_in_user_id = session['user_id']

	# get the restaurant id associated with the recommendation
	rest_id = request.args['restId']
	
	# query for the specific user's recommendation(s)
	recommendations = model.session.query(model.Recommendation).filter(model.Recommendation.recipient_id==logged_in_user_id, 
		model.Recommendation.restaurant_id==rest_id).all()
	# print "\n \n RECOMMENDATION(S) to change ", recommendations

	saved_bookmark = model.session.query(model.Bookmark).filter(model.Bookmark.user_id==logged_in_user_id, 			
		model.Bookmark.restaurant_id==rest_id).first()

	# print "***** SAVED BOOKMARK?? ", saved_bookmark
	
	# go through each recommendation and change the pending status from True to False 
	for rec in recommendations:
		rec.pending = False
	model.session.commit()

	#if the bookmark does not already exist for this restaurant, add it to bookmarks and bookmarkrecommendation table
	if not saved_bookmark:
		# save a new bookmark
		new_bookmark = model.Bookmark(user_id=logged_in_user_id, restaurant_id=rest_id)		
		model.session.add(new_bookmark)
		model.session.commit()

		# refresh to refer to the SQLAlchemy reference for the new_bookmark
		model.session.refresh(new_bookmark) 
		
		# for each recommendation associated with that restaurant, save a new bookmarkrecommendation
		for rec in recommendations:
			new_bookmarkrecommendation = model.BookmarkRecommendation(bookmark_id=new_bookmark.id, recommendation_id=rec.id)
			model.session.add(new_bookmarkrecommendation)
		model.session.commit()

		return jsonify({"message": "You successfully added %s to your bookmarks!" % new_bookmark.restaurant.name}) 

	else:
		return jsonify({"message": "You already bookmarked this restaurant!"}) 


@app.route("/deny-recommendation")
def deny_recommendation():
	"""Route to deny the recommendation"""
	logged_in_user_id = session['user_id']

	# get the restaurant id associated with the recommendation
	rest_id = request.args['restId']
	
	# query for the recommendation(s) to change
	recommendations = model.session.query(model.Recommendation).filter(model.Recommendation.recipient_id==logged_in_user_id, 
		model.Recommendation.restaurant_id==rest_id).all()
	# print "\n \n \n RECOMMENDATION(s) to change ", recommendations
	
	for rec in recommendations:
		rec.pending = False
	model.session.commit()

	return jsonify({"message": "You denied this restaurant recommendation."}) 

if __name__ == "__main__":
    app.run(debug = True)





