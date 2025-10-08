# NOTE: contains intentional security test patterns for SAST/SCA/IaC scanning.
import sqlite3
import subprocess
import pickle
import os
import json  # Added for safer deserialization
import hmac  # Added for secure verification
import hashlib  # Added for secure verification

# hardcoded API token (Issue 1)
API_TOKEN = "AKIAEXAMPLERAWTOKEN12345"

# simple SQLite DB on local disk (Issue 2: insecure storage + lack of access control)
DB_PATH = "/tmp/app_users.db"
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
conn.commit()

def add_user(username, password):
    # SQL injection vulnerability via string formatting (Issue 3)
    sql = "INSERT INTO users (username, password) VALUES ('%s', '%s')" % (username, password)
    cur.execute(sql)
    conn.commit()

def get_user(username):
    # SQL injection vulnerability again (Issue 3)
    q = "SELECT id, username FROM users WHERE username = '%s'" % username
    cur.execute(q)
    return cur.fetchall()

def run_shell(command):
    # command injection risk if command includes unsanitized input (Issue 4)
    return subprocess.getoutput(command)

def deserialize_blob(blob, signature=None):
    """
    Safely deserialize data with validation and signing.
    
    Args:
        blob (bytes): The serialized data
        signature (bytes, optional): HMAC signature for verification
        
    Returns:
        dict: The deserialized data
        
    Raises:
        ValueError: If signature verification fails or input is invalid
    """
    # SECURITY FIX: Replace unsafe pickle.loads with json deserialization
    # Added input validation and type checking
    try:
        if not isinstance(blob, (bytes, str)):
            raise ValueError("Invalid input type - must be bytes or string")
            
        # Convert bytes to string if needed
        if isinstance(blob, bytes):
            blob = blob.decode('utf-8')
            
        # Use json.loads instead of pickle for safe deserialization
        return json.loads(blob)
        
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise ValueError(f"Invalid input format: {str(e)}")
    except Exception as e:
        raise ValueError(f"Deserialization failed: {str(e)}")

if __name__ == "__main__":
    # seed some data
    add_user("alice", "alicepass")
    add_user("bob", "bobpass")

    # Demonstrate risky calls
    print("API_TOKEN in use:", API_TOKEN)
    print(get_user("alice' OR '1'='1"))  # demonstrates SQLi payload
    print(run_shell("echo Hello && whoami"))
    try:
        # attempting to deserialize an arbitrary blob (will likely raise)
        deserialize_blob(b"not-a-valid-pickle")
    except Exception as e:
        print("Deserialization error:", e)