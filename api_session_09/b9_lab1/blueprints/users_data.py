USERS = {
    1: {
        "first_name": "Văn",
        "last_name": "Nguyễn",
        "email": "van.nguyen@example.com",
    },
    2: {
        "first_name": "An",
        "last_name": "Trần",
        "email": "an.tran@example.com",
    },
}

def get_user(uid):
    return USERS.get(uid)

def create_user(first_name, last_name, email):
    uid = max(USERS, default=0) + 1
    USERS[uid] = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
    }
    return uid, USERS[uid]