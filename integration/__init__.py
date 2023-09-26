import sys
import pygsheets
import pymongo
import time
import json


# Get values from command line
GOOGLE_SHEETS_SECRETS_PATH = sys.argv[1]
GOOGLE_SHEETS_ID = sys.argv[2]
MONGODB_URI = sys.argv[3]



# Configure Google Sheets
sheets_client = pygsheets.authorize(client_secret=GOOGLE_SHEETS_SECRETS_PATH)
sheet = sheets_client.open_by_key(GOOGLE_SHEETS_ID)
worksheet = sheet.sheet1


# Configure MongoDB
mongodb_client = pymongo.MongoClient(MONGODB_URI)
database = mongodb_client["5409-rfid-checkin"]
users_collection = database["users"]


# Define functions to handle actions

def handle_check_in_or_out(user_id):
    user = users_collection.find_one({"user_id": user_id})

    if (user != None):
        if user["check_in_status"] == True:
            check_out_user(user)
        else:
            check_in_user(user)

    else:
        print("User not found. Creating new user...")
        user_name = input("Enter user name: ")
        create_user(user_id, user_name)

    # Update list on Google Sheets to be handled by Google Apps Script
    first_cell = worksheet.cell("A1")
    first_cell.set_value(json.dumps(get_all_users()))


def check_in_user(user):
    users_collection.update_one({"user_id": user["user_id"]}, 
                                {"$set":
                                    {"since": int(time.time()),
                                    "check_in_status": True}})
    users_collection.update_one({"user_id": user["user_id"]}, {"$push": {"check_ins": int(time.time())}})
    
    print(f"SUCCESS: Checked in user '{user['name']}'.")


def check_out_user(user):
    current_time = int(time.time())
    add_elapsed = current_time - user["since"]

    users_collection.update_one({"user_id": user["user_id"]}, 
                                {"$set":
                                    {"since": current_time,
                                    "check_in_status": False,
                                    "elapsed_sec": user["elapsed_sec"] + add_elapsed}})
    users_collection.update_one({"user_id": user["user_id"]}, {"$push": {"check_outs": int(time.time())}})
    print(f"SUCCESS: Checked out user '{user['name']}'.")


def create_user(user_id, user_name):
    if (users_collection.find_one({"user_id": user_id}) != None):
        print("ERROR: User with ID already exists. Please delete this user from MongoDB or use a new ID.")
    else:
        users_collection.insert_one({"user_id": user_id, "name": user_name, "check_in_status": False, "since": int(time.time()), "elapsed_sec": 0, "check_ins": [], "check_outs": []})
        handle_check_in_or_out()
        print(f"SUCCESS: User '{user_name}' has been created and checked in.")


def get_all_users():
    users = list(users_collection.find())
    for user in users:
        del user["_id"]
    return users

