# -*- coding: utf-8 -*-
import copy
import random
import uuid
import math
import time
import json
import traceback
import logging

from mod.common.mod import Mod
from mod.common.utils.mcmath import Vector3, Quaternion
import mod.client.extraClientApi as ClientApi
import mod.server.extraServerApi as ServerApi

DEVELOPMENT = True
CanUnlockTime = time.mktime((2024, 1, 14, 20, 0, 0, 0, 0, 0))

# Mod Version
ModName = "fg_more_crab"
ModVersion = "1.0.0"
ConfigVersion = "one"

ModScriptFilePath = "fg_more_crabScripts"

# Server System
ServerSystemName = "fg_more_crabServerSystem"
ServerSystemClsPath = ModScriptFilePath + ".modMain.ServerMain"

# Client System
ClientSystemName = "fg_more_crabClientSystem"
ClientSystemClsPath = ModScriptFilePath + ".modMain.ClientMain"

# Engine
Minecraft = "Minecraft"

# UI Path
BasePanel0 = "/variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix"
BasePanel = BasePanel0 + '/safezone_screen_panel/root_screen_panel'
UiBasePath = ModScriptFilePath + ".client.ui."

TextureBasePath = "textures/ui/empty_ble/"

# ClientSystem
ClientSystem = ClientApi.GetClientSystemCls()
ClientEngineNamespace = ClientApi.GetEngineNamespace()
ClientEngineSystemName = ClientApi.GetEngineSystemName()

# ServerSystem
ServerSystem = ServerApi.GetServerSystemCls()
ServerEngineNameSpace = ServerApi.GetEngineNamespace()
ServerEngineSystemName = ServerApi.GetEngineSystemName()


def SetDevelopmentMessage(*args):
    print("[this empty studio development message]->%s\n" % (args,))


def DoProfile(second):
    ServerApi.StartProfile()

    def finishProfile():
        timestamp = int(time.time())
        filename = "profile_%d.svg" % timestamp
        ServerApi.StopProfile(filename)

    comp = ServerApi.GetEngineCompFactory().CreateGame(ServerApi.GetLevelId())
    comp.AddTimer(second, finishProfile)


def DoProfileEvent(second):
    ServerApi.StartRecordEvent()

    def finishProfile():
        result = ServerApi.StopRecordEvent()
        for eventName, data in result.iteritems():
            head = "event[{}]".format(eventName)
            head = head.ljust(20)
            print "{} sendNum={} sendSize={} recvNum={} recvSize={}".format(head, data["send_num"], data["send_size"], data["recv_num"],
                                                                            data["recv_size"])

    comp = ServerApi.GetEngineCompFactory().CreateGame(ServerApi.GetLevelId())
    comp.AddTimer(second, finishProfile)


def DoProfilePacket(second):
    ServerApi.StartRecordPacket()

    def finishProfile():
        result = ServerApi.StopRecordPacket()
        for packetName, data in result.iteritems():
            head = "packet[{}]".format(packetName)
            head = head.ljust(20)
            print "{} sendNum={} sendSize={} recvNum={} recvSize={}".format(head, data["send_num"], data["send_size"], data["recv_num"], data["recv_size"])

    comp = ServerApi.GetEngineCompFactory().CreateGame(ServerApi.GetLevelId())
    comp.AddTimer(second, finishProfile)
