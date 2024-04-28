import bcrypt

# this is for hashing password so it not store in plain text
def hashPassword(password):
     return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

def verifyPassword(provided_password, stored_hashed_password):
     return bcrypt.checkpw(provided_password.encode("utf-8"), stored_hashed_password)