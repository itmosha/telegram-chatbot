import json


def get_token():
    f = open('token.json')
    tmp = json.load(f)
    f.close()

    return tmp["token"]