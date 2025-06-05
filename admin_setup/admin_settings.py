import os

# Now I'm the king
# How to understand that you became an admin

def get_admin_ids():
    base = os.path.dirname(__file__)
    path = os.path.join(base, "..", "admin_id.txt")
    with open(path, "r", encoding="utf-8") as f:
        return [int(line.strip()) for line in f if line.strip()]

def is_admin(user_id: int) -> bool:
    return user_id in get_admin_ids()