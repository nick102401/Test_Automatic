import requests
import warnings

warnings.filterwarnings('ignore')

session = requests.session()


class ApiDriver(object):
    def __init__(self):
        pass

    def login(self):
        pass

    def logout(self):
        pass

    def get_token(self):
        pass


def get():
    resp = session.get(url="https://wstatic.apizl.com/tools/upload/201901/1146741545.png?w=50&h=50", verify=False)
    print(resp.content)
    print("===================================")
    print(resp.status_code)
    return resp.status_code


def post():
    return


def put():
    return


def delete():
    return


if __name__ == '__main__':
    driver = ApiDriver()
    get()
