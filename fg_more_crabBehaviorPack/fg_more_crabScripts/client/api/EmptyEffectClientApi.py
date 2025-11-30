# -*- coding: utf-8 -*-

from fg_more_crabScripts.client.api.EmptyBaseClientApi import *


def CreateEngineSfxFromEditor(path, pos=None, rot=None, scale=None, need_play_now=True):
    """
    创建序列帧特效
    创建序列帧后，可以用返回的frame_entity_id创建序列帧分类中的相关组件，设置所需属性，以实现各种表现效果
    切换维度后会自动隐藏非本维度创建的而且没有绑定实体的序列帧, 回到该维度后会自动重新显示
    需要注意，序列帧创建之后需要调用frameAniControl组件的play函数才会播放,如果播放非本维度创建的序列帧,会同时修改该序列帧的创建维度为当前维度

    :param path: 特效配置路径，需要为"effects/xxx.json"，"xxx"为编辑器创建序列帧时填写的名称
    :type path: str
    :param pos: 创建位置，可选，没传则可以创建完用frameAniTrans组件设置
    :type pos: 	tuple[float,float,float] or None
    :param rot: 角度，可选，没传则可以创建完用frameAniTrans组件设置
    :type rot: tuple[float,float,float] or None
    :param scale: 缩放系数，可选，没传则可以创建完用frameAniTrans组件设置
    :type scale: tuple[float,float,float] or None
    :param need_play_now: need_play_now
    :type need_play_now: bool
    :return:frame_entity_id或者None
    :rtype:int or None
    """
    frame_entity_id = ClientMain.CreateEngineSfxFromEditor(path, pos, rot, scale)
    if need_play_now and frame_entity_id:
        GetFrameAniControlComp(frame_entity_id).Play()
    return frame_entity_id


def RemoveSfx(frame_entity_id):
    ClientMain.DestroyEntity(frame_entity_id)
