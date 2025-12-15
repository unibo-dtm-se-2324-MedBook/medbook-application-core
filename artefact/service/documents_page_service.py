import pyrebase
import os
import json
from artefact.service.database import db
import uuid
import requests
from artefact.service.admin_delete_from_storage import delete_file_from_storage


FIREBASE_CONFIG_FILE = os.environ.get("FIREBASE_CONFIG_FILE", ".secrets/firebase.json")
with open(FIREBASE_CONFIG_FILE) as f:
    firebaseConfig = json.load(f)

firebase = pyrebase.initialize_app(firebaseConfig)
storage = firebase.storage()


def upload_user_document(uid: str, token: str, file_path: str):
    file_name = os.path.basename(file_path)
    unique_name = f'{uid}/{uuid.uuid4()}_{file_name}' # function from the uuid module that generates a random UUID version 4. Use it for a unique file name

    storage.child(unique_name).put(file_path, token)

    public_url = storage.child(unique_name).get_url(token)
    if 'alt=media' not in public_url:
        public_url += '&alt=media'

    db.child('users').child(uid).child('documents').push({
        'name': file_name,
        'url': public_url,
        'storage_path': unique_name
    }, token)


def load_user_documents(uid: str, token: str) -> dict:
    documents = db.child('users').child(uid).child('documents').get(token)
    return documents.val() if documents.each() else {}


def download_file_from_url(url, saved_path, token):
    try:  
        headers = {'Authorization': f'Bearer {token}'}  
        response = requests.get(url, headers = headers)
        response.raise_for_status()

        content_type = response.headers.get('Content-Type', '')
        if 'image/jpeg' in content_type:
            ext = '.jpg'
        elif 'image/png' in content_type:
            ext = '.png'
        elif 'application/pdf' in content_type:
            ext = '.pdf'
        else:
            raise ValueError(f'Unsupported file format: {content_type}')
        base, current_ext = os.path.splitext(saved_path)
        if not current_ext and ext:
            saved_path += ext

        with open(saved_path, 'wb') as f:
            f.write(response.content)

    except Exception as e:
        # print(f'Download failed: {e}')
        pass


def delete_user_document(uid: str, token: str, doc_id: str, storage_path: str):
    try:
        delete_file_from_storage(storage_path)
        db.child('users').child(uid).child('documents').child(doc_id).remove(token)

    except Exception as e:
        # print(f'Error while deleting document: {e}')
        pass