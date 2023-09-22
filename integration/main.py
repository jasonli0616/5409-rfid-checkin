import sys
import pygsheets
import pymongo


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


# Configure MongoDB
mongodb_client = pymongo.MongoClient(MONGODB_URI)
database = mongodb_client["5409-rfid-checkin"]
users_collection = database["users"]


# Define functions to handle actions

def check_in_user():
    ...


def check_out_user():
    ...


def create_user():
    ...



# Actions list
valid_actions = {
    "checkin": check_in_user,
    "checkout": check_out_user,
    "create": create_user
}