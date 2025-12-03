import pyrebase
import os
import json
from datetime import datetime


FIREBASE_CONFIG_FILE = os.environ.get("FIREBASE_CONFIG_FILE", ".secrets/firebase.json")
with open(FIREBASE_CONFIG_FILE) as f:
  firebaseConfig = json.load(f)

firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

def save_pill_database(uid, id_token, medicine, quantity, date, note):
    result = db.child('users') \
        .child(uid) \
        .child('medicines') \
        .push({
            'medicine_name': medicine,
            'quantity': quantity,
            'date': date,
            'note': note
        }, id_token)
    
    return result['name'] # Pyrebase returns {'name': '<NEW_KEY>'}



def load_medicines_for_user(uid, id_token, year, month) -> dict[str, list[dict]]:
    result = db.child('users').child(uid).child('medicines').get(id_token)
    data_by_date = {}
    
    if not result.each():
        return data_by_date

    for item in result.each():
        key = item.key()
        value = item.val()
        date_str = value['date']
        date = datetime.strptime(date_str, '%Y-%m-%d')
        if date.year == year and date.month == month:
            pill = {
                'key': key,
                'medicine_name': value['medicine_name'],
                'quantity': value['quantity'],
                'note': value['note']
            }
            data_by_date.setdefault(date_str, []).append(pill)
    return data_by_date


def delete_pill_database(uid, id_token, key):
    try:
        db.child("users") \
          .child(uid) \
          .child("medicines") \
          .child(key) \
          .remove(id_token)
        
        # print(f'Successfully removed record {key}')
        return True
    
    except Exception as e:
        # print(f'Failed to remove record {key}: {e}')
        return False