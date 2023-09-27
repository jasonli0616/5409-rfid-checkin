import pygsheets
import pymongo
import time
import json


# Get values
with open("config.json", "r") as f:
    json_data = json.load(f)
    GOOGLE_SHEETS_SECRETS_PATH = json_data["GOOGLE_SHEETS_SECRETS_PATH"]
    GOOGLE_SHEETS_ID = json_data["GOOGLE_SHEETS_ID"]
    MONGODB_URI = json_data["MONGODB_URI"]



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
    users_collection.insert_one({"user_id": user_id, "name": user_name, "check_in_status": False, "since": int(time.time()), "elapsed_sec": 0, "check_ins": [], "check_outs": []})
    handle_check_in_or_out(user_id)
    print(f"SUCCESS: User '{user_name}' has been created and checked in.")


def get_all_users():
    users = list(users_collection.find())
    for user in users:
        del user["_id"]
    return users

