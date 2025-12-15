import firebase_admin
from firebase_admin import credentials, storage as admin_storage
import os

SERVICE_ACCOUNT_FILE = os.environ.get('SERVICE_ACCOUNT_FILE', '.secrets/service_account.json')

if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'medbook-2bed9.appspot.com'
    })


def delete_file_from_storage(storage_path: str):
    try:
        bucket = admin_storage.bucket()
        blob = bucket.blob(storage_path)
        
        if not blob.exists():
            # print(f'File already deleted or not found: {storage_path}')
            return

        blob.delete()
        # print(f'Successfully deleted: {storage_path}')

    except Exception as e:
        # print(f'Error deleting file: {e}')
        pass