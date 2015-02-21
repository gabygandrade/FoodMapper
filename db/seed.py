import model
import csv
from datetime import datetime

def load_users(session):
    with open('seed_data/u.user', 'rb') as file:
        reader = csv.reader(file, delimiter= '\t')  
        for row in reader:
            username = row[0]
            email = row[1]
            password = [2]
            u = model.User(username = username, email=email, password=password)       
            session.add(u)
    session.commit()

# def load_restaurants(session):
#     # use u.restaurants
#     with open('seed_data/u.restaurants', 'rb') as file:
#         reader = csv.reader(file, delimiter = '|')
#         for row in reader:
#             # title = row[1].decode("latin-1")
#             # if row[2] != "":
#             #     rel_date = datetime.strptime(row[2], "%d-%b-%Y")
#             # else:
#             #     rel_date = None
#             # url= row[4]
#             # m = model.Movie(title=title, rel_date=rel_date, url=url)
#             session.add(m)
#     session.commit()

# def load_userrests(session):
#     # use u.userrests
#     with open('seed_data/u.data', 'rb') as file:
#         reader = csv.reader(file, delimiter = '\t')
#         for row in reader:
#             # rating = row[2]
#             # user_id = row[0]
#             # movie_id = row[1]
#             # r = model.Rating(user_id=user_id,movie_id=movie_id,rating=rating)
#             session.add(r)
#     session.commit()

def main(session):
    # You'll call each of the load_* functions with the session as an argument
    load_users(session)
    load_restaurants(session)
    load_userrests(session)

if __name__ == "__main__":
    # s= model.connect()
    s = model.session
    main(s)