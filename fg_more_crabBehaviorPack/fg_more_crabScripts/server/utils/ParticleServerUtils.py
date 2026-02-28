# -*- coding: utf-8 -*-
from ..ServerBaseUtils import *

# particle_name_to_id_map={}
#
# particle_id_to_name_map={}
#
# particle_id_to_data_map={}


def CreateParticle(particle_name, particle_pos):
    """
    在指定坐标生成指定名称粒子特效，无返回值
    :param particle_name: 粒子名称
    :param particle_pos: 坐标

    """
    _x, _y, _z = particle_pos
    GetCompCommandLevel().SetCommand("/particle %s %s %s %s" % (particle_name, _x, _y, _z))

# <editor-fold desc="处理特效到所有客户端">

def CreateParticleToClient(**kwargs):
    """
    向所有客户端广播创建粒子发射器事件。

    关键字参数 (**kwargs):
    - server_id (str): 服务端存储的粒子发射器唯一标识符。如果未提供，将自动生成一个UUID。
    - effect_name (str): 粒子发射器的名称，需与粒子发射器的JSON文件中的identifier匹配。
    - offset (tuple[float, float, float], optional): 粒子发射器的位置偏移，默认为 (0.0, 0.0, 0.0)。
    - rotation (tuple[float, float, float], optional): 粒子发射器的旋转角度（ZYX顺序，单位为度数），默认为 (0.0, 0.0, 0.0)。
    - entity_id (int, optional): 绑定的实体ID，如果存在，粒子发射器将绑定到该实体。
    - bone_name (str, optional): 绑定的骨骼名称，不区分大小写，默认为 "body"。
    - variable_map(dict[str,float]): 变量字典

    功能:
    - 生成一个唯一的 `server_id`，将其添加到kwargs中。
    - 使用 `ServerMain.BroadcastToAllClient` 向所有客户端广播粒子发射器创建事件。
    """
    server_id = str(uuid.uuid4())
    kwargs["server_id"] = server_id
    GetServerMainSystem().BroadcastToAllClient("ServerCreateParticleEvent", kwargs)
    return server_id
    # effect_name=kwargs["effect_name"]
    # particle_name_to_id_map[effect_name]=server_id
    # particle_id_to_name_map[server_id]=effect_name
    # particle_id_to_data_map[server_id]=kwargs


def RemoveParticleToClient(**kwargs):
    """
    向所有客户端广播停止粒子发射器事件。

    关键字参数 (**kwargs):
    - server_id (str): 服务端存储的粒子发射器唯一标识符，用于标识需要停止的粒子发射器。
    - effect_name (str): 粒子发射器的名称，需与粒子发射器的JSON文件中的identifier匹配。

    功能:
    - 使用 `ServerMain.BroadcastToAllClient` 向所有客户端广播粒子发射器停止事件。
    """
    GetServerMainSystem().BroadcastToAllClient("ServerRemoveParticleEvent", kwargs)
    # server_id=kwargs["server_id"]
    # effect_name=kwargs["effect_name"]
    # particle_name_to_id_map.pop(effect_name,None)
    # particle_id_to_name_map.pop(server_id,None)
    # particle_id_to_data_map.pop(server_id,None)


def SetParticleVariableToClient(**kwargs):
    """
    向所有客户端广播修改粒子发射器参数事件。

    关键字参数 (**kwargs):
    - server_id (str): 服务端存储的粒子发射器唯一标识符，用于标识需要停止的粒子发射器。
    - variable_map(dict[str,float]): 变量字典。

    功能:
    - 使用 `ServerMain.BroadcastToAllClient` 向所有客户端广播粒子发射器停止事件。
    """
    GetServerMainSystem().BroadcastToAllClient("ServerParticleChangeVariableEvent", kwargs)


def PauseParticleToClient(**kwargs):
    """
    向所有客户端广播暂停粒子发射器逻辑更新事件。

    关键字参数 (**kwargs):
    - server_id (str): 服务端存储的粒子发射器唯一标识符，用于标识需要停止的粒子发射器。

    功能:
    - 使用 `ServerMain.BroadcastToAllClient` 向所有客户端广播粒子发射器停止事件。
    """
    GetServerMainSystem().BroadcastToAllClient("ServerPauseParticleEvent", kwargs)


def ResumeParticleToClient(**kwargs):
    """
    向所有客户端广播恢复暂停粒子发射器逻辑更新事件。

    关键字参数 (**kwargs):
    - server_id (str): 服务端存储的粒子发射器唯一标识符，用于标识需要停止的粒子发射器。

    功能:
    - 使用 `ServerMain.BroadcastToAllClient` 向所有客户端广播粒子发射器停止事件。
    """
    GetServerMainSystem().BroadcastToAllClient("ServerResumeParticleEvent", kwargs)

# </editor-fold>

# <editor-fold desc="处理特效到单独客户端">
def CreateParticleToClientById(client_id, **kwargs):
    """
    向指定客户端发送创建粒子发射器事件。

    参数:
    - client_id (int): 目标客户端的唯一标识符。

    关键字参数 (**kwargs):
    - server_id (str): 服务端存储的粒子发射器唯一标识符。如果未提供，将自动生成一个UUID。
    - effect_name (str): 粒子发射器的名称，需与粒子发射器的JSON文件中的identifier匹配。
    - offset (tuple[float, float, float], optional): 粒子发射器的位置偏移，默认为 (0.0, 0.0, 0.0)。
    - rotation (tuple[float, float, float], optional): 粒子发射器的旋转角度（ZYX顺序，单位为度数），默认为 (0.0, 0.0, 0.0)。
    - entity_id (int, optional): 绑定的实体ID，如果存在，粒子发射器将绑定到该实体。
    - bone_name (str, optional): 绑定的骨骼名称，不区分大小写，默认为 "body"。
    - variable_map(dict[str,float]): 变量字典。

    功能:
    - 生成一个唯一的 `server_id`，将其添加到kwargs中。
    - 使用 `ServerMain.NotifyToClient` 向指定客户端发送粒子发射器创建事件。
    """
    server_id = str(uuid.uuid4())
    kwargs["server_id"] = server_id
    GetServerMainSystem().NotifyToClient(client_id, "ServerCreateParticleEvent", kwargs)
    return server_id
    # effect_name = kwargs["effect_name"]
    # particle_name_to_id_map[effect_name] = server_id
    # particle_id_to_name_map[server_id] = effect_name
    # particle_id_to_data_map[server_id] = kwargs


def RemoveParticleToClientById(client_id, **kwargs):
    """
    向指定客户端发送停止粒子发射器事件。

    参数:
    - client_id (int): 目标客户端的唯一标识符。

    关键字参数 (**kwargs):
    - server_id (str): 服务端存储的粒子发射器唯一标识符，用于标识需要停止的粒子发射器。
    - effect_name (str): 粒子发射器的名称，需与粒子发射器的JSON文件中的identifier匹配。

    功能:
    - 使用 `ServerMain.NotifyToClient` 向指定客户端发送粒子发射器停止事件。
    """
    GetServerMainSystem().NotifyToClient(client_id, "ServerRemoveParticleEvent", kwargs)
    # server_id = kwargs["server_id"]
    # effect_name = kwargs["effect_name"]
    # particle_name_to_id_map.pop(effect_name, None)
    # particle_id_to_name_map.pop(server_id, None)
    # particle_id_to_data_map.pop(server_id, None)


def PauseParticleToClientById(client_id, **kwargs):
    """
    向指定客户端发送暂停粒子发射器逻辑更新事件。

    参数:
    - client_id (int): 目标客户端的唯一标识符。

    关键字参数 (**kwargs):
    - server_id (str): 服务端存储的粒子发射器唯一标识符，用于标识需要暂停的粒子发射器。

    功能:
    - 使用 `ServerMain.NotifyToClient` 向指定客户端发送粒子发射器暂停事件。
    """
    GetServerMainSystem().NotifyToClient(client_id, "ServerPauseParticleEvent", kwargs)


def ResumeParticleToClientById(client_id, **kwargs):
    """
    向指定客户端发送恢复暂停粒子发射器逻辑更新事件。

    参数:
    - client_id (int): 目标客户端的唯一标识符。

    关键字参数 (**kwargs):
    - server_id (str): 服务端存储的粒子发射器唯一标识符，用于标识需要恢复的粒子发射器。

    功能:
    - 使用 `ServerMain.NotifyToClient` 向指定客户端发送粒子发射器恢复事件。
    """
    GetServerMainSystem().NotifyToClient(client_id, "ServerResumeParticleEvent", kwargs)


# </editor-fold>