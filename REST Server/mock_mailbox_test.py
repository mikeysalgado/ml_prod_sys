import requests


def test1():
    # Test 1
    url = 'http://localhost:5000/mailbox/email/1'
    x = requests.get(url)
    print(x.text)


def test2():
    # Test 2
    url = 'http://localhost:5000/mailbox/email/1/folder'
    x = requests.get(url)
    print(x.text)


def test3():
    # Test 3
    url = 'http://localhost:5000/mailbox/email/1/labels'
    x = requests.get(url)
    print(x.text)


def test6():
    # Test 6
    url = 'http://localhost:5000/mailbox/folder/Inbox'
    x = requests.get(url)
    print(x.text)


def test7():
    # Test 7
    url = 'http://localhost:5000/mailbox/label/spam'
    x = requests.get(url)
    print(x.text)


def test4():
    # Test 4
    url = 'http://localhost:5000/mailbox/email/1/label/read'
    x = requests.put(url)
    print(x.text)


def test8():
    # Test 8
    url = 'http://localhost:5000/mailbox/email/1/folder/Archive'
    x = requests.put(url)
    print(x.text)


def test5():
    # Test 5
    url = 'http://localhost:5000/mailbox/email/1/label/read'
    x = requests.delete(url)
    print(x.text)


if __name__ == "__main__":
    test1()
    test2()
    test3()
    test4()
    test5()
    test6()
    test7()
    test8()
