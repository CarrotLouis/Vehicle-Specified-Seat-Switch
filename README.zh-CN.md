# Vehicle Specified Seat Switch

[English](README.md) | 简体中文

《绝地潜兵 2》载具指定座位切换模组：保持在车内，用自定义按键切换到指定空座。目标被队友占用或预留时拒绝切换。加强版支持单人和多人，使用者可以是房主或客机，其他队友无需安装。

INI 支持已支持键名的自由组合，包括 `MOUSE4+W`、`Q+E`、`CTRL+MOUSE4+Q`。按住前面的键，再按最后一个键；修改后重启游戏。原生操作冲突由用户自行安排。

## 安装与配置

当前修订为 **0.4.5**，使用统一安装包。

1. 退出游戏，启用 [Bingus Shared Loader](https://github.com/CowboyBingus/BingusSharedLoader) v18 或以上及必需的 [ModOptionsMenu](https://github.com/CowboyBingus/ModOptionsMenu)。
2. 按需启用 [ModBindingsMenu](https://github.com/CowboyBingus/ModBindingsMenu)，每个菜单只安装一份。
3. 将整个 ZIP 导入 Arsenal，启用“安装模组”并部署。禁用旧换座诊断包及其他换座控制模组。
4. 启动后在舰船上等约 30 秒，在游戏选项的 MODS 页选择本模组。

首次默认为普通版、INI 按键策略、性能监控屏蔽关闭。普通／加强版在游戏内切换。未安装 ModBindingsMenu 时，按键策略固定为 INI，菜单不提供其策略选项；以前保存的菜单策略也不会使按键失效。

安装的是完整加强版运行时；普通版通过 Lua 座位权限表限制可用组合。两者共用常驻控制器和联机接口。正在执行的换座先完成，再应用版本或按键来源变化。

| 车型 | INI 默认键位 | 普通版 | 加强版 |
| --- | --- | --- | --- |
| M-102 Gunner FRV | F1 驾驶、F2 副驾、F3 后左、F4 后右、F5 机枪 | 前排互换、后排互换 | 所有空座之间切换 |
| M-103 Supply FRV | F1 驾驶、F2 副驾、F3 后左、F4 后右 | 前排互换、后排互换 | 所有空座之间切换 |
| M-104 Incinerator FRV | F1 驾驶、F2 副驾、F3 喷火 | 前排互换 | 所有空座之间切换 |
| Bastion / Maelstrom | F1 驾驶、F2 炮位、F3 左乘员、F4 右乘员 | 炮位与两乘员位互换 | 所有空座之间切换 |
| 任务油罐车 | F1 驾驶、F2 炮位 | 两座互换 | 两座互换 |

INI 位于 `%APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini`，首次自动生成并保留已有配置。支持键盘、五个鼠标键和组合键，如 `CTRL+1`、`SHIFT+Q`。修改后重启游戏读取。[完整键位说明](docs/KEYS_按键清单.txt)。

ModBindingsMenu 的五个座位动作初始未绑定，请在游戏原生按键设置的 MODS 页自行绑定。它与 INI 独立保存，切换来源不会覆盖任一配置。INI 生效时，第一个动作标签提示当前来源及切换方式。[详细安装与使用说明](docs/README_中文.txt)。

## 游戏内选项

在 MODS 选项页选择普通版或加强版、独立的按键策略和性能监控快捷键屏蔽（默认关闭）。文本跟随游戏内的语言设置。

ModBindingsMenu 当前公开接口使自动分配的动作初始未绑定，请自行设置为“按下 F1-F5”或其他键位。项目的研究进度和验证记录单独放在 [STATUS](docs/STATUS.md)。

## 原生辅助模块

本模组包含两个未签名的原生 DLL，处理联机换座确认和游戏窗口内的指定换座输入。它们从 ZIP 内嵌数据释放，校验后缓存到 `%LOCALAPPDATA%\CowboyBingus\Helldivers2\VehicleSeatSwitch\Native`。安装包提供对应 DLL 和 SHA-256 清单，源码在本仓库公开；用途、校验及信任边界见 [SECURITY.md](SECURITY.md)。

## 工程目录

| 目录 | 内容 |
| --- | --- |
| `src/` | 当前 Lua 功能、菜单、按键及接口契约 |
| `native/` | 接收门和按键辅助模块源码 |
| `tests/` | 当前回归测试及自编夹具 |
| `scripts/` | 构建、校验、打包和 Git 同步工具 |
| `docs/` | 玩家文档、架构、当前状态及历史记录 |
| `examples/` | INI 示例 |
| `research/archive/` | 保留的历史实验、失败尝试和基线 |
| `research/scripts/` | 保留的历史分析脚本 |
| `build/`、`local_data/`、`vendor/` | 构建产物、私有采集和外部依赖，不提交 Git |

历史记录保留原来的路径和证据。当前构建入口以 `scripts/` 为准，归档实验不全是可安装版本。ZIP 位于仓库外的 `outputs/`，由作者自行发布 Releases。

## 构建与验证

保留现有测试的 `work/` 路径约定，将仓库克隆为名叫 `work` 的目录，在其父目录运行：

```text
python -X utf8 work/scripts/make_locales.py
python -X utf8 work/scripts/build_native.py
python -X utf8 work/scripts/build_input_native.py
python -X utf8 work/scripts/audit_native_helpers.py
python -X utf8 work/scripts/validate.py
python -X utf8 work/scripts/build.py --package
node work/scripts/test_arsenal.cjs outputs/Vehicle-Specified-Seat-Switch-0.4.5.zip
python -X utf8 work/scripts/verify_artifact.py <Arsenal 检查打印的 result.json 路径>
```

需要 Windows、Python 3 和 x64 MinGW GCC；通过 `VSS_GCC`、`VSS_OBJDUMP` 指定编译器，通过 `HD2_LUA51_DLL` 指定游戏的 `bin/lua51.dll`。测试在自己的进程里使用该库，不启动或连接游戏。

完整回归还需要 `local_data/reverse/` 内两份私有采集、`research/archive/menu_integration_research/` 内菜单源码，以及 Arsenal 检查使用的 `research/archive/packaging_research/arsenal_source/`。这些外部或游戏原始数据不放在公开仓库，缺少输入会明确失败。可单独通过 `scripts/run_lua.py` 运行不依赖采集的测试。

打包只接受与当前源码一致的成功验证记录，拒绝覆盖已有 ZIP，不修改实际游戏或管理器配置。

离线回归与实机研究记录见 [STATUS](docs/STATUS.md)。测试不会启动实际游戏。

## 问题反馈与学习

日志目录：`%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs`。提供 `VehicleSeatSwitch.log`，菜单或加载问题附相关 Loader、ModOptionsMenu、ModBindingsMenu 日志，并说明游戏／模组版本、模式、按键策略、车型、房主／客机及复现步骤。

从[当前状态](docs/STATUS.md)、[架构说明](docs/ARCHITECTURE.md)和[已接受的 0.3.0 基线](docs/history/STATE_RELEASE_0.3.0_20261005.md)开始查看项目。[第三方来源](THIRD_PARTY_NOTICES.md)单独记录。作者尚未选择整个项目的许可证；公开可见不等于授权自由再分发全部原创代码。
