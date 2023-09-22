import sys
import pygsheets
import pymongo
import time
import json


# Get values from command line
ACTION = sys.argv[1]
USER_ID = sys.argv[2]
FULL_NAME = sys.argv[3]
GOOGLE_SHEETS_SECRETS_PATH = sys.argv[4]
GOOGLE_SHEETS_ID = sys.argv[5]
MONGODB_URI = sys.argv[6]



# Configure Google Sheets
sheets_client = pygsheets.authorize(client_secret=GOOGLE_SHEETS_SECRETS_PATH)
sheet = sheets_client.open_by_key(GOOGLE_SHEETS_ID)
worksheet = sheet.sheet1
# TODO: Integrate Google Sheets


# Configure MongoDB
mongodb_client = pymongo.MongoClient(MONGODB_URI)
database = mongodb_client["5409-rfid-checkin"]
users_collection = database["users"]


# Define functions to handle actions

def handle_check_in_or_out():
    user = users_collection.find_one({"user_id": USER_ID})

    if (user != None):
        if user["check_in_status"] == True:
            check_out_user(user)
        else:
            check_in_user(user)

    else:
        print("ERROR: User with ID does not exist. Please create new user or use a different ID.")


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


def create_user():
    if (users_collection.find_one({"user_id": USER_ID}) != None):
        print("ERROR: User with ID already exists. Please delete this user from MongoDB or use a new ID.")
    else:
        users_collection.insert_one({"user_id": USER_ID, "name": FULL_NAME, "check_in_status": False, "since": int(time.time()), "elapsed_sec": 0, "check_ins": [], "check_outs": []})
        handle_check_in_or_out()
        print(f"SUCCESS: User '{FULL_NAME}' has been created and checked in.")


def get_all_users():
    users = list(users_collection.find())
    for user in users:
        del user["_id"]
    return users



# Actions list
valid_actions = {
    "checkin": handle_check_in_or_out,
    "create": create_user
}

# Run action
valid_actions[ACTION]()

# Update list on Google Sheets to be handled by Google Apps Script
first_cell = worksheet.cell("A1")
first_cell.set_value(json.dumps(get_all_users()))