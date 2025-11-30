# -*- coding: utf-8 -*-

from fg_more_crabScripts.client.api import EmptyDataClientApi
from fg_more_crabScripts.client.base_parent_class.ClientListener import *


class ClientTaskFunction(ClientListener):
    def __init__(self, task_queue_name, task_function, task_function_uuid, is_exclusive):
        self.task_queue_name = task_queue_name
        self.task_function = task_function
        self.task_function_uuid = str(task_function_uuid)
        self.is_exclusive = is_exclusive
        self.task_function_already_run = False

        print("****************************************%s" % self.task_function_uuid)
        if self.is_exclusive:
            if self.GetCurrentTaskQueue():
                print "already has task,remove self %s" % self.task_function_uuid
                print self
                return
            else:
                self.SetCurrentTaskQueue([self.task_function_uuid])
        else:
            self.AddTaskToTaskQueue()

        super(ClientTaskFunction, self).__init__(True)

    def GetCurrentTaskQueue(self):
        return EmptyDataClientApi.GetClientKeyValue(self.task_queue_name, [], "empty_studio", True)

    def SetCurrentTaskQueue(self, task_queue):
        EmptyDataClientApi.SetClientKeyValue(self.task_queue_name, task_queue, "empty_studio", True)

    def ClearCurrentTaskQueue(self):
        print("----------------------------------------------")
        print "ClearCurrentTaskQueue %s" % self.task_function_uuid
        if self.is_exclusive:
            task_queue = self.GetCurrentTaskQueue()
            print task_queue
            if task_queue and task_queue[0] == self.task_function_uuid:
                print "all is clear"
                self.SetCurrentTaskQueue([])
        else:
            self.SetCurrentTaskQueue([])

    def AddTaskToTaskQueue(self):
        task_queue = self.GetCurrentTaskQueue()
        task_queue.append(self.task_function_uuid)
        self.SetCurrentTaskQueue(task_queue)

    def CheckCanRunTaskFunction(self):
        task_queue = self.GetCurrentTaskQueue()
        return task_queue and task_queue[0] == self.task_function_uuid

    def OnScriptTickClient(self):
        if not self.task_function_already_run:
            if self.CheckCanRunTaskFunction():
                try:
                    self.task_function()  # 执行任务
                except Exception as e:
                    print("执行任务函数时发生错误: {}".format(e))

                if not self.is_exclusive:
                    task_queue = self.GetCurrentTaskQueue()
                    if task_queue:
                        task_queue.pop(0)
                        self.SetCurrentTaskQueue(task_queue)
                self.task_function_already_run = True
                self.UnRegister()
