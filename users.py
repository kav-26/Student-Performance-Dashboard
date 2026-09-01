from auth import hash_password


USERS = {
    "admin": {
        "password_hash": hash_password("Admin@12345"),
        "role": "admin"
    },

    "analyst": {
        "password_hash": hash_password("Analyst@12345"),
        "role": "analyst"
    }
}