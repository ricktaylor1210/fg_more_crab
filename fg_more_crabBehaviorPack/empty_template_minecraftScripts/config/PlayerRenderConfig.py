# -*- coding: utf-8 -*-

RegisterGeometry = [
    # 渲染几何体键:渲染几何体名称
    # {"dummy": "geometry.dummy"}
]
RegisterMaterial = [
    # 材质键:材质名称
    # {"Material": "Material"}
]
RegisterTexture = [
    # 贴图键:贴图路径
    # {"dummy": "textures/entity/dummy"}
]
RegisterRenderController = [
    # 渲染控制器名称:渲染控制器条件
    # {"controller.render.dummy": "query.mod.dummy>0"}
]
RegisterSoundEffect = [
    # 音效资源Key:音效资源名称
    # {"dummy": "music.dummy.dummy"}
]
RegisterParticleEffect = [
    # 特效资源Key:特效资源名称
    # {"dummy": "fg:dummy"}
]
RegisterActorScriptAnimate = [
    # 动画/动画控制器名称:动画/动画控制器控制表达式
    # {"dummy_re_controller": "query.mod.dummy>0"}

]
RegisterAnimationController = [
    # 动画控制器键:动画控制器名称
    # {"dummy_ac": "controller.animation.dummy.dummy"}
]
RegisterAnimation = [
    # 动画键:动画名称
    # {"animation.dummy.dummy": "animation.dummy.dummy"}

]


def HasRenderData():
    return any([
        RegisterGeometry,
        RegisterMaterial,
        RegisterTexture,
        RegisterRenderController,
        RegisterSoundEffect,
        RegisterParticleEffect,
        RegisterActorScriptAnimate,
        RegisterAnimationController,
        RegisterAnimation
    ])
