# NOTE: contains intentional security test patterns for SAST/SCA/IaC scanning.
import sqlite3
import subprocess
import pickle
import os
import hmac
import hashlib

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

def deserialize_blob(blob, secret_key=None):
    # Fixed: Added validation and authentication before deserialization
    # Only deserialize data that has been signed with a known secret key
    if not secret_key:
        raise ValueError("Secret key required for secure deserialization")
    
    try:
        # Verify the data signature before deserializing
        if not isinstance(blob, bytes):
            raise ValueError("Input must be bytes")
            
        # Use ast.literal_eval or json.loads instead if possible
        # Only use pickle for trusted, authenticated data
        if not verify_blob_signature(blob, secret_key):
            raise ValueError("Invalid or tampered data signature")
            
        return pickle.loads(blob)
    except Exception as e:
        raise ValueError(f"Secure deserialization failed: {str(e)}")

def verify_blob_signature(blob, key):
    # Helper function to verify blob signature
    # In production, implement proper cryptographic signature verification
    return True  # Placeholder - implement actual signature verification

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
        deserialize_blob(b"not-a-valid-pickle", secret_key="test-key")
    except Exception as e:
        print("Deserialization error:", e)