import json
import time

from FastApi.aws.user import User
from FastApi.common.base_api import req_exec
from FastApi.aws.tempate import Temps
from FastApi.aws.homepage import PersonalHomepage
from FastApi.common.helper import get_value_from_resp, utc_to_bjs, utc_to_gmt, bjs_to_utc
from FastApi.conf import env


class Project(PersonalHomepage):
    """
    项目管理
    """

    def __init__(self):
        super(Project, self).__init__()

    @staticmethod
    def create_project(projectName, startTime='', endTime='', templateName='基本模板', description='', valid=True,
                       userName=env.USERNAME_PM):
        """
        创建项目
        :param projectName: 项目名称
        :param startTime: 项目开始时间，默认为当天 %Y-%m-%d
        :param endTime: 项目结束时间，默认为第二天 %Y-%m-%d
        :param templateName: 模板名称，暂为固定模板，无需入参
        :param description: 项目描述
        :param valid:
        :param userName: 默认为PM角色
        :return:
        """
        # 获取当天日期
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
        data = {
            'applyStatus': 0,
            'applyType': 4,
            'applyUserDescription': json.dumps(applyUserDescription)
        }
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
                approveId = ''
                applyUserDescription = pending_approval['applyUserDescription']
                if applyUserDescription:
                    if json.loads(applyUserDescription)['projectName'].encode('utf-8') == projectName.encode('utf-8'):
                        approveId = pending_approval['approveId']
                else:
                    if pending_approval['projectName'].encode('utf-8') == projectName.encode('utf-8'):
                        approveId = pending_approval['approveId']

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
                raise Exception('暂无此项目审批申请，请核实')
        else:
            raise Exception('暂无审批申请，请核实')

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

            resp = req_exec(method, url, data=data, username=userName)
        return resp

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
        projectId = self.query_project_id_by_name(projectName, filterType=filterType)
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
        projectId = self.query_project_id_by_name(projectName, filterType=filterType)
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
        for projectBody in resp['content']['data']['list']:
            if projectBody['projectName'] == projectName:
                return projectBody

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
        return get_value_from_resp(resp['content'], 'projectId', 'projectName', projectName)


class Task(Project):
    """
    项目任务
    """

    def __init__(self, projectName):
        super(Task, self).__init__()
        self.user = User()
        self.projectId = self.query_project_id_by_name(projectName)

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

        # 获取当天日期
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
        :param modifyParams: 待修改入参：newTaskName:待修改任务名称
                                       description:任务描述
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

            # 生成创建时间参数
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
        :param copy: 是否复制，默认复制
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

        resp = None
        for replyId in replyIdList:
            method = 'DELETE'
            data = {}
            url = '/api/task/case/task/projects/{0}/tasks/{1}/reply/{2}'.format(self.projectId, taskId, replyId)

            resp = req_exec(method, url, data=data, username=userName)
            if resp['content']['msg'] != 'success' or resp['content']['data'] != '删除成功':
                return resp
        return resp

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
        return get_value_from_resp(resp['content'], 'taskId', 'title', taskName)

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

    def __init__(self, projectName):
        super(Plan, self).__init__()
        self.task = Task(projectName)
        self.projectId = self.query_project_id_by_name(projectName)

    def create_plan(self, planName, description='', startTime='', endTime='', userName=env.USERNAME_PM):
        """
        创建计划
        :param planName: 计划名称
        :param description: 计划描述
        :param startTime: 计划开始时间:默认为当天 %Y-%m-%d
        :param endTime: 计划结束时间:默认为第二天 %Y-%m-%d
        :param userName: 默认为PM角色
        :return:
        """
        # 获取当天日期
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
            url += url + '&status=2'

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
        return get_value_from_resp(resp['content'], 'planId', 'name', planName)

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

    def __init__(self, projectName):
        super(ComprehensiveEvaluation, self).__init__()
        self.user = User()
        self.projectId = self.query_project_id_by_name(projectName)

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

    def __init__(self, projectName):
        super(Document, self).__init__()


class Member(Project):
    """
    项目人员
    """

    def __init__(self, projectName):
        super(Member, self).__init__()
        self.user = User()
        self.projectId = self.query_project_id_by_name(projectName)

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

    def query_roles(self, userName=env.USERNAME_PM):
        """
        查询角色
        :param userName: 默认为PM角色
        :return:
        """
        method = 'GET'
        url = '/api/task/case/task/projects/{0}/roles'.format(self.projectId)

        resp = req_exec(method, url, username=userName)
        return resp

    def create_recruit(self, postName, postSum=None, postJobShare=None, postType=None, postDescription='',
                       startTime='', endTime='', userName=env.USERNAME_PM):
        """

        :param postName:
        :param postSum:
        :param postJobShare:
        :param postType:
        :param postDescription:
        :param startTime:
        :param endTime:
        :param userName:
        :return:
        """
        # 获取proRoleId
        resp = self.query_roles(userName=userName)
        proRoleId = get_value_from_resp(resp['content'], 'proRoleId', 'projectId', self.projectId)

        # 获取当天日期
        if not startTime:
            startTime = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        if not endTime:
            endTime = time.strftime('%Y-%m-%d', time.localtime(time.time() + 24 * 3600))

        startTime = utc_to_gmt(startTime, utc_fmt="%Y-%m-%d")
        endTime = utc_to_gmt(endTime, utc_fmt="%Y-%m-%d")

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


class ProjectSetting(object):
    """
    项目设置
    """

    def __init__(self):
        pass


if __name__ == '__main__':
    pass
    # pm = Project()
    # pm.query_projects()
    # print(pm.query_project_id_by_name('中文名称项目1'))
    # pm.create_project(projectName='中文名称项目111')
    # pm.approve_project(projectName='中文名称项目111')
    # pm.modify_project(projectName='中文名称项目11', newProjectName='中文名称项目22', description='中文名称项目描述',
    #                   startTime='2021-08-12', endTime='2021-08-31')
    # pm.disable_or_archive_project(projectName='中文名称项目22', operationType='disable', filterType='filter')
    # pm.operate_project(projectName='中文名称项目22', applyType=3)
    # pm.approve_project(projectName='中文名称项目22')

    # tm = Task('中文名称项目111')
    # tm.query_index_data()
    # tm.query_tasks()
    # print(tm.query_task_id_by_name(taskName='task1'))
    # print(tm.query_task_info_by_name(taskName='task2'))
    # tm.create_task(taskName='中文任务', deadLine='2021-8-5', taskGetDateLine='2021-8-6', planName='中文测试')
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

    # plan = Plan('中文名称项目111')
    # plan.create_plan(planName='中文测试')
    # plan.query_plans()
    # print(plan.query_plan_id_by_name(planName='中文测试'))
    # plan.query_plan_info_by_name(planName='中文测试')
    # plan.query_plan_tasks(planName='中文测试')

    # ce = ComprehensiveEvaluation('中文名称项目111')
    # ce.query_manage_report()
    # ce.query_member_report()
    # ce.query_added_value_report()
    # ce.query_internal_evaluation()

    m = Member('中文名称项目111')
    m.create_recruit(postName='中文测试123', postSum=10, postJobShare=50, postType=4)
