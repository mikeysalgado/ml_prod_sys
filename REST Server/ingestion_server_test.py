import requests


def test():
    url = 'http://localhost:8888/email'
    data = {
        'to': 'someone@somewhere.com',
        'from': 'someone_else@somewhere_else.com',
        'subject': 'some important summary',
        'body': 'Lots of Text'
    }
    x = requests.post(url, json=data)
    print(x.text)


if __name__ == "__main__":
    test()
