import json
import time
from datetime import datetime

from FastApi.common.base_api import req_exec
from FastApi.common.common import Common
from FastApi.common.helper import get_value_from_resp, utc_to_bjs, utc_to_gmt
from FastApi.conf import env


class ProjectMgt(Common):
    """
    项目管理
    """

    def __init__(self):
        super().__init__()

    def query_project(self, type='filter', userName=''):
        """
        查询当前用户名下项目
        :param type: filter:参与的项目
                     archive:已完结项目
                     disable:已终止项目
        :param userName: 不传默认为PM角色
        :return:
        """
        method = 'GET'
        url = '/api/task/case/task/user/projects?currentPage={0}&perPage={1}&type={2}'.format(self.currentPage,
                                                                                              self.perPage,
                                                                                              type)

        # 默认查询PM名下项目信息
        if not userName:
            userName = env.USERNAME_PM
        resp = req_exec(method, url, username=userName)
        return resp

    @staticmethod
    def create_project(projectName, startTime='', endTime='', templateName='基本模板', description='', valid=True,
                       userName=''):
        """
        创建项目
        :param projectName: 项目名称
        :param startTime: 项目开始时间，不传默认为当天
        :param endTime: 项目结束时间，不传默认为当天
        :param templateName: 模板名称，暂为固定模板，无需入参
        :param description: 项目描述
        :param valid:
        :param userName: 不传默认为PM角色
        :return:
        """
        # 获取当天日期
        if not startTime:
            startTime = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        if not endTime:
            endTime = time.strftime('%Y-%m-%d', time.localtime(time.time()))

        # 模板id
        if not templateName or templateName == '基本模板':
            tempId = 'ST-72f987fe9f8646618c9ca66fc63c3135'
        else:
            tempId = 'ST-72f987fe9f8646618c9ca66fc63c3135'

        # 项目信息
        applyUserDescription = {
            "valid": valid,
            "projectName": projectName,
            "tempId": tempId,
            "description": description,
            "endTime": endTime,
            "startTime": startTime
        }

        method = 'POST'
        data = {
            'applyStatus': '0',
            'applyType': '4',
            'applyUserDescription': json.dumps(applyUserDescription)
        }
        url = '/api/task/case/task/projects/apply'

        # 默认为PM创建项目
        if not userName:
            userName = env.USERNAME_PM
        resp = req_exec(method, url, data=data, username=userName)
        return resp

    def modify_project(self, projectName, userName='', **modifyParams):
        """
        修改项目
        :param projectName: 项目名称
        :param userName: 不传默认为PM角色
        :param newProjectName: 新项目名称
        :param description: 描述
        :param startTime: 格式：%Y-%m-%d
        :param endTime: 格式：%Y-%m-%d
        :return:
        """
        resp = self.query_project_info_by_name(projectName)
        if resp:
            # 获取项目ID
            projectId = resp['projectId']

            # 原项目信息获取
            modifyBody = resp
            del modifyBody['creatorName']
            del modifyBody['logo']
            if not modifyBody['disabled']:
                modifyBody['disabled'] = '0'
            modifyBody['sprintIndex'] = str(modifyBody['sprintIndex'])
            modifyBody['archive'] = str(modifyBody['archive'])
            # UTC格式时间转GMT格式
            modifyBody['startTime'] = utc_to_gmt(utc_to_bjs(modifyBody['startTime'].split('+')[0]))
            modifyBody['endTime'] = utc_to_gmt(utc_to_bjs(modifyBody['endTime'].split('+')[0]))

            for modifyParamsKey in modifyParams.keys():
                if modifyParamsKey == 'newProjectName':
                    modifyBody['projectName'] = modifyParams[modifyParamsKey]
                if modifyParamsKey == 'description':
                    modifyBody['description'] = modifyParams[modifyParamsKey]
                if modifyParamsKey == 'startTime':
                    modifyBody['startTime'] = utc_to_gmt(modifyParams[modifyParamsKey], utc_fmt='%Y-%m-%d')
                if modifyParamsKey == 'endTime':
                    modifyBody['endTime'] = utc_to_gmt(modifyParams[modifyParamsKey], utc_fmt='%Y-%m-%d')
            method = 'PUT'
            data = modifyBody
            url = '/api/task/case/task/user/projects/{0}'.format(projectId)
            # 默认为PM
            if not userName:
                userName = env.USERNAME_PM
            resp = req_exec(method, url, data=data, username=userName)
        return resp

    def operate_project(self, projectName, applyUserDescription='', applyType='2', type='filter', userName=''):
        """
        操作项目
        :param projectName: 项目名称
        :param applyUserDescription: 申请描述
        :param applyType: 操作类型： '2'：申请审核
                                   '3'：申请恢复
        :param type: filter:参与的项目
                     archive:已完结项目
                     disable:已终止项目
        :param userName: 不传默认为PM角色
        :return:
        """
        if applyType == '3':
            type = 'disable'
        projectId = self.query_project_id_by_name(projectName, type=type)
        method = 'POST'
        data = {
            'applyStatus': '0',
            'applyUserDescription': '',
            'applyType': applyType,
            'projectId': projectId
        }
        url = '/api/task/case/task/projects/apply'
        # 默认为PM
        if not userName:
            userName = env.USERNAME_PM
        resp = req_exec(method, url, data=data, username=userName)
        return resp

    def disable_or_archive_project(self, projectName, operationType='', type='filter', userName=''):
        """
        终止项目
        :param projectName: 项目名称
        :param operationType: 操作类型：disable:终止项目
                                      archive:完结项目
        :param type: filter:参与的项目
                     archive:已完结项目
                     disable:已终止项目
        :param userName: 不传默认为PM角色
        :return:
        """
        projectId = self.query_project_id_by_name(projectName, type=type)
        method = 'PATCH'
        data = {}
        url = '/api/task/case/task/user/projects/{0}/{1}'.format(projectId, operationType)
        # 默认为PM
        if not userName:
            userName = env.USERNAME_PM
        resp = req_exec(method, url, data=data, username=userName)
        return resp

    def query_project_info_by_name(self, projectName, type='filter', userName=''):
        """
        根据项目名称获取项目信息
        :param projectName:
        :param type: filter:参与的项目
                     archive:已完结项目
                     disable:已终止项目
        :param userName: 不传默认为PM角色
        :return:
        """
        resp = self.query_project(type=type, userName=userName)
        for projectBody in resp['content']['data']['list']:
            if projectBody['projectName'] == projectName:
                return projectBody

    def query_project_id_by_name(self, projectName, type='filter', userName=''):
        """
        根据项目名称获取项目ID
        :param projectName:
        :param type: filter:参与的项目
                     archive:已完结项目
                     disable:已终止项目
        :param userName: 不传默认为PM角色
        :return:
        """
        resp = self.query_project(type=type, userName=userName)
        return get_value_from_resp(resp['content'], 'projectId', 'projectName', projectName)


if __name__ == '__main__':
    pass
    pm = ProjectMgt()
    # pm.query_project()
    # print(pm.query_project_id_by_name('P1'))
    # pm.create_project(projectName='P2')
    # pm.modify_project(projectName='P12', newProjectName='P1', description='55555',
    #                   startTime='2021-08-12', endTime='2021-08-31')
    # pm.operate_project(projectName='P1', applyType='3')
    # pm.disable_or_archive_project(projectName='P2', operationType='archive', type='disable')
