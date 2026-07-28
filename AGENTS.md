# AGENTS.md

## Scope

- This file is the repository guide for the whole `fg_more_crab` project.
- It applies to everything under this project root unless a narrower child `AGENTS.md` is added later.
- If a child directory later needs its own guide, it should only add narrow project-specific notes and must not contradict this root guide.

## Edit boundaries

- Never modify these paths unless the user explicitly approves it:
  - `.idea/`
  - `.venv/`
  - `.git/`
  - `.github/`
  - `.vscode/`
  - `.editorconfig`
  - `.gitignore`
  - `.gitattributes`
  - `.gitmodules`
  - `.gitkeep`
  - `.DS_Store`
  - `__pycache__/`
- Do not remove `.gitkeep` files unless the directory is being populated with real project files and the removal is necessary.
- Do not edit generated, binary, image, or tool-cache files unless the task explicitly requires it.
- Existing or newly generated `__pycache__/` files must not be edited or added. Clean them only when the user asks, or before committing after verifying the resolved paths are inside this workspace.

## Role

你是本仓库的代码代理，负责阅读上下文、分析问题、提出计划、实施修改、执行验证，并以最小必要改动完成任务。

## Project Overview

- 这是网易基岩 `fg_more_crab` 更多螃蟹玩法包。
- 主要目录：
  - `fg_more_crabBehaviorPack/`
  - `fg_more_crabResourcePack/`
  - `docs/`
- 当前脚本 `ModName` 是 `fg_more_crab`，当前包名分别是 `fg_more_crabBehaviorPack` 和 `fg_more_crabResourcePack`。
- 当前内容使用 `fg:` 命名空间；不要为了风格统一擅自重命名实体 ID、物品 ID、资源 ID、UUID 或脚本路径。需要迁移/改名时，先写清映射和影响面。
- 当前重点链路包括普通生态螃蟹、捕蟹笼、矿物螃蟹、海盗螃蟹、料理、基础装备、负重背包、Boss 结构入口和 Boss 装备基础链路。
- 当前不是单纯资源包；服务端脚本承担矿物蟹吃矿、海盗蟹偷窃/逃跑、Boss 技能、盾牌事件 / 减伤兜底、背包装备和结构放置等运行态行为。

## Current Source Of Truth

- 当前进度和风险优先参考：
  - `README.md`
  - `docs/project_progress_analysis.md`
  - `docs/07_dev_roadmap.md`
- 设计文档入口：
  - `docs/01_mobs_and_ecology.md`
  - `docs/02_crab_normal_variant_design.md`
  - `docs/03_crab_mineral_variant_design.md`
  - `docs/04_systems_and_mechanics.md`
  - `docs/05_items_and_equipment.md`
  - `docs/06_worldgen_and_bosses.md`
  - `docs/crab_showcase.md`
- 如果代码实现和旧文档口径冲突，先确认 `project_progress_analysis.md` 与当前代码，再说明差异；不要直接按旧设计文档覆盖现有实现。
- 行为、资源或路线图发生变化时，按影响范围同步更新相关文档；不要让 docs 再次和实现漂移。

## Key Paths

- 模组配置、名称、版本、system 路径：
  - `fg_more_crabBehaviorPack/fg_more_crabScripts/ModMainConfig.py`
- 模组注册入口：
  - `fg_more_crabBehaviorPack/fg_more_crabScripts/modMain.py`
- 服务端主系统和当前主要业务逻辑：
  - `fg_more_crabBehaviorPack/fg_more_crabScripts/server/ServerMainSystem.py`
- 行为包实体：
  - `fg_more_crabBehaviorPack/entities/`
- 行为包生成规则：
  - `fg_more_crabBehaviorPack/spawn_rules/`
- 行为包物品定义：
  - `fg_more_crabBehaviorPack/netease_items_beh/`
- 行为包配方：
  - `fg_more_crabBehaviorPack/netease_recipes/`
- 行为包掉落表：
  - `fg_more_crabBehaviorPack/loot_tables/entities/`
  - `fg_more_crabBehaviorPack/loot_tables/chests/`
- 行为包动画控制器：
  - `fg_more_crabBehaviorPack/animation_controllers/`
- 资源包客户端实体：
  - `fg_more_crabResourcePack/entity/`
- 资源包模型：
  - `fg_more_crabResourcePack/models/entity/`
  - `fg_more_crabResourcePack/models/netease_models.json`
- 资源包材质、动画、渲染控制器：
  - `fg_more_crabResourcePack/textures/entity/`
  - `fg_more_crabResourcePack/textures/items/`
  - `fg_more_crabResourcePack/textures/item_texture.json`
  - `fg_more_crabResourcePack/textures/terrain_texture.json`
  - `fg_more_crabResourcePack/animation_controllers/`
  - `fg_more_crabResourcePack/animations/`
  - `fg_more_crabResourcePack/render_controllers/`
- 粒子与音效：
  - `fg_more_crabResourcePack/particles/`
  - `fg_more_crabResourcePack/textures/particle/`
  - `fg_more_crabResourcePack/sounds.json`
  - `fg_more_crabResourcePack/sounds/sound_definitions.json`
- 文本本地化：
  - `fg_more_crabResourcePack/texts/zh_CN.lang`
  - `fg_more_crabResourcePack/texts/en_US.lang`
- 包声明：
  - `fg_more_crabBehaviorPack/manifest.json`
  - `fg_more_crabResourcePack/manifest.json`

## API And References

- 官方 API 优先参考：
  - `D:\MeshorioMincecraft\MineCraftProjects\modapi\`
  - `D:\MeshorioMincecraft\MineCraftProjects\modapi\modapi-docs\codex\`
- 游戏本体可参考：
  - `C:\MCStudioDownload\game\MinecraftPE_Netease`
- 除了官方可用 API、本项目已存在模式、当前项目里已经实测或有代码证据支持的模式，不要自己虚构 API。
- 如果一个问题很难解决，可以先加入必要的 `print` 调试日志，然后让用户提供实机日志。
- 如果没有特别提出，普通临时调试优先用 `print`；不要大面积引入或改造 `SetDevelopmentMessage` / `DEVELOPMENT_LEVEL` 调试链路。

## Current Behavior Notes

- 当前服务端脚本只有 server system，`modMain.py` 注册 `ServerMainSystem`，没有客户端 system 注册入口。
- `ServerMainSystem.OnScriptTickServer` 维护 `_tick`，当前按：
  - 每 10 tick 执行活跃螃蟹、Boss 装备玩家、临时方块逻辑；
  - 每 120 tick 执行海盗结构补刷；
  - 每 240 tick 执行 Boss 巢穴补刷。
- Tick 口径以每秒 30 tick 为标准；新增或调整秒级配置时按 `30 * N` 换算，遇到历史 `20 * N` 写法先确认实际行为和回归风险，再做最小范围修正。
- 普通生态螃蟹当前正式变体为 7 个独立实体，`fg:crab`、`fg:crab_help`、`fg:crab_aggressive` 更接近原型 / 兼容 / 特殊用途实体，不要误当成所有普通生态的正式范围。
- 捕蟹笼当前是实体版 MVP，不是 BlockEntity 方案；包含 5 个品质、诱饵、收获、破坏概率、水面浮起和陆地低效捕获。
- 矿物螃蟹当前是 9 个独立矿物实体，服务端脚本负责匹配矿石扫描、靠近、吃矿和类型化 Buff。
- 海盗螃蟹当前是 3 个职业实体，服务端脚本负责偷窃、携物逃跑、击杀返还、受伤集结和海岸藏身处补刷。
- Boss 当前已有 5 个实体、阶段切换、血条、主题技能、P2/P3 场地机制、展示级 `.mcstructure` 巢穴 / 神庙资源、补给宝箱、核心掉落、Boss 装备链路和右键主动技能；结构谜题、终局事件、蟹卵养殖、潮汐入侵和元素盾牌仍是后续扩展。
- 负重背包当前使用普通驯服蟹上的 9 格原生 `container` 第一方案，是否能稳定打开、保存和跨死亡/维度保留需要网易客户端实机确认。
- 蟹壳盾牌已接入自定义盾牌入口、副手、抵挡角度和盾牌事件；`DamageEvent` 潜行/朝向减伤仍作为兜底，副手动画、真实抵挡和物品耐久写回属于需要重点实机回归的高风险链路。

## Work Style

- 先阅读相关代码、配置、资源索引、设计文档和调用链，再下结论。
- 优先定位根因，不只修表面症状。
- 优先做最小充分修改，避免顺手重构。
- 遇到复杂任务、多文件联动任务、影响不明确任务时，先输出计划，再实施。
- 如果存在不确定性，明确写出假设、影响面和风险，不要伪装成确定结论。
- 如果发现工作区有无关改动，不要回滚，先避开。
- 用户没有提出问题就是没问题；不要主动扩散排查并改动无关行为。
- 网易基岩实机测试默认由用户执行；代理负责给出触发条件、预期表现、关键日志和失败 reason，不把本机检查说成实机通过。

## Modification Boundaries

- 当前 `ServerMainSystem.py` 已承载大量业务逻辑。非必要不要做大规模拆分、搬移或重写；优先做局部修正、表驱动补充和小范围防错。
- 非必要不修改 `modMain.py`、manifest UUID、包依赖、目录结构、实体/物品命名空间、关键数据结构。
- 非必要不引入新依赖。
- 非必要不做大规模格式化、命名翻新或资源重排。
- 重构与行为修复尽量分离；如果无法分离，必须明确说明原因和回滚点。
- 新增或调整螃蟹实体时，优先按这条链路补齐：
  - 行为包 entity；
  - 资源包 entity；
  - geometry / texture / animation / animation controller；
  - spawn rule；
  - loot table；
  - item 或 spawn egg 图集入口；
  - `zh_CN.lang` / `en_US.lang`；
  - `ServerMainSystem.py` 中必要的集合、配置表和 handler。
- 新增或调整物品 / 料理 / 装备时，优先按这条链路补齐：
  - `netease_items_beh/`；
  - `netease_items_res/`；
  - `textures/items/`；
  - `textures/item_texture.json`；
  - `netease_recipes/`；
  - `zh_CN.lang` / `en_US.lang`；
  - 必要的服务端事件逻辑。
- 新增或调整 Boss / 巢穴 / 世界生成时，必须同步考虑：实体、生成、掉落、结构/脚本生成、粒子、音效、Boss 装备材料链和文档口径。
- 不要只改脚本而遗漏资源映射；也不要只加资源而没有行为包定义、掉落/生成、文本或服务端逻辑入口。

## Code Principles

- 保持与本项目现有风格一致。
- 这个项目的网易基岩脚本是 Python 2 风格；不要顺手批量改成 Python 3 语法。
- 优先复用现有能力和现有模式，尤其是 `ServerMainSystem.py` 中已有的配置表、helper、事件注册、状态 map 和 guard clause 风格。
- 优先使用配置表修正、资源映射修正、局部防错，而不是扩散式特判。
- 只在以下情况抽取 helper：
  - 同一逻辑会复用至少两次；或
  - 内联逻辑过长，明显影响可读性。
- 优先使用 guard clauses，避免过深嵌套。
- 循环中避免重复读取相同值，应缓存后复用。
- 在 tick、实体扫描、方块扫描、结构生成、伤害事件、Boss 技能、矿物蟹寻矿、海盗蟹偷窃、背包容器和日志 payload 等热路径里，避免大对象 `copy.deepcopy`、重复全量扫描、重复组件创建和大 payload 打印。
- 热路径需要记录信息时，优先保存小型摘要字段，例如 entity id、entity type、player id、item name、tick、position、dimension、reason；不要把完整 inventory、entity list、block scan result 或配置表直接深拷贝进 history / diagnostics / print payload。
- 注释应解释“为什么这样做”“约束是什么”“兼容什么问题”，不要重复代码表意。
- 不要把猜测性兼容逻辑埋成静默行为；必要时写清触发条件。
- 不确定可行或者之前代码没有使用到的接口，可以先尝试写一小段，并加 `TODO` 注释方便后续实机确认。

## Python / Runtime Notes

- 网易基岩运行环境与普通本机 Python 不完全一致，实机表现优先。
- 某些文件包含旧式 `print` 或 Python 2 语法，本机 Python 3 `py_compile` 不能直接作为语法验证依据。
- 修改运行时代码后，能做静态检查时只做最小必要范围；不要把静态检查当成网易基岩实机正确性的替代。
- 涉及组件 API、事件生命周期、实体/玩家 ID、生成规则、AI、动画事件、容器、物品耐久、伤害、效果、粒子、音效、方块替换和结构生成的改动，仍需实机回归。
- 调用网易组件前，先确认创建对象的生命周期、平台差异和入参 ID 是否有效。

## Before Editing

开始改动前，先输出：

1. 你对问题的理解
2. 可能的根因
3. 预计修改的文件
4. 验证方案
5. 风险点

如果任务较大或涉及多个实体 / 多个物品 / 多个模块 / 多个资源索引：

- 先给出分步计划，不要直接大改。
- 说明哪些改动应该合并，哪些应该拆开。
- 说明是否存在配置、资源或文档优先于脚本修复的路径。

## After Editing

完成改动后，必须输出：

1. 实际修改的文件列表
2. 每个文件改了什么
3. 为什么这样改
4. 风险与边界情况
5. 明确回归点
6. 已完成的验证
7. 未完成的验证与原因

不要只说“理论上已修复”；必须给出可以回归的检查点。

## Testing And Verification

- 优先运行最小必要验证范围。
- 新增或更新测试代码前，先判断该测试是否保护重要行为或高风险边界；低风险配置、常量、薄封装和过程性改动优先用静态检查或手动回归点说明。
- 修改 JSON 资源时，优先对被修改 JSON 做解析检查。
- 修改实体时，检查行为包 entity、资源包 entity、模型、贴图、动画控制器、生成规则、掉落表、语言条目是否对齐。
- 修改物品时，检查行为包物品、资源包物品、贴图文件、`item_texture.json`、配方、语言条目是否对齐。
- 修改脚本配置表时，检查对应实体/物品 ID 是否存在于资源和行为定义中，handler 或事件名是否真实存在。
- 修改 tick 调度、实体扫描、方块扫描、结构生成、背包容器、伤害、效果、Boss 技能、矿物蟹寻矿、海盗蟹偷窃/返还、捕蟹笼收获时，必须给出实机回归步骤和预期表现。
- 若无法运行完整验证，必须明确说明原因，并给出精确的手动验证步骤。
- 不得编造测试结果。
- 不得在没有验证依据时声称“已经彻底修复”。

## Regression Points

每次修改后，优先给出：

- 触发条件
- 预期表现
- 对照表现
- 需要重点回归的 entity / item / boss / crab pot / mineral crab / pirate crab / backpack / shield / loot / spawn / resource
- 可能受影响但本次未展开验证的链路

## Output Style

- 结论先行，内容简洁具体。
- 不输出冗长空泛解释。
- 不贴大段代码，除非用户要求。
- 用户要求返回代码时，返回可直接替换的完整方法或完整文件片段，而不是残缺片段。
- 明确区分“已确认事实”“代码推断”“待实机验证项”。

## Recommended Collaboration

- 小步修改，优先补防错和局部修正。
- 改完给出明确回归点，不要只说“理论上已修复”。
- 如果发现工作区有无关改动，不要回滚，先避开。
- 需要网易 API 行为作为依据时，说明参考的是官方 API 哪个位置，并指出本项目中的对应落点。
- 涉及玩法口径变化时，先更新或对齐 docs，再实现对应资源/脚本，避免文档与实现继续漂移。

## Forbidden

- 不看代码就直接下结论。
- 不在证据不足时断言根因。
- 不进行无关的样式清理、命名翻新、目录整理。
- 不把多个无关问题混成一次大改。
- 不编造运行结果、测试结果或日志。
- 不把猜测表述成事实。
- 不在没有充分理由时把配置问题改成脚本特判。
- 不为了“通用性”破坏当前螃蟹、捕蟹笼、Boss 或装备的既有定制逻辑。
- 不擅自重命名当前 `fg:` ID、UUID、资源路径或脚本路径。
- 不把 `ServerMainSystem.py` 作为无边界重构目标；确需拆分时先写计划、边界和回滚点。

