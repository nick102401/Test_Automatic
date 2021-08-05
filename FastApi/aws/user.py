from FastApi.common.base_api import req_exec
from FastApi.common.common import Common
from FastApi.common.helper import get_value_from_resp
from FastApi.conf import env


class User(Common):
    """
    用户管理
    """

    def __init__(self):
        super(User, self).__init__()

    def get_user_info(self, username=env.USERNAME, password=env.PASSWORD):
        """
        管理员登录获取用户信息
        :param username:
        :param password:
        :return:
        """
        self.currentPage = 1
        self.perPage = 200
        method = 'GET'
        url = '/api/task/case/task/user/page?currentPage={0}&pageSize={1}'.format(self.currentPage, self.perPage)
        resp = req_exec(method, url, username=username, password=password)
        return resp

    def get_user_id(self, username=env.USERNAME_PM):
        """
        获取用户ID
        :param username: 待查询的用户名
        :return:
        """
        resp = self.get_user_info()
        return get_value_from_resp(resp['content'], 'userId', 'realName', username)


if __name__ == '__main__':
    pass
    user = User()
    # user.get_user_info()
    # print(user.get_user_id())
