import ast
import time

from FastApi.aws.user import User
from FastApi.common.base_api import req_exec
from FastApi.aws.tempate import Temps
from FastApi.aws.homepage import PersonalHomepage
from FastApi.common.helper import get_value_from_resp, utc_to_bjs, utc_to_gmt, bjs_to_utc
from FastApi.conf import env
from FastApi.conf.config import ReadConfig


class Project(PersonalHomepage):
    """
    项目管理
    """

    def __init__(self):
        super(Project, self).__init__()

    """
    项目基本配置
    """

    @staticmethod
    def create_project(projectName, startTime='', endTime='', templateName='基本模板', description='', valid=True,
                       userName=env.USERNAME_PM):
        """
        创建项目
        :param projectName: 项目名称
        :param startTime: 项目开始日期,默认为系统当前日期 %Y-%m-%d
        :param endTime: 项目结束日期,默认为第二天 %Y-%m-%d
        :param templateName: 模板名称,暂为固定模板,无需入参
        :param description: 项目描述
        :param valid:
        :param userName: 默认为PM角色
        :return:
        """
        # 获取系统当前日期
        if not startTime:
            startTime = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        if not endTime:
            endTime = time.strftime('%Y-%m-%d', time.localtime(time.time() + 24 * 3600))

        # 获取模板id
        tempId = Temps.query_template_id_by_name(templateName=templateName)

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
        data = dict(applyStatus=0, applyType=4, applyUserDescription=applyUserDescription)
        url = '/api/task/case/task/projects/apply'

        resp = req_exec(method, url, data=data, username=userName)
        return resp

    def approve_project(self, projectName, approveDescription='', approveStatus=1, userName=env.USERNAME_PMO):
        """
        审批项目
        :param projectName: 项目名称
        :param approveDescription: 审批描述
        :param approveStatus: 审批方式：1:审批通过
                                      2:驳回
        :param userName: 默认为PMO角色
        :return:
        """
        pending_approvals = self.query_pending_approvals(userName=userName)
        if pending_approvals:
            for pending_approval in pending_approvals:
                # 获取审批事件ID
                applyUserDescription = pending_approval['applyUserDescription']
                if applyUserDescription:
                    if ast.literal_eval(applyUserDescription)['projectName'] == projectName:
                        approveId = pending_approval['approveId']
                    else:
                        raise Exception('暂无此项目申请,请核实后操作')
                else:
                    if pending_approval['projectName'] == projectName:
                        approveId = pending_approval['approveId']
                    else:
                        raise Exception('暂无此项目申请,请核实后操作')

                method = 'PATCH'
                data = {
                    'approveDescription': approveDescription,
                    'approveId': approveId,
                    'approveStatus': approveStatus
                }
                url = '/api/task/case/task/projects/{0}/approve'.format(approveId)

                resp = req_exec(method, url, data=data, username=userName)
                return resp
        else:
            raise Exception('暂无审批申请,请核实后操作')

    def modify_project(self, projectName, userName=env.USERNAME_PM, **modifyParams):
        """
        修改项目
        :param projectName: 项目名称
        :param userName: 默认为PM角色
        :param modifyParams: 待修改入参：newProjectName:待修改项目名称
                                       description:描述
                                       startTime:格式：%Y-%m-%d
                                       endTime:格式：%Y-%m-%d
        :return:
        """
        resp = self.query_project_info_by_name(projectName)
        if resp:
            # 获取项目ID
            projectId = resp['projectId']

            # 复制原项目信息
            modifyBody = resp
            del modifyBody['creatorName']
            del modifyBody['logo']
            if not modifyBody['disabled']:
                modifyBody['disabled'] = 0
            modifyBody['sprintIndex'] = str(modifyBody['sprintIndex'])
            modifyBody['archive'] = str(modifyBody['archive'])
            # UTC格式日期转GMT格式
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

            resp = req_exec(method, url, data=data, username=userName)
            return resp
        else:
            raise Exception('暂无此项目信息,请核实后操作')

    def operate_project(self, projectName, applyUserDescription='', applyType=2, filterType='filter',
                        userName=env.USERNAME_PM):
        """
        操作项目
        :param projectName: 项目名称
        :param applyUserDescription: 操作描述
        :param applyType: 操作类型： 2：申请审核
                                   3：申请恢复
        :param filterType: filter:参与的项目
                           archive:已完结项目
                           disable:已终止项目
        :param userName: 默认为PM角色
        :return:
        """
        if applyType == 3:
            filterType = 'disable'
        projectId = self.query_project_id_by_name(projectName, filterType=filterType, userName=userName)
        method = 'POST'
        data = {
            'applyStatus': 0,
            'applyUserDescription': applyUserDescription,
            'applyType': applyType,
            'projectId': projectId
        }
        url = '/api/task/case/task/projects/apply'

        resp = req_exec(method, url, data=data, username=userName)
        return resp

    def disable_or_archive_project(self, projectName, operationType='', filterType='filter', userName=env.USERNAME_PM):
        """
        终止项目
        :param projectName: 项目名称
        :param operationType: 操作类型：disable:终止项目
                                      archive:完结项目
        :param filterType: filter:参与的项目
                           archive:已完结项目
                           disable:已终止项目
        :param userName: 默认为PM角色
        :return:
        """
        projectId = self.query_project_id_by_name(projectName, filterType=filterType, userName=userName)
        method = 'PATCH'
        data = {}
        url = '/api/task/case/task/user/projects/{0}/{1}'.format(projectId, operationType)

        resp = req_exec(method, url, data=data, username=userName)
        return resp

    def query_projects(self, filterType='filter', userName=env.USERNAME_PM):
        """
        查询当前用户名下项目
        :param filterType: filter:参与的项目
                           archive:已完结项目
                           disable:已终止项目
        :param userName: 默认为PM角色
        :return:
        """
        method = 'GET'
        url = '/api/task/case/task/user/projects?currentPage={0}&perPage={1}&type={2}'.format(self.currentPage,
                                                                                              self.perPage,
                                                                                              filterType)

        resp = req_exec(method, url, username=userName)
        return resp

    def query_project_info_by_name(self, projectName, filterType='filter', userName=env.USERNAME_PM):
        """
        根据项目名称获取项目信息
        :param projectName:
        :param filterType: filter:参与的项目
                           archive:已完结项目
                           disable:已终止项目
        :param userName: 默认为PM角色
        :return:
        """
        resp = self.query_projects(filterType=filterType, userName=userName)
        projectList = resp['content']['data']['list']
        if projectList:
            for projectBody in resp['content']['data']['list']:
                if projectBody['projectName'] == projectName:
                    return projectBody
            else:
                raise Exception('暂无此项目信息,请核实后操作')
        else:
            raise Exception('暂无项目信息,请核实后操作')

    def query_project_id_by_name(self, projectName, filterType='filter', userName=env.USERNAME_PM):
        """
        根据项目名称获取项目ID
        :param projectName:
        :param filterType: filter:参与的项目
                           archive:已完结项目
                           disable:已终止项目
        :param userName: 默认为PM角色
        :return:
        """
        resp = self.query_projects(filterType=filterType, userName=userName)
        projectId = get_value_from_resp(resp['content'], 'projectId', 'projectName', projectName)
        if projectId:
            return projectId
        else:
            raise Exception('暂无此项目信息,请核实后操作')

    """
    WebHook配置
    """

    def config_web_hook(self, projectName, webUrl='', webAccessToken='', webSecret='', filterType='filter',
                        userName=env.USERNAME_PM):
        """
        配置WebHook
        :param projectName: 项目名称
        :param webUrl: url
        :param webAccessToken: access token
        :param webSecret: 加签
        :param filterType: filter:参与的项目
                           disable:已终止项目
        :param userName: 默认为PM角色
        :return:
        """
        # 获取项目ID
        projectId = self.query_project_id_by_name(projectName, filterType=filterType, userName=userName)

        method = 'PUT'
        data = {
            "projectId": projectId,
            "webUrl": webUrl,
            "webAccess": webAccessToken,
            "webSecret": webSecret,
            "triggerCreate": "0",
            "triggerUpdate": "0",
            "triggerCancel": "0",
            "triggerFinished": "0"
        }
        url = '/api/task/case/task/projects/{0}/web/hook'.format(projectId)

        resp = req_exec(method, url, data=data, username=userName)
        return resp

    def query_web_hook(self, projectName, filterType='filter', userName=env.USERNAME_PM):
        """
        查看项目WebHook配置
        :param projectName: 项目名称
        :param filterType: filter:参与的项目
                           archive:已完结项目
                           disable:已终止项目
        :param userName: 默认为PM角色
        :return:
        """
        # 获取项目ID
        projectId = self.query_project_id_by_name(projectName, filterType=filterType, userName=userName)

        method = 'GET'
        url = '/api/task/case/task/projects/{0}/web/hook'.format(projectId)

        resp = req_exec(method, url, username=userName)
        return resp

    """
    项目角色
    """

    def modify_role(self, roleName, projectName, filterType='filter', userName=env.USERNAME_PM, **modifyParams):
        """
        修改角色配置
        :param roleName: 角色名称
        :param projectName: 项目名称
        :param filterType: filter:参与的项目
                           archive:已完结项目
                           disable:已终止项目
        :param userName: 默认为PM角色
        :param modifyParams: newRoleName:待修改角色名称
                             manage:管理项目 1:是 0:否
                             createTask:创建任务 1:是 0:否
                             updateTask:修改任务 1:是 0:否
        :return:
        """

        # 获取原角色配置信息
        preRoleBody = self.query_role_info_by_name(roleName, projectName=projectName, filterType=filterType,
                                                   userName=userName)

        if preRoleBody:
            # 获取项目ID
            projectId = preRoleBody['projectId']
            # 获取角色ID
            proRoleId = preRoleBody['proRoleId']

            # 复制原配置
            modifyBody = preRoleBody

            for modifyParamsKey in modifyParams.keys():
                if modifyParamsKey == 'newRoleName':
                    modifyBody['roleName'] = modifyParams[modifyParamsKey]
                if modifyParamsKey == 'manage':
                    modifyBody['manage'] = modifyParams[modifyParamsKey]
                if modifyParamsKey == 'createTask':
                    modifyBody['createTask'] = modifyParams[modifyParamsKey]
                if modifyParamsKey == 'updateTask':
                    modifyBody['updateTask'] = modifyParams[modifyParamsKey]

            method = 'PATCH'
            data = modifyBody
            url = '/api/task/case/task/projects/{0}/roles/{1}'.format(projectId, proRoleId)

            resp = req_exec(method, url, data=data, username=userName)
            return resp
        else:
            raise Exception('无此角色信息,请核实后操作')

    def query_roles(self, projectName, filterType='filter', userName=env.USERNAME_PM):
        """
        查询角色
        :param projectName: 项目名称
        :param filterType: filter:参与的项目
                           archive:已完结项目
                           disable:已终止项目
        :param userName: 默认为PM角色
        :return:
        """
        # 获取项目ID
        projectId = self.query_project_id_by_name(projectName, filterType=filterType, userName=userName)

        method = 'GET'
        url = '/api/task/case/task/projects/{0}/roles'.format(projectId)

        resp = req_exec(method, url, username=userName)
        return resp

    def query_role_info_by_name(self, roleName, projectName, filterType='filter', userName=env.USERNAME_PM):
        """
        根据角色名称获取角色配置信息
        :param roleName: 角色名称
        :param projectName: 项目名称
        :param filterType: filter:参与的项目
                           archive:已完结项目
                           disable:已终止项目
        :param userName: 默认为PM角色
        :return:
        """
        resp = self.query_roles(projectName, filterType=filterType, userName=userName)
        roleList = resp['content']['data']['list']

        if roleList:
            for role in roleList:
                if role['roleName'] == roleName:
                    return role
                else:
                    raise Exception('无此角色信息,请核实后操作')
        else:
            raise Exception('无角色信息,请核实后操作')

    def query_role_id_by_name(self, roleName, projectName, filterType='filter', userName=env.USERNAME_PM):
        """
        根据角色名称获取角色ID
        :param roleName: 角色名称
        :param projectName: 项目名称
        :param filterType: filter:参与的项目
                           archive:已完结项目
                           disable:已终止项目
        :param userName: 默认为PM角色
        :return:
        """
        resp = self.query_roles(projectName, filterType=filterType, userName=userName)
        proRoleId = get_value_from_resp(resp['content'], 'proRoleId', 'roleName', roleName)
        if proRoleId:
            return proRoleId
        else:
            raise Exception('暂无该项目角色信息,请核实后操作')

    """
    任务状态 & BUG状态
    >>>>>接口相同--合并处理
    """

    def modify_status(self, statusName, projectName, bugFlag=0, filterType='filter', userName=env.USERNAME_PM,
                      **modifyParams):
        """
        修改角色配置
        :param statusName: 名称
        :param projectName: 项目名称
        :param bugFlag: 0:任务状态
                        1:BUG状态
        :param filterType: filter:参与的项目
                           archive:已完结项目
                           disable:已终止项目
        :param userName: 默认为PM角色
        :param modifyParams: newStatusName:待修改名称
                             statusColor:颜色
                             statusType:任务状态类型 0:是 1:否 2:否 (BUG状态默认为0)
        :return:
        """

        # 获取原状态配置信息
        preStatusBody = self.query_status_info_by_name(statusName, projectName=projectName, bugFlag=bugFlag,
                                                       filterType=filterType, userName=userName)

        if not bugFlag:
            statusStr = '任务状态'
        else:
            statusStr = 'BUG状态'

        if preStatusBody:
            # 获取项目ID
            projectId = preStatusBody['projectId']
            # 获取状态ID
            taskStatusId = preStatusBody['taskStatusId']

            # 复制原配置
            modifyBody = preStatusBody

            for modifyParamsKey in modifyParams.keys():
                if modifyParamsKey == 'newStatusName':
                    modifyBody['statusName'] = modifyParams[modifyParamsKey]
                if modifyParamsKey == 'statusColor':
                    modifyBody['statusColor'] = modifyParams[modifyParamsKey]
                if modifyParamsKey == 'statusType':
                    modifyBody['statusType'] = modifyParams[modifyParamsKey]

            method = 'PATCH'
            data = modifyBody
            if not bugFlag:
                url = '/api/task/case/task/projects/{0}/status/{1}'.format(projectId, taskStatusId)
            else:
                url = '/api/task/case/task/projects/{0}/bug/status/{1}'.format(projectId, taskStatusId)

            resp = req_exec(method, url, data=data, username=userName)
            return resp
        else:
            raise Exception('无此{0}信息,请核实后操作'.format(statusStr))

    def query_status(self, projectName, bugFlag=0, filterType='filter', userName=env.USERNAME_PM):
        """
        查询任务状态或BUG状态配置
        :param projectName: 项目名称
        :param bugFlag: 0:任务状态
                        1:BUG状态
        :param filterType: filter:参与的项目
                           archive:已完结项目
                           disable:已终止项目
        :param userName: 默认为PM角色
        :return:
        """
        # 获取项目ID
        projectId = self.query_project_id_by_name(projectName, filterType=filterType, userName=userName)

        method = 'GET'
        url = '/api/task/case/task/projects/{0}/status?bugFlag={1}'.format(projectId, bugFlag)

        resp = req_exec(method, url, username=userName)
        return resp

    def query_status_info_by_name(self, statusName, projectName, bugFlag=0, filterType='filter',
                                  userName=env.USERNAME_PM):
        """
        根据角色名称获取状态信息
        :param statusName: 名称
        :param projectName: 项目名称
        :param bugFlag: 0:任务状态
                        1:BUG状态
        :param filterType: filter:参与的项目
                           archive:已完结项目
                           disable:已终止项目
        :param userName: 默认为PM角色
        :return:
        """
        if not bugFlag:
            statusStr = '任务状态'
        else:
            statusStr = 'BUG状态'
        resp = self.query_status(projectName, bugFlag=bugFlag, filterType=filterType, userName=userName)
        statusList = resp['content']['data']['list']

        if statusList:
            for status in statusList:
                if status['statusName'] == statusName:
                    return status
                else:
                    raise Exception('无此{0}信息,请核实后操作'.format(statusStr))
        else:
            raise Exception('无{0}信息,请核实后操作'.format(statusStr))

    def query_status_id_by_name(self, statusName, projectName, bugFlag=0, filterType='filter',
                                userName=env.USERNAME_PM):
        """
        根据角色名称获取状态ID
        :param statusName: 名称
        :param projectName: 项目名称
        :param bugFlag: 0:任务状态
                        1:BUG状态
        :param filterType: filter:参与的项目
                           archive:已完结项目
                           disable:已终止项目
        :param userName: 默认为PM角色
        :return:
        """
        if not bugFlag:
            statusStr = '任务状态'
        else:
            statusStr = 'BUG状态'
        resp = self.query_status(projectName, bugFlag=bugFlag, filterType=filterType, userName=userName)
        taskStatusId = get_value_from_resp(resp['content'], 'taskStatusId', 'statusName', statusName)
        if taskStatusId:
            return taskStatusId
        else:
            raise Exception('无此{0}信息,请核实后操作'.format(statusStr))

    """
    任务类型
    """

    def modify_task_type(self, typeName, projectName, filterType='filter', userName=env.USERNAME_PM, **modifyParams):
        """
        修改角色配置
        :param typeName: 名称
        :param projectName: 项目名称
        :param filterType: filter:参与的项目
                           archive:已完结项目
                           disable:已终止项目
        :param userName: 默认为PM角色
        :param modifyParams: newTypeName:待修改名称
        :return:
        """

        # 获取原状态配置信息
        preTypeBody = self.query_task_type_info_by_name(typeName, projectName=projectName, filterType=filterType,
                                                        userName=userName)

        if preTypeBody:
            # 获取项目ID
            projectId = preTypeBody['projectId']
            # 获取任务类型ID
            taskTypeId = preTypeBody['taskTypeId']

            # 复制原配置
            modifyBody = preTypeBody

            for modifyParamsKey in modifyParams.keys():
                if modifyParamsKey == 'newTypeName':
                    modifyBody['typeName'] = modifyParams[modifyParamsKey]

            method = 'PATCH'
            data = modifyBody
            url = '/api/task/case/task/projects/{0}/types/{1}'.format(projectId, taskTypeId)

            resp = req_exec(method, url, data=data, username=userName)
            return resp
        else:
            raise Exception('无此任务类型信息,请核实后操作')

    def query_task_types(self, projectName, filterType='filter', userName=env.USERNAME_PM):
        """
        查询任务类型
        :param projectName: 项目名称
        :param filterType: filter:参与的项目
                           archive:已完结项目
                           disable:已终止项目
        :param userName: 默认为PM角色
        :return:
        """
        # 获取项目ID
        projectId = self.query_project_id_by_name(projectName, filterType=filterType, userName=userName)

        method = 'GET'
        url = '/api/task/case/task/projects/{0}/types'.format(projectId)

        resp = req_exec(method, url, username=userName)
        return resp

    def query_task_type_info_by_name(self, typeName, projectName, filterType='filter', userName=env.USERNAME_PM):
        """
        根据任务类型名称获取任务类型信息
        :param typeName: 任务类型名称
        :param projectName: 项目名称
        :param filterType: filter:参与的项目
                           archive:已完结项目
                           disable:已终止项目
        :param userName: 默认为PM角色
        :return:
        """
        resp = self.query_task_types(projectName, filterType=filterType, userName=userName)
        typeList = resp['content']['data']['list']

        if typeList:
            for typeInfo in typeList:
                if typeInfo['typeName'] == typeName:
                    return typeInfo
                else:
                    raise Exception('无此任务类型信息,请核实后操作')
        else:
            raise Exception('无任务类型信息,请核实后操作')

    def query_task_type_id_by_name(self, typeName, projectName, filterType='filter', userName=env.USERNAME_PM):
        """
        根据任务类型名称获取任务类型信息
        :param typeName: 任务类型名称
        :param projectName: 项目名称
        :param filterType: filter:参与的项目
                           archive:已完结项目
                           disable:已终止项目
        :param userName: 默认为PM角色
        :return:
        """
        resp = self.query_task_types(projectName, filterType=filterType, userName=userName)
        taskTypeId = get_value_from_resp(resp['content'], 'taskTypeId', 'typeName', typeName)
        if taskTypeId:
            return taskTypeId
        else:
            raise Exception('无此任务类型信息,请核实后操作')

    """
    任务优先级
    """

    def modify_task_priority(self, priorityName, projectName, filterType='filter', userName=env.USERNAME_PM,
                             **modifyParams):
        """
        修改角色配置
        :param priorityName: 任务优先级名称
        :param projectName: 项目名称
        :param filterType: filter:参与的项目
                           archive:已完结项目
                           disable:已终止项目
        :param userName: 默认为PM角色
        :param modifyParams: newPriorityName:待修改名称
                             priorityColor:优先级颜色
                             defaultMark:是否默认 1:默认 0:不默认
        :return:
        """

        # 获取原状态配置信息
        prePriorityBody = self.query_task_priority_info_by_name(priorityName, projectName=projectName,
                                                                filterType=filterType, userName=userName)

        if prePriorityBody:
            # 获取项目ID
            projectId = prePriorityBody['projectId']
            # 获取任务优先级ID
            taskPriorityId = prePriorityBody['taskPriorityId']

            # 复制原配置
            modifyBody = prePriorityBody

            for modifyParamsKey in modifyParams.keys():
                if modifyParamsKey == 'newPriorityName':
                    modifyBody['priorityName'] = modifyParams[modifyParamsKey]
                if modifyParamsKey == 'priorityColor':
                    modifyBody['priorityColor'] = modifyParams[modifyParamsKey]
                if modifyParamsKey == 'defaultMark':
                    modifyBody['defaultMark'] = modifyParams[modifyParamsKey]

            method = 'PATCH'
            data = modifyBody
            url = '/api/task/case/task/projects/{0}/priorities/{1}'.format(projectId, taskPriorityId)

            resp = req_exec(method, url, data=data, username=userName)
            return resp
        else:
            raise Exception('无此任务优先级信息,请核实后操作')

    def query_task_priorities(self, projectName, filterType='filter', userName=env.USERNAME_PM):
        """
        查询任务优先级
        :param projectName: 项目名称
        :param filterType: filter:参与的项目
                           archive:已完结项目
                           disable:已终止项目
        :param userName: 默认为PM角色
        :return:
        """
        # 获取项目ID
        projectId = self.query_project_id_by_name(projectName, filterType=filterType, userName=userName)

        method = 'GET'
        url = '/api/task/case/task/projects/{0}/priorities'.format(projectId)

        resp = req_exec(method, url, username=userName)
        return resp

    def query_task_priority_info_by_name(self, priorityName, projectName, filterType='filter',
                                         userName=env.USERNAME_PM):
        """
        根据任务优先级名称获取任务优先级信息
        :param priorityName: 任务优先级名称
        :param projectName: 项目名称
        :param filterType: filter:参与的项目
                           archive:已完结项目
                           disable:已终止项目
        :param userName: 默认为PM角色
        :return:
        """
        resp = self.query_task_priorities(projectName, filterType=filterType, userName=userName)
        priorityList = resp['content']['data']['list']

        if priorityList:
            for priority in priorityList:
                if priority['priorityName'] == priorityName:
                    return priority
                else:
                    raise Exception('无此任务优先级信息,请核实后操作')
        else:
            raise Exception('无任务优先级信息,请核实后操作')

    def query_task_priority_id_by_name(self, priorityName, projectName, filterType='filter', userName=env.USERNAME_PM):
        """
        根据任务优先级名称获取任务优先级信息
        :param priorityName: 任务优先级名称
        :param projectName: 项目名称
        :param filterType: filter:参与的项目
                           archive:已完结项目
                           disable:已终止项目
        :param userName: 默认为PM角色
        :return:
        """
        resp = self.query_task_priorities(projectName, filterType=filterType, userName=userName)
        taskPriorityId = get_value_from_resp(resp['content'], 'taskPriorityId', 'priorityName', priorityName)
        if taskPriorityId:
            return taskPriorityId
        else:
            raise Exception('无此任务优先级信息,请核实后操作')


class Task(Project):
    """
    项目任务
    """

    def __init__(self, projectName, userName=env.USERNAME_PM):
        super(Task, self).__init__()
        self.user = User()
        self.projectId = self.query_project_id_by_name(projectName, userName=userName)

    def query_index_data(self, userName=env.USERNAME_PM):
        """
        任务首页
        :param userName:
        :return:
        """
        method = 'GET'
        url = '/api/task/case/task/projects/{0}/index/data'.format(self.projectId)

        resp = req_exec(method, url, username=userName)
        return resp

    def create_task(self, taskName, broTaskName='', description='', deadLine='', taskGetDateLine='', points=1,
                    countedPoints=1, priceFlag=False, planId='', userName=env.USERNAME_PM):
        """
        创建任务或子任务、关联任务
        :param taskName: 任务名称
        :param broTaskName: 被关联任务名称
        :param description: 任务描述
        :param deadLine: 截至日期
        :param taskGetDateLine: 任务有效期
        :param points: 任务点数
        :param countedPoints: 有效点数
        :param priceFlag: 是否悬赏: True:悬赏
                                  False:不悬赏
        :param planId: 计划ID
        :param userName: 默认为PM角色
        :return:
        """
        # 获取被关联任务ID
        if broTaskName:
            # 获取关联任务ID
            broTaskId = self.query_task_id_by_name(broTaskName, userName=userName)
        else:
            broTaskId = ''

        # 获取系统当前日期
        if not deadLine:
            deadLine = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        if not taskGetDateLine:
            taskGetDateLine = time.strftime('%Y-%m-%d', time.localtime(time.time()))

        # 是否悬赏任务
        if priceFlag:
            priceFlag = 1
        else:
            priceFlag = 0

        method = 'POST'
        data = {
            'title': taskName,
            'description': description,
            'typeId': 'PT-bb4147499d094736b55555b09f6f574c',  # 类型ID：开发任务
            'points': points,
            'deadLine': deadLine,
            'statusId': 'PS-160fd53c509240528393a5d62e903799',  # 状态ID：未开发
            'taskGetDateLine': taskGetDateLine,
            'priorityId': 'PP-caa66cec286948159cb1fa4404d751e4',  # 优先级ID：普通
            'broTaskId': broTaskId,
            'countedPoints': countedPoints,
            'priceFlag': priceFlag,
            'bugStatusId': 'PS-b30fda4e981b4b5b94f26b520bfd9ac4'  # BUG状态ID：轻微
        }

        # 计划ID
        if planId:
            data['planId'] = planId
        url = '/api/task/case/task/projects/{0}/tasks'.format(self.projectId)

        resp = req_exec(method, url, data=data, username=userName)
        return resp

    def copy_task(self, taskName, userName=env.USERNAME_PM):
        """
        复制任务
        :param taskName: 任务名称
        :param userName: 默认为PM角色
        :return:
        """
        # 获取任务ID
        taskId = self.query_task_id_by_name(taskName, userName=userName)
        method = 'PUT'
        data = {}
        url = '/api/task/case/task/projects/{0}/tasks/{1}/copy'.format(self.projectId, taskId)

        resp = req_exec(method, url, data=data, username=userName)
        return resp

    def modify_task(self, taskName, userName=env.USERNAME_PM, **modifyParams):
        """
        修改任务
        :param taskName: 任务名称
        :param userName: 默认为PM角色
        :param modifyParams: 待修改入参：newTaskName: 待修改任务名称
                                       description: 任务描述
                                       points: 任务点数
                                       countedPoints: 有效点数
                                       deadLine: 格式：%Y-%m-%d
                                       taskGetDateLine: 格式：%Y-%m-%d
        :return:
        """
        resp = self.query_task_info_by_name(taskName)
        if resp:
            # 获取任务ID
            taskId = resp['taskId']

            # 复制原任务信息
            modifyBody = resp
            del modifyBody['parTaskId']
            del modifyBody['projectName']
            del modifyBody['executorId']
            del modifyBody['startedAt']
            del modifyBody['finishedAt']
            del modifyBody['updatedAt']
            del modifyBody['planId']
            del modifyBody['dealId']

            modifyBody['points'] = int(modifyBody['points'])
            modifyBody['countedPoints'] = int(modifyBody['countedPoints'])
            modifyBody['archive'] = str(modifyBody['archive'])

            # 生成创建日期参数
            modifyBody['createdAt'] = bjs_to_utc(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

            for modifyParamsKey in modifyParams.keys():
                if modifyParamsKey == 'newTaskName':
                    modifyBody['title'] = modifyParams[modifyParamsKey]
                if modifyParamsKey == 'description':
                    modifyBody['description'] = modifyParams[modifyParamsKey]
                if modifyParamsKey == 'points':
                    modifyBody['points'] = modifyParams[modifyParamsKey]
                if modifyParamsKey == 'countedPoints':
                    modifyBody['countedPoints'] = modifyParams[modifyParamsKey]
                if modifyParamsKey == 'deadLine':
                    modifyBody['deadLine'] = modifyParams[modifyParamsKey]
                if modifyParamsKey == 'taskGetDateLine':
                    modifyBody['taskGetDateLine'] = modifyParams[modifyParamsKey]
            method = 'PUT'
            data = modifyBody
            url = '/api/task/case/task/projects/{0}/tasks/{1}'.format(self.projectId, taskId)

            resp = req_exec(method, url, data=data, username=userName)
            return resp
        else:
            raise Exception('暂无此任务,请核实后操作')

    def archive_task(self, taskName, userName=env.USERNAME_PM):
        """
        任务完结
        :param taskName: 任务名称
        :param userName: 默认为PM角色
        :return:
        """
        # 获取任务ID
        taskId = self.query_task_id_by_name(taskName, userName=userName)
        method = 'PUT'
        data = {}
        url = '/api/task/case/task/projects/{0}/tasks/{1}/archive'.format(self.projectId, taskId)

        resp = req_exec(method, url, data=data, username=userName)
        return resp

    def archive_task_and_copy(self, taskName, score=0, attr=0, remark='', copy=True, userName=env.USERNAME_PM):
        """
        任务完结并复制
        :param taskName: 任务名称
        :param copy: 是否复制,默认复制
        :param score: 任务分数
        :param attr: 态度分数
        :param remark: 评分备注
        :param userName: 默认为PM角色
        :return:
        """
        # 获取任务ID
        taskId = self.query_task_id_by_name(taskName, userName=userName)

        # 是否复制
        if copy:
            copy = 1
        else:
            copy = 0

        method = 'PUT'
        data = {
            'copy': copy,
            'score': score,
            'attr': attr,
            'remark': remark
        }
        url = '/api/task/case/task/projects/{0}/tasks/{1}/archive'.format(self.projectId, taskId)

        resp = req_exec(method, url, data=data, username=userName)
        return resp

    def delete_task(self, taskName, userName=env.USERNAME_PM):
        """
        删除任务
        :param taskName: 任务名称
        :param userName: 默认为PM角色
        :return:
        """
        # 获取任务ID
        taskId = self.query_task_id_by_name(taskName, userName=userName)
        method = 'DELETE'
        data = {}
        url = '/api/task/case/task/projects/{0}/tasks/{1}'.format(self.projectId, taskId)

        resp = req_exec(method, url, data=data, username=userName)
        return resp

    def reply_task(self, taskName, content='', userName=env.USERNAME_PM):
        """
        评论任务
        :param taskName: 任务名称
        :param content: 评论
        :param userName: 默认为PM角色
        :return:
        """
        # 获取任务ID
        taskId = self.query_task_id_by_name(taskName, userName=userName)
        method = 'POST'
        data = {
            'content': content
        }
        url = '/api/task/case/task/projects/{0}/tasks/{1}/replies'.format(self.projectId, taskId)

        resp = req_exec(method, url, data=data, username=userName)
        return resp

    def delete_replies_by_content(self, taskName, content, userName=env.USERNAME_PM):
        """
        根据评论内容删除评论
        :param taskName: 任务名称
        :param content: 评论内容
        :param userName: 默认为PM角色
        :return:
        """
        # 获取任务ID
        taskId = self.query_task_id_by_name(taskName, userName=userName)

        # 获取评论ID
        replyId = self.query_replies_id_by_content(taskName, content=content, userName=userName)

        method = 'DELETE'
        data = {}
        url = '/api/task/case/task/projects/{0}/tasks/{1}/reply/{2}'.format(self.projectId, taskId, replyId)

        resp = req_exec(method, url, data=data, username=userName)
        return resp

    def delete_replies_by_user(self, taskName, contentUser, userName=env.USERNAME_PM):
        """
        根据评论用户删除评论
        :param taskName: 任务名称
        :param contentUser: 评论用户
        :param userName: 默认为PM角色
        :return:
        """
        # 获取任务ID
        taskId = self.query_task_id_by_name(taskName, userName=userName)

        # 获取评论ID
        replyIdList = self.query_replies_id_by_user(taskName, contentUser=contentUser, userName=userName)

        if replyIdList:
            for replyId in replyIdList:
                method = 'DELETE'
                data = {}
                url = '/api/task/case/task/projects/{0}/tasks/{1}/reply/{2}'.format(self.projectId, taskId, replyId)

                resp = req_exec(method, url, data=data, username=userName)
                if resp['content']['msg'] != 'success' or resp['content']['data'] != '删除成功':
                    return resp
        else:
            raise Exception('暂无此用户评论,请核实后操作')

    def get_task(self, taskName, userName=env.USERNAME_PG):
        """
        领取任务
        :param taskName: 任务名称
        :param userName: 默认为职能角色
        :return:
        """
        # 获取任务ID
        taskId = self.query_task_id_by_name(taskName, userName=userName)
        method = 'PUT'
        data = {}
        url = '/api/task/case/task/projects/{0}/tasks/{1}/task'.format(self.projectId, taskId)

        resp = req_exec(method, url, data=data, username=userName)
        return resp

    def give_red_flower(self, taskName, archive=1, userName=env.USERNAME_PG):
        """
        赠送小红花
        :param taskName: 任务名称
        :param archive: 是否完成: 1:完成
                                0:未完成
        :param userName: 默认为职能角色
        :return:
        """
        # 获取任务ID
        taskId = self.query_task_id_by_name(taskName, archive=archive, userName=userName)
        # 获取用户ID
        userId = self.user.get_user_id(username=userName)
        method = 'POST'
        data = {
            'score': '',
            'remark': '',
            'dealType': '1'
        }
        url = '/api/task/case/task/projects/{0}/tasks/{1}/user/{2}/deal'.format(self.projectId, taskId, userId)

        resp = req_exec(method, url, data=data, username=userName)
        return resp

    def query_tasks(self, archive=None, assign=None, executor='', planId='', userName=env.USERNAME_PM):
        """
        查询任务
        :param archive: 是否完成: 1:完成
                                0:未完成
        :param assign: 是否分配: 1:已分配
                                0:未分配
        :param executor: 执行人
        :param planId: 计划ID
        :param userName: 默认为PM角色
        :return:
        """
        method = 'GET'
        url = '/api/task/case/task/projects/{0}/tasks?'.format(self.projectId)
        if archive is not None:
            assign = 1
            url += 'archive=' + str(archive) + '&'
        if executor:
            assign = 1
            executorId = self.user.get_user_id(username=executor)
            url += 'executorId=' + executorId + '&'
        if assign is not None:
            url += 'assign=' + str(assign) + '&'

        # 计划ID
        if planId:
            url += 'planId=' + planId + '&limitFlag=0&'

        url += 'page={0}&perPage={1}'.format(self.currentPage, self.perPage)

        resp = req_exec(method, url, username=userName)
        return resp

    def query_task_info_by_name(self, taskName, userName=env.USERNAME_PM):
        """
        根据任务名称获取任务信息
        :param taskName: 任务名称
        :param userName: 默认为PM角色
        :return:
        """
        # 获取任务ID
        taskId = self.query_task_id_by_name(taskName, userName=userName)
        method = 'GET'
        url = '/api/task/case/task/projects/{0}/tasks/{1}'.format(self.projectId, taskId)

        resp = req_exec(method, url, username=userName)
        return resp['content']['data']['item']

    def query_task_id_by_name(self, taskName, archive=None, assign=None, executor='', userName=env.USERNAME_PM):
        """
        根据任务名称获取任务ID
        :param taskName: 任务名称
        :param archive: 是否完成: 1:完成
                                0:未完成
        :param assign: 是否分配: 1:已分配
                                0:未分配
        :param executor: 执行人
        :param userName: 默认为PM角色
        :return:
        """
        resp = self.query_tasks(archive=archive, assign=assign, executor=executor, userName=userName)
        taskId = get_value_from_resp(resp['content'], 'taskId', 'title', taskName)
        if taskId:
            return taskId
        else:
            raise Exception('暂无此任务,请核实后操作')

    def query_task_replies(self, taskName, userName=env.USERNAME_PM):
        """
        获取任务评论
        :param taskName: 任务名称
        :param userName: 默认为PM角色
        :return:
        """
        # 获取任务ID
        taskId = self.query_task_id_by_name(taskName, userName=userName)
        method = 'GET'
        url = '/api/task/case/task/projects/{0}/tasks/{1}/replies'.format(self.projectId, taskId)

        resp = req_exec(method, url, username=userName)
        return resp

    def query_replies_id_by_content(self, taskName, content, userName=env.USERNAME_PM):
        """
        根据评论内容获取ID
        :param taskName: 任务名称
        :param content: 评论内容
        :param userName: 默认为PM角色
        :return:
        """
        resp = self.query_task_replies(taskName, userName=userName)
        replyList = resp['content']['data']['list']

        if replyList:
            for reply in replyList:
                if reply['content'] == content:
                    return reply['replyId']
                else:
                    raise Exception('暂无此评论,请核实后操作')
        else:
            raise Exception('该任务暂无评论')

    def query_replies_id_by_user(self, taskName, contentUser, userName=env.USERNAME_PM):
        """
        根据评论用户获取ID
        :param taskName: 任务名称
        :param contentUser: 评论用户
        :param userName: 默认为PM角色
        :return:
        """
        resp = self.query_task_replies(taskName, userName=userName)
        replyList = resp['content']['data']['list']

        # 获取用户ID
        userId = self.user.get_user_id(username=contentUser)

        replyIdList = []
        if replyList:
            for reply in replyList:
                if reply['oratorId'] == userId:
                    replyIdList.append(reply['replyId'])
        else:
            raise Exception('该任务暂无评论')
        return replyIdList


class Plan(Project):
    """
    项目计划
    """

    def __init__(self, projectName, userName=env.USERNAME_PM):
        super(Plan, self).__init__()
        self.task = Task(projectName)
        self.projectId = self.query_project_id_by_name(projectName, userName=userName)

    def create_plan(self, planName, description='', startTime='', endTime='', userName=env.USERNAME_PM):
        """
        创建计划
        :param planName: 计划名称
        :param description: 计划描述
        :param startTime: 计划开始日期:默认为系统当前日期 %Y-%m-%d
        :param endTime: 计划结束日期:默认为第二天 %Y-%m-%d
        :param userName: 默认为PM角色
        :return:
        """
        # 获取系统当前日期
        if not startTime:
            startTime = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        if not endTime:
            endTime = time.strftime('%Y-%m-%d', time.localtime(time.time() + 24 * 3600))

        method = 'POST'
        data = {
            'name': planName,
            'desc': description,
            'startTime': startTime,
            'endTime': endTime
        }
        url = '/api/task/case/task/projects/{0}/plans'.format(self.projectId)

        resp = req_exec(method, url, data=data, username=userName)
        return resp

    def create_task_for_plan(self, taskName, broTaskName='', description='', deadLine='', taskGetDateLine='', points=1,
                             countedPoints=1, priceFlag=False, planName='', userName=env.USERNAME_PM):
        """
        创建计划任务
        :param taskName: 任务名称
        :param broTaskName: 被关联任务名称
        :param description: 任务描述
        :param deadLine: 截至日期
        :param taskGetDateLine: 任务有效期
        :param points: 任务点数
        :param countedPoints: 有效点数
        :param priceFlag: 是否悬赏: True:悬赏
                                  False:不悬赏
        :param planName: 计划名称
        :param userName: 默认为PM角色
        :return:
        """
        planId = self.query_plan_id_by_name(planName)
        resp = self.task.create_task(taskName, broTaskName=broTaskName, description=description, deadLine=deadLine,
                                     taskGetDateLine=taskGetDateLine, points=points, countedPoints=countedPoints,
                                     priceFlag=priceFlag, planId=planId, userName=userName)
        return resp

    def query_plans(self, status=None, userName=env.USERNAME_PM):
        """
        查询当前项目计划
        :param status: 完成状态
        :param userName: 默认为PM角色
        :return:
        """
        method = 'GET'
        url = '/api/task/case/task/projects/{0}/plans?currentPage={1}&perPage={2}'.format(self.projectId,
                                                                                          self.currentPage,
                                                                                          self.perPage)
        # 计划完成状态
        if status == 2:
            url += '&status=2'

        resp = req_exec(method, url, username=userName)
        return resp

    def query_plan_info_by_name(self, planName, userName=env.USERNAME_PM):
        """
        根据计划名称获取计划信息
        :param planName: 计划名称
        :param userName: 默认为PM角色
        :return:
        """
        # 获取计划ID
        planId = self.query_plan_id_by_name(planName, userName=userName)
        method = 'GET'
        url = '/api/task/case/task/projects/{0}/plans/{1}'.format(self.projectId, planId)

        resp = req_exec(method, url, username=userName)
        return resp['content']['data']['item']

    def query_plan_id_by_name(self, planName, userName=env.USERNAME_PM):
        """
        根据计划名称获取计划ID
        :param planName: 计划名称
        :param userName: 默认为PM角色
        :return:
        """
        resp = self.query_plans(userName=userName)
        planId = get_value_from_resp(resp['content'], 'planId', 'name', planName)
        if planId:
            return planId
        else:
            raise Exception('暂无此计划,请核实后操作')

    def query_tasks_by_plan(self, planName, userName=env.USERNAME_PM):
        """
        查询当前计划任务
        :param planName: 计划名称
        :param userName: 默认为PM角色
        :return:
        """
        # 获取计划ID
        planId = self.query_plan_id_by_name(planName, userName=userName)
        resp = self.task.query_tasks(planId=planId)
        return resp


class ComprehensiveEvaluation(Project):
    """
    综合评价
    """

    def __init__(self, projectName, userName=env.USERNAME_PM):
        super(ComprehensiveEvaluation, self).__init__()
        self.user = User()
        self.projectId = self.query_project_id_by_name(projectName, userName=userName)

    def query_manage_report(self, userName=env.USERNAME_PM):
        """
        查看项目报告
        :param userName: 默认为PM角色
        :return:
        """
        method = 'GET'
        url = '/api/task/case/task/manageReport/projectUserScoreReport?projectId={0}'.format(self.projectId)

        resp = req_exec(method, url, username=userName)
        return resp

    def query_member_report(self, userName=env.USERNAME_PM):
        """
        查看项目成员报告
        :param userName: 默认为PM角色
        :return:
        """
        # 获取用户ID
        userId = self.user.get_user_id(username=userName)
        method = 'GET'
        url = '/api/task/case/task/report/{0}/{1}'.format(userId, self.projectId)

        resp = req_exec(method, url, username=userName)
        return resp

    def query_added_value_report(self, userName=env.USERNAME_PM):
        """
        查看附加值报告
        :param userName: 默认为PM角色
        :return:
        """
        method = 'GET'
        url = '/api/task/case/task/project/{0}/deals?currentPage={1}&perPage={2}'.format(self.projectId,
                                                                                         self.currentPage,
                                                                                         self.perPage)

        resp = req_exec(method, url, username=userName)
        return resp

    def query_internal_evaluation(self, userName=env.USERNAME_PM):
        """
        查看组内互评
        :param userName: 默认为PM角色
        :return:
        """
        method = 'GET'
        url = '/api/task/case/task/assess?projectId={0}'.format(self.projectId)

        resp = req_exec(method, url, username=userName)
        return resp


class Document(Project):
    """
    项目文档
    """

    def __init__(self, projectName, userName=env.USERNAME_PM):
        super(Document, self).__init__()
        self.projectName = projectName
        self.projectId = self.query_project_id_by_name(projectName, userName=userName)

    def upload_document(self, fileName, isPublic=0, userName=env.USERNAME_PM):
        """
        上传文件
        :param fileName: 文件名
        :param isPublic: 是否公开: 0:个人可见  ————默认个人可见
                                 1:项目可见
                                 2:全员可见
        :param userName: 默认为PM角色
        :return:
        """
        allOnly = False
        projectOnly = False
        createrOnly = False
        if isPublic == 0:
            createrOnly = True
        elif isPublic == 1:
            projectOnly = True
        elif isPublic == 2:
            allOnly = True
        method = 'POST'
        url = '/api/task/case/task/{0}/upload'.format(self.projectId)
        data = {
            "allOnly": allOnly,
            "createrOnly": createrOnly,
            "desc": '',
            "fileName": fileName,
            "projectOnly": projectOnly,
            "title": fileName
        }
        files = {'file': ('fileName', open('../data/' + fileName + '', 'rb'), 'application/*')}

        resp = req_exec(method, url, data=data, files=files, username=userName)
        return resp


class Member(Project):
    """
    项目人员
    """

    def __init__(self, projectName, userName=env.USERNAME_PM):
        super(Member, self).__init__()
        self.user = User()
        self.projectName = projectName
        self.projectId = self.query_project_id_by_name(projectName, userName=userName)

    def query_members(self, userName=env.USERNAME_PM):
        """
        查询人员
        :param userName: 默认为PM角色
        :return:
        """
        method = 'GET'
        url = '/api/task/case/task/projects/{0}/users'.format(self.projectId)

        resp = req_exec(method, url, username=userName)
        return resp

    def create_recruit(self, postName, postSum=None, postJobShare=None, postType=None, roleType='项目管理',
                       postDescription='', startTime='', endTime='', userName=env.USERNAME_PM):
        """
        新增招募信息
        :param postName: 职位名称
        :param postSum: 招募人数
        :param postJobShare: 职位全时率
        :param postType: 职位类型: 1:Java后端
                                 2:Web前端
                                 3:手机前端
                                 4:小程序
                                 5:UI
                                 6:测试
        :param roleType: 角色类型
        :param postDescription: 职位描述
        :param startTime: 开始日期
        :param endTime: 结束日期
        :param userName: 默认为PM角色
        :return:
        """
        # 获取proRoleId
        proRoleId = self.query_role_id_by_name(roleName=roleType, projectName=self.projectName, userName=userName)

        # 获取系统当前日期
        if not startTime:
            startTime = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        if not endTime:
            endTime = time.strftime('%Y-%m-%d', time.localtime(time.time() + 24 * 3600))

        # UTC格式日期转GMT格式,默认为8点
        startTime = utc_to_gmt(startTime, utc_fmt="%Y-%m-%d").replace('00:00:00', '08:00:00')
        endTime = utc_to_gmt(endTime, utc_fmt="%Y-%m-%d").replace('00:00:00', '08:00:00')

        method = 'POST'
        url = '/api/task/case/task/project/recruit?'
        data = {
            "postName": postName,
            "postDescription": postDescription,
            "postSum": postSum,
            "postJobShare": postJobShare,
            "proRoleId": proRoleId,
            "postType": postType,
            "startTime": startTime,
            "endTime": endTime,
            "openFlag": 0,
            "projectId": self.projectId
        }

        resp = req_exec(method, url, data=data, username=userName)
        return resp

    def modify_recruit(self, postName, userName=env.USERNAME_PM, **modifyParams):
        """
        修改招募信息
        :param postName: 职位名称
        :param userName: 默认为PM角色
        :param modifyParams: newPostName: 待修改职位名称
                             postSum: 招募人数
                             postJobShare: 职位全时率
                             postType: 职位类型: 1:Java后端
                                               2:Web前端
                                               3:手机前端
                                               4:小程序
                                               5:UI
                                               6:测试
                             postDescription: 职位描述
                             startTime: 开始日期
                             endTime: 结束日期
        :return:
        """
        resp = self.query_recruit_info_by_name(postName)
        if resp:
            # 获取招募信息ID
            recruitId = resp['recruitId']

            # 复制原招募信息
            modifyBody = resp
            del modifyBody['recruitId']
            del modifyBody['inPlaceSum']
            del modifyBody['createdAt']
            del modifyBody['updatedAt']
            modifyBody['postJobShare'] = int(modifyBody['postJobShare'])

            # UTC格式日期转GMT格式
            modifyBody['startTime'] = utc_to_gmt(modifyBody['startTime'], utc_fmt='%Y-%m-%d').replace(
                '00:00:00', '08:00:00')
            modifyBody['endTime'] = utc_to_gmt(modifyBody['endTime'], utc_fmt='%Y-%m-%d').replace(
                '00:00:00', '08:00:00')

            for modifyParamsKey in modifyParams.keys():
                if modifyParamsKey == 'newPostName':
                    modifyBody['postName'] = modifyParams[modifyParamsKey]
                if modifyParamsKey == 'postSum':
                    modifyBody['postSum'] = modifyParams[modifyParamsKey]
                if modifyParamsKey == 'postJobShare':
                    modifyBody['postJobShare'] = modifyParams[modifyParamsKey]
                if modifyParamsKey == 'postType':
                    modifyBody['postType'] = modifyParams[modifyParamsKey]
                if modifyParamsKey == 'postDescription':
                    modifyBody['postDescription'] = modifyParams[modifyParamsKey]
                if modifyParamsKey == 'startTime':
                    modifyBody['startTime'] = utc_to_gmt(modifyParams[modifyParamsKey], utc_fmt='%Y-%m-%d').replace(
                        '00:00:00', '08:00:00')
                if modifyParamsKey == 'endTime':
                    modifyBody['endTime'] = utc_to_gmt(modifyParams[modifyParamsKey], utc_fmt='%Y-%m-%d').replace(
                        '00:00:00', '08:00:00')
            method = 'PATCH'
            data = modifyBody
            url = '/api/task/case/task/project/recruit/{0}'.format(recruitId)

            resp = req_exec(method, url, data=data, username=userName)
            return resp
        else:
            raise Exception('暂无此招募信息,请核实后操作')

    def operate_recruit(self, postName, openFlag=True, userName=env.USERNAME_PM):
        """
        打开或关闭招募信息
        :param postName: 职位名称
        :param openFlag: 是否打开
        :param userName: 默认为PM角色
        :return:
        """
        resp = self.query_recruit_info_by_name(postName)
        if resp:
            # 获取招募信息ID
            recruitId = resp['recruitId']

            # 复制原招募信息
            data = resp
            del data['recruitId']
            del data['inPlaceSum']
            del data['createdAt']
            del data['updatedAt']
            data['postJobShare'] = int(data['postJobShare'])

            # UTC格式日期转GMT格式
            data['startTime'] = utc_to_gmt(data['startTime'], utc_fmt='%Y-%m-%d').replace(
                '00:00:00', '08:00:00')
            data['endTime'] = utc_to_gmt(data['endTime'], utc_fmt='%Y-%m-%d').replace(
                '00:00:00', '08:00:00')

            if openFlag:
                data['openFlag'] = 1
            else:
                data['openFlag'] = 0
            method = 'PATCH'
            url = '/api/task/case/task/project/recruit/{0}'.format(recruitId)

            resp = req_exec(method, url, data=data, username=userName)
            return resp
        else:
            raise Exception('暂无此招募信息,请核实后操作')

    def delete_recruit(self, postName, userName=env.USERNAME_PM):
        """
        删除招募信息
        :param postName: 职位名称
        :param userName: 默认为PM角色
        :return:
        """
        recruitId = self.query_recruit_id_by_name(postName)
        method = 'DELETE'
        data = {}
        url = '/api/task/case/task/project/recruit/{0}'.format(recruitId)

        resp = req_exec(method, url, data=data, username=userName)
        return resp

    def query_recruits(self, userName=env.USERNAME_PM):
        """
        查询当前项目招募信息
        :param userName:
        :return:
        """
        method = 'GET'
        url = '/api/task/case/task/project/{0}/recruit/'.format(self.projectId)

        resp = req_exec(method, url, username=userName)
        return resp

    def query_recruit_info_by_name(self, postName, userName=env.USERNAME_PM):
        """
        根据职位名称获取招募信息
        :param postName: 职位名称
        :param userName: 默认为PM角色
        :return:
        """
        resp = self.query_recruits(userName=userName)
        recruitList = resp['content']['data']['list']
        if recruitList:
            for recruit in recruitList:
                if recruit['postName'] == postName:
                    return recruit
            else:
                raise Exception('暂无该招募信息,请核实后操作')
        else:
            raise Exception('该项目暂无招募信息,请核实后操作')

    def query_recruit_id_by_name(self, postName, userName=env.USERNAME_PM):
        """
        根据职位名称获取招募信息ID
        :param postName: 职位名称
        :param userName: 默认为PM角色
        :return:
        """
        resp = self.query_recruits(userName=userName)
        recruitId = get_value_from_resp(resp['content'], 'recruitId', 'postName', postName)
        if recruitId:
            return recruitId
        else:
            raise Exception('暂无此招募信息,请核实后操作')


if __name__ == '__main__':
    pass
    config = ReadConfig()

    # pm = Project()
    # pm.query_projects()
    # print(pm.query_project_id_by_name(projectName='test_中文名称项目'))
    # pm.create_project(projectName='test_中文名称项目')
    # pm.approve_project(projectName='test_中文名称项目', approveStatus=2)
    # pm.modify_project(projectName='中文名称项目11', newProjectName='中文名称项目22', description='中文名称项目描述',
    #                   startTime='2021-08-12', endTime='2021-08-31')
    # pm.disable_or_archive_project(projectName='中文名称项目22', operationType='disable', filterType='filter')
    # pm.operate_project(projectName='中文名称项目22', applyType=3)
    # pm.approve_project(projectName='中文名称项目22')
    # pm.query_web_hook(projectName='test_中文名称项目')
    # print(pm.query_role_id_by_name(roleName='项目管理', projectName='test_中文名称项目'))
    # pm.modify_role(roleName='项目管理1', projectName='test_中文名称项目', newRoleName='项目管理', createTask=0, updateTask=0)
    # pm.query_task_status(projectName='test_中文名称项目', bugFlag=1)
    # print(pm.query_status_id_by_name(statusName='未开发', projectName='test_中文名称项目'))
    # pm.modify_status(statusName='未开发1', projectName='test_中文名称项目', newStatusName='未开发')
    # pm.modify_status(statusName='轻微1', projectName='test_中文名称项目', bugFlag=1, newStatusName='轻微')
    # pm.modify_task_type(typeName='开发任务1', projectName='test_中文名称项目', newTypeName='开发任务')
    # pm.modify_task_priority(priorityName='普通', projectName='test_中文名称项目', newPriorityName='普通', defaultMark=1,
    #                         priorityColor=config.get_color('Purple'))

    # tm = Task('test_中文名称项目')
    # tm.query_index_data()
    # tm.query_tasks()
    # print(tm.query_task_id_by_name(taskName='task1'))
    # print(tm.query_task_info_by_name(taskName='task2'))
    # tm.create_task(taskName='中文任务123', deadLine='2021-8-5', taskGetDateLine='2021-8-6')
    # tm.copy_task(taskName='task1')
    # tm.modify_task(taskName='task1', newTaskName='test11', description='test', points='15', countedPoints='5',
    #                deadLine='2021-8-16', taskGetDateLine='2021-8-15')
    # tm.archive_task(taskName='test5')
    # tm.archive_task_and_copy(taskName='test4', score='50', attr='100', remark='中文测试')
    # tm.delete_task(taskName='task2')
    # tm.reply_task(taskName='test11', content='')
    # tm.get_task(taskName='中文任务')
    # tm.query_task_replies(taskName='test11')
    # print(tm.query_replies_id_by_content(taskName='test11', contentList=[]))
    # print(tm.query_replies_id_by_user(taskName='test11', contentUser=env.USERNAME_PMO))
    # tm.delete_replies_by_content(taskName='test11', content='中文测试')
    # tm.delete_replies_by_user(taskName='test11', contentUser=env.USERNAME_PM)
    # tm.give_red_flower(taskName='test4')

    # plan = Plan('test_中文名称项目')
    # plan.create_plan(planName='中文测试')
    # plan.query_plans()
    # print(plan.query_plan_id_by_name(planName='中文测试'))
    # plan.query_plan_info_by_name(planName='中文测试')
    # plan.query_plan_tasks(planName='中文测试')

    # ce = ComprehensiveEvaluation('test_中文名称项目')
    # ce.query_manage_report()
    # ce.query_member_report()
    # ce.query_added_value_report()
    # ce.query_internal_evaluation()

    # doc = Document('test_中文名称项目')
    # doc.upload_document('Jenkins流水线配置.docx')
    # doc.upload_document('管理员.xlsx')

    # m = Member('test_中文名称项目')
    # m.create_recruit(postName='中文测试1234', postSum=10, postJobShare=50, postType=4, postDescription='中文测试1234',
    #                  startTime='2021-8-6', endTime='2021-8-6')
    # m.modify_recruit(postName='CICS', newPostName='中文测试1234', postSum=100, postJobShare=20, postType=6,
    #                  postDescription='CICS', startTime='2021-8-10', endTime='2021-8-10')
    # m.operate_recruit(postName='中文测试1234', openFlag=True)
    # m.delete_recruit(postName='中文测试1234')
    # m.query_recruits()
    # try:
    #     m.query_recruit_info_by_name('test123')
    # except Exception as e:
    #     print(e)
