# -*- coding: utf-8 -*-

RegisterEntityActorScriptAnimate = {
    # "entity_type_str"
    "all": [
        # 动画/动画控制器名称:动画/动画控制器控制表达式
        # {"dummy_re_controller": "query.mod.dummy>0"}
    ]
}
RegisterEntityAnimation = {
    # "entity_type_str"
    "all": [
        # 动画键:动画名称
        # {"animation.dummy.dummy": "animation.dummy.dummy"}
    ]
}
RegisterEntityAnimationController = {
    # "entity_type_str"
    "all": [
        # 动画控制器键:动画控制器名称
        # {"dummy_ac": "controller.animation.dummy.dummy"}
    ]
}
RegisterEntityRenderController = {
    # "entity_type_str"
    "all": [
        # 渲染控制器名称:渲染控制器条件
        # {"controller.render.dummy": "query.mod.dummy>0"}
    ]
}
RegisterEntityGeometry = {
    # "entity_type_str"
    "all": [
        # 渲染几何体键:渲染几何体名称
        # {"dummy": "geometry.dummy"}
    ]
}
RegisterEntityMaterial = {
    # "entity_type_str"
    "all": [
        # 材质键:材质名称
    ]
}
RegisterEntityTexture = {
    # "entity_type_str"
    "all": [
        # 贴图键:贴图路径
        # {"dummy": "textures/entity/dummy"}
    ]
}
RegisterEntitySoundEffect = {
    # "entity_type_str"
    "all": [

        # 音效资源Key:音效资源名称
        # {"dummy": "music.dummy.dummy"}
    ]
}
RegisterEntityParticleEffect = {
    # "entity_type_str"
    "all": [

        # 特效资源Key:特效资源名称
        # {"dummy": "fg:dummy"}
    ]
}

RegisterAllEntityRenderExcludeList = []

AllRenderNeedAddVariable = ""


def HasRenderDataEntity(entity_type_str="all"):
    return any([
        RegisterEntityActorScriptAnimate.get(entity_type_str, []),
        RegisterEntityAnimation.get(entity_type_str, []),
        RegisterEntityAnimationController.get(entity_type_str, []),
        RegisterEntityRenderController.get(entity_type_str, []),
        RegisterEntityGeometry.get(entity_type_str, []),
        RegisterEntityMaterial.get(entity_type_str, []),
        RegisterEntityTexture.get(entity_type_str, []),
    ])
