def deserialize_blob(blob):
    # insecure deserialization of untrusted data (Issue 5)
    return pickle.loads(blob)

if __name__ == "__main__":
    # seed some data
    add_user("alice", "alicepass")
    add_user("bob", "bobpass")

    # Demonstrate risky calls
    # Fixed: Removed direct printing of API_TOKEN to prevent sensitive information exposure
    print("API_TOKEN status: [REDACTED]")  # Security fix: Don't expose sensitive tokens in logs
    print(get_user("alice' OR '1'='1"))  # demonstrates SQLi payload
    print(run_shell("echo Hello && whoami"))
    try:
        # attempting to deserialize an arbitrary blob (will likely raise)
        deserialize_blob(b"not-a-valid-pickle")
    except Exception as e:
        print("Deserialization error:", e)