import ujson


def get_token():
    f = open('token.json')
    tmp = ujson.load(f)
    f.close()

    return tmp["token"]


def get_answers():
    f = open('answers.json')
    tmp = ujson.load(f)
    f.close()

    return tmp
