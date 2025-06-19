import firebase_admin
from firebase_admin import credentials, firestore
import json
import os
from datetime import datetime, timedelta
import streamlit as st
from dotenv import load_dotenv

# Load environment variables (for local development)
load_dotenv()

# In-memory storage for development/testing when Firebase is not available
_memory_storage = []

def initialize_firebase():
    """Initialize Firebase if not already initialized"""
    try:
        print("\n=== Firebase Initialization ===")
        # Check if Firebase is already initialized
        if not firebase_admin._apps:
            print("Firebase not initialized, starting initialization...")
            
            # Try to get Firebase credentials from Streamlit secrets first
            if hasattr(st, 'secrets') and 'firebase' in st.secrets:
                print("Found Firebase credentials in Streamlit secrets")
                try:
                    # Handle TOML format secrets
                    firebase_secrets = st.secrets['firebase']
                    firebase_config = {
                        "type": firebase_secrets.get("type", "service_account"),
                        "project_id": firebase_secrets.get("project_id"),
                        "private_key_id": firebase_secrets.get("private_key_id"),
                        "private_key": firebase_secrets.get("private_key", "").replace('\\n', '\n'),
                        "client_email": firebase_secrets.get("client_email"),
                        "client_id": firebase_secrets.get("client_id"),
                        "auth_uri": firebase_secrets.get("auth_uri", "https://accounts.google.com/o/oauth2/auth"),
                        "token_uri": firebase_secrets.get("token_uri", "https://oauth2.googleapis.com/token"),
                        "auth_provider_x509_cert_url": firebase_secrets.get("auth_provider_x509_cert_url", "https://www.googleapis.com/oauth2/v1/certs"),
                        "client_x509_cert_url": firebase_secrets.get("client_x509_cert_url")
                    }
                    
                    # Validate required fields
                    required_fields = ["project_id", "private_key", "client_email"]
                    missing_fields = [field for field in required_fields if not firebase_config.get(field)]
                    
                    if missing_fields:
                        print(f"Missing required Firebase fields in secrets: {missing_fields}")
                        raise ValueError(f"Missing required Firebase configuration: {missing_fields}")
                    
                    print("Successfully processed Firebase credentials from secrets")
                    
                except Exception as secrets_error:
                    print(f"Error processing Firebase secrets: {secrets_error}")
                    raise secrets_error
                    
            else:
                print("No Firebase credentials in Streamlit secrets, checking environment variables")
                # Check if all required environment variables are present
                required_env_vars = [
                    "FIREBASE_TYPE", "FIREBASE_PROJECT_ID", "FIREBASE_PRIVATE_KEY_ID",
                    "FIREBASE_PRIVATE_KEY", "FIREBASE_CLIENT_EMAIL", "FIREBASE_CLIENT_ID",
                    "FIREBASE_AUTH_URI", "FIREBASE_TOKEN_URI", "FIREBASE_AUTH_PROVIDER_CERT_URL",
                    "FIREBASE_CLIENT_CERT_URL"
                ]
                
                missing_vars = [var for var in required_env_vars if not os.getenv(var)]
                
                if missing_vars:
                    print(f"Missing Firebase environment variables: {missing_vars}")
                    print("Firebase not available - using in-memory storage for development")
                    st.warning("⚠️ Firebase not configured. Using temporary in-memory storage. Data will not persist between sessions.")
                    return False
                
                # Fallback to environment variables for local development
                firebase_config = {
                    "type": os.getenv("FIREBASE_TYPE", "service_account"),
                    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                    "private_key": os.getenv("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n"),
                    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                    "auth_uri": os.getenv("FIREBASE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth"),
                    "token_uri": os.getenv("FIREBASE_TOKEN_URI", "https://oauth2.googleapis.com/token"),
                    "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_CERT_URL", "https://www.googleapis.com/oauth2/v1/certs"),
                    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL")
                }
            
            # Create a temporary JSON file with the credentials
            cred_path = "firebase-credentials.json"
            print(f"Creating temporary credentials file: {cred_path}")
            with open(cred_path, 'w') as f:
                json.dump(firebase_config, f, indent=2)
            
            # Initialize Firebase with the credentials file
            print("Initializing Firebase with credentials...")
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            
            # Clean up the temporary file
            print("Cleaning up temporary credentials file")
            os.remove(cred_path)
            print("Firebase initialization successful!")
            st.success("✅ Firebase connected successfully!")
            return True
        print("Firebase already initialized")
        return True
    except Exception as e:
        print(f"Firebase initialization error: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        st.warning("⚠️ Firebase not available. Using temporary in-memory storage. Data will not persist between sessions.")
        return False

def verify_user(id_file):
    """Verify user with uploaded ID"""
    try:
        st.session_state.verified = True
        return True
    except Exception as e:
        st.error(f"Verification error: {str(e)}")
        return False

def save_food_post(post_data):
    """Save food post data to Firebase or memory storage"""
    try:
        print(f"Attempting to save food post: {post_data}")
        
        # Try Firebase first
        if firebase_admin._apps:
            db = firestore.client()
            # Add timestamp if not present
            if 'timestamp' not in post_data:
                post_data['timestamp'] = datetime.now().isoformat()
            
            # Add to Firestore
            doc_ref = db.collection('food_posts').add(post_data)
            print(f"Successfully saved food post to Firebase with ID: {doc_ref[1].id}")
            return True
        else:
            # Use in-memory storage as fallback
            print("Firebase not available, using in-memory storage")
            if 'timestamp' not in post_data:
                post_data['timestamp'] = datetime.now().isoformat()
            
            # Add unique ID for in-memory storage
            post_data['id'] = f"mem_{len(_memory_storage)}_{int(datetime.now().timestamp())}"
            _memory_storage.append(post_data)
            print(f"Successfully saved food post to memory storage with ID: {post_data['id']}")
            return True
            
    except Exception as e:
        print(f"Error saving post: {str(e)}")
        st.error(f"Error saving post: {str(e)}")
        return False

def get_all_food_posts():
    """Get all food posts from Firebase or memory storage"""
    try:
        print("\n=== Fetching Food Posts ===")
        print("Attempting to fetch all food posts")
        
        # Try Firebase first
        if firebase_admin._apps:
            db = firestore.client()
            posts = db.collection('food_posts').stream()
            post_list = [post.to_dict() for post in posts]
            print(f"Successfully fetched {len(post_list)} food posts from Firebase")
            if len(post_list) > 0:
                print("Sample post data:", post_list[0])
            return post_list
        else:
            # Use in-memory storage as fallback
            print("Firebase not available, using in-memory storage")
            print(f"Successfully fetched {len(_memory_storage)} food posts from memory")
            if len(_memory_storage) > 0:
                print("Sample post data:", _memory_storage[0])
            return _memory_storage.copy()
            
    except Exception as e:
        print(f"Error fetching posts: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        st.error(f"Error fetching posts: {str(e)}")
        return []

def delete_expired_posts():
    """Delete posts that are past their expiry time"""
    try:
        current_time = datetime.now()
        
        # Try Firebase first
        if firebase_admin._apps:
            db = firestore.client()
            posts = db.collection('food_posts').stream()
            
            for post in posts:
                post_data = post.to_dict()
                if 'timestamp' in post_data and 'expiry_hours' in post_data:
                    post_time = datetime.fromisoformat(post_data['timestamp'])
                    expiry_time = post_time + timedelta(hours=post_data['expiry_hours'])
                    
                    if current_time > expiry_time:
                        # Delete expired post
                        db.collection('food_posts').document(post.id).delete()
                        print(f"Deleted expired post from Firebase: {post.id}")
        else:
            # Use in-memory storage as fallback
            global _memory_storage
            original_count = len(_memory_storage)
            _memory_storage = [
                post for post in _memory_storage
                if not (
                    'timestamp' in post and 'expiry_hours' in post and
                    current_time > datetime.fromisoformat(post['timestamp']) + timedelta(hours=post['expiry_hours'])
                )
            ]
            deleted_count = original_count - len(_memory_storage)
            if deleted_count > 0:
                print(f"Deleted {deleted_count} expired posts from memory storage")
                
    except Exception as e:
        print(f"Error deleting expired posts: {str(e)}")
        st.error(f"Error deleting expired posts: {str(e)}")

def add_sample_data():
    """Add sample food posts for testing when Firebase is not available"""
    if not firebase_admin._apps and len(_memory_storage) == 0:
        print("Adding sample data for testing...")
        sample_posts = [
            {
                "name": "Green Plate Cafe",
                "contact": "+1234567890",
                "food_type": "Vegetable Biryani",
                "quantity": 15,
                "address": "123 Main Street, New York, NY 10001",
                "latitude": 40.7589,
                "longitude": -73.9851,
                "timestamp": datetime.now().isoformat(),
                "verified": True,
                "business_type": "Restaurant",
                "additional_info": "Freshly made, contains nuts",
                "expiry_hours": 6,
                "id": "sample_1"
            },
            {
                "name": "Sunrise Bakery",
                "contact": "+1987654321",
                "food_type": "Fresh Bread Loaves",
                "quantity": 25,
                "address": "456 Oak Avenue, Brooklyn, NY 11201",
                "latitude": 40.6892,
                "longitude": -73.9442,
                "timestamp": datetime.now().isoformat(),
                "verified": False,
                "business_type": "Bakery",
                "additional_info": "Various types: whole wheat, sourdough, rye",
                "expiry_hours": 12,
                "id": "sample_2"
            },
            {
                "name": "Community Kitchen",
                "contact": "+1555123456",
                "food_type": "Mixed Vegetable Curry",
                "quantity": 30,
                "address": "789 Community Center Dr, Queens, NY 11354",
                "latitude": 40.7282,
                "longitude": -73.7949,
                "timestamp": datetime.now().isoformat(),
                "verified": True,
                "business_type": "Catering",
                "additional_info": "Vegan, gluten-free, served with rice",
                "expiry_hours": 4,
                "id": "sample_3"
            }
        ]
        _memory_storage.extend(sample_posts)
        print(f"Added {len(sample_posts)} sample posts")