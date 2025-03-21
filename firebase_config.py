import firebase_admin
from firebase_admin import credentials, firestore, auth

# Initialize Firebase Admin SDK
cred = credentials.Certificate("f1-app-61258-firebase-adminsdk-fbsvc-a77194ad01.json") 
firebase_admin.initialize_app(cred)

db = firestore.client()
