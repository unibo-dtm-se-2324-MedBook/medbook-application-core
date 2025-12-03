import pyrebase
import os
import json
import firebase_admin
from firebase_admin.auth import UserNotFoundError
from firebase_admin import auth as firebase_auth
from firebase_admin import credentials
import pickle # “Pickling” is the process whereby a Python object hierarchy is converted into a byte stream, and “unpickling” is the inverse operation, whereby a byte stream (from a binary file or bytes-like object) is converted back into an object hierarchy.
import os # provides functions for interacting with the operating system
from flet import SnackBar, Text


SERVICE_ACCOUNT_FILE = os.environ.get("SERVICE_ACCOUNT_FILE", ".secrets/service_account.json")
credential = credentials.Certificate(SERVICE_ACCOUNT_FILE)
firebase_admin.initialize_app(credential, {'storageBucket': 'medbook-2bed9.firebasestorage.app'})

FIREBASE_CONFIG_FILE = os.environ.get("FIREBASE_CONFIG_FILE", ".secrets/firebase.json")
with open(FIREBASE_CONFIG_FILE) as f:
  firebaseConfig = json.load(f)

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()


def create_user(name, surname, email, password):
  try:
    user = firebase_auth.create_user(
      email = email,
      password = password,
      display_name = name + '_' + surname)
    return user.uid # return user credentials [there is column in firebase database of users]
  except:
    return None

def check_email(email):
  try:
    user_uid = firebase_auth.get_user_by_email(email)
    # print('Successfully fetched user data: {0}'.format(user_uid.uid))
    return user_uid.email
  except UserNotFoundError:
    # print("Email wasn't found")
    return False 
  except Exception as e:
    # print(f"Other mistake: {e}")
    return None

def login_user(email, password):
  try:
    user = auth.sign_in_with_email_and_password(email, password)
    return user['idToken']
  except:
    return None

# Activate user['idToken']
def store_token(token):
  if os.path.exists('token.pickle'):
    os.remove('token.pickle') #  method is used to delete a file path. This method can not delete a directory and if directory is found it will raise an OSError
  with open('token.pickle', 'wb') as f: # Write + Binary mode
    pickle.dump(token, f) #  to store the object data to the file

# Update user information in authentication firebase
def change_user_info(name: str, surname: str, email: str, uid: str, page):
  try:
    firebase_auth.update_user(
      uid = uid,
      display_name = f'{name}_{surname}',
      email = email
    )

    page.snack_bar = SnackBar(
      content = Text('Info successfully updated'),
      open = True,
    )
    page.update()

  except firebase_auth.AuthError as e:
    page.snack_bar = SnackBar(
      content = Text(f'Error updating info: {str(e)}'),
      open = True,
    )
    page.update()

# Exit the account
def log_out(token):
  if os.path.exists('token.pickle'):
    os.remove('token.pickle')
