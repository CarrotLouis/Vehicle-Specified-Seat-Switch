# Vehicle Specified Seat Switch

[English](README.md) | 简体中文

《绝地潜兵 2》载具指定座位切换模组：保持在车内，用自定义按键切换到指定空座。目标已被队友占用或预留时，拒绝切换。支持 M-102 机枪 FRV、M-103 补给 FRV、M-104 喷火 FRV、TD-220 Bastion MK XVI、TD-110 Maelstrom 和特殊任务油罐车。

加强版支持单人和多人，使用者可以是房主或客机，其他队友无需安装。只有希望使用本功能的玩家需要安装。

## 当前版本与安装

当前修订为 **0.4.1**，源码位于 [`seat_release_041`](seat_release_041)。安装包由作者自行发布到本仓库 Releases。本仓库不提交 `outputs` 中的安装包，也不提交游戏原始文件、模块转储、采集日志、下载工具或本机登录信息。

**0.4.0 已有用户报告 GameGuard 强制关闭游戏，应升级至 0.4.1。** 此次退出前，日志记录到开启性能监控屏蔽；用户随后尝试切换版本。退出前未记录加强版生效，不能仅凭这轮日志证明版本切换是原因。0.4.1 完整移除了监控屏蔽的游戏指令修改及其选项，不提供绕过或修改 GameGuard 的功能。新包仍需实机复测，不能保证任何模组组合均被反作弊接受。

安装步骤：

1. 完全退出游戏，启用 [Bingus Shared Loader](https://github.com/CowboyBingus/BingusSharedLoader)。菜单依赖要求 v18 或以上。
2. 启用 [ModOptionsMenu](https://github.com/CowboyBingus/ModOptionsMenu) 和 [ModBindingsMenu](https://github.com/CowboyBingus/ModBindingsMenu)，可以使用 Vanilla Plus Megapack 中的对应选项，每个菜单只安装一份。
3. 将 0.4.1 ZIP 整包导入 Arsenal，启用模组并重新部署。禁用旧换座诊断包及其他换座控制模组。
4. 启动后在舰船上等待约 30 秒，完成初始化。
5. 在游戏选项的 MODS 页选择 Vehicle Specified Seat Switch，设置版本和按键策略。

## 普通版与加强版

安装的是完整加强版运行时，首次默认普通版。普通版仅通过 Lua 座位权限表限制可用组合；加强版解除这些分组限制。两者使用相同的常驻控制器、适配器和联机接口，版本切换不重新加载模组，也不改写游戏指令。已有换座请求会先完成，再应用新选择。

| 车型 | 默认键位 | 普通版 | 加强版 |
| --- | --- | --- | --- |
| M-102 Gunner FRV | F1 驾驶、F2 副驾、F3 后左、F4 后右、F5 机枪 | 前排互换、后排互换 | 上述所有空座之间切换 |
| M-103 Supply FRV | F1 驾驶、F2 副驾、F3 后左、F4 后右 | 前排互换、后排互换 | 上述所有空座之间切换 |
| M-104 Incinerator FRV | F1 驾驶、F2 副驾、F3 喷火 | 前排互换 | 上述所有空座之间切换 |
| Bastion / Maelstrom | F1 驾驶、F2 炮位、F3 左乘员、F4 右乘员 | 炮位与两乘员位互换 | 上述所有空座之间切换 |
| 任务油罐车 | F1 驾驶、F2 炮位 | 两座互换 | 两座互换 |

普通版同样检查空位，不能切换到队友的座位。换座前停止射击、探头并等待角色坐稳。同车队友可以继续驾驶。

## 两套独立按键配置

“按键策略”可随时在以下来源之间切换，首次默认 INI。配置各自保存，互不覆盖。

**VehicleSeatSwitch.ini**：首次初始化生成在 `%APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini`。支持各车型独立键位、键盘、五个鼠标键以及组合键，例如 `CTRL+1`、`SHIFT+Q`、`CTRL+SHIFT+MOUSE4`。编辑文件后重启游戏读取；游戏内更换策略不需要重启。完整清单见 [`KEYS_按键清单.txt`](seat_release_041/KEYS_按键清单.txt)。

**ModBindingsMenu**：在游戏鼠标／键盘或手柄按键配置的 MODS 页设置本模组的五个座位动作。原生自动分配动作初始未绑定，需要自行指定按键。座位编号适用于所有车型，第三个动作同时对应后左／左乘员／M-104 喷火位。支持该菜单允许的设备和触发类型，不复制 INI 的组合键规则。

INI 策略生效时，原生按键列表第一行显示当前来源和切换提示。仍可编辑保存菜单键位，但只有选中菜单策略才生效。界面文字跟随游戏文本语言，内置 13 种语言。

F2–F5 仍可能与游戏性能监控冲突。0.4.1 撤下了会修改游戏指令的屏蔽方案；目前建议改用专用组合键，例如在 INI 中配置 `CTRL+1` 至 `CTRL+5`。如果原生菜单键也用于射击、探头或移动，可能需要释放该操作后完成跨区换座。

## 验证与反馈

换座核心依据此前的单人、双人房主／客机、三人加入／退出、多车、行驶换座和坦克退出测试。四人已有离线检查，尚未完成四人实机验证。

0.4.1 的常驻控制器、普通版权限限制、菜单接口、13 种语言和两套键位隔离已有离线回归。本次 GameGuard 退出的确切检测原因未获确认；修订包仍需要一次单人短测，确认菜单切换、普通版限制与加强版功能。不要把离线回归视为反作弊实机兼容验证。

反馈请提供游戏／模组版本、版本选择、按键策略、房主／客机、车型和操作步骤，以及 `%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs` 内相关日志：

- `VehicleSeatSwitch.log`
- `BingusSharedLoader.log`
- `ModOptionsMenu.log`
- `ModBindingsMenu.log`

如再次出现 GameGuard 提示，记录提示文字、错误码与大致时间。无需发送密码、令牌或整个进程内存。

## 源码与学习资料

此仓库以原工作目录 `work` 为根目录。当前源码在 `seat_release_041`，旧版本和失败尝试保存在历史 `seat_*` 目录及 `STATE_*` 文档中。阅读 [`STATE_MENU_REVISION_20261007.md`](STATE_MENU_REVISION_20261007.md)、[`STATE_RELEASE_0.3.0_20261005.md`](STATE_RELEASE_0.3.0_20261005.md) 和 [`TASK_STATE.md`](TASK_STATE.md) 可了解当前状态及研究路径。历史文件不都代表当前可安装版本。

为兼容现有测试路径，克隆到名为 `work` 的目录，在其父目录执行：

```text
git clone https://github.com/CarrotLouis/Vehicle-Specified-Seat-Switch.git work
python -X utf8 work/seat_release_041/make_locales.py
python -X utf8 work/seat_release_041/build_native.py
python -X utf8 work/seat_release_041/build.py
python -X utf8 work/seat_release_041/validate.py
python -X utf8 work/seat_release_041/build.py --package
```

需要 Windows、Python 3、x64 MinGW GCC 和游戏的 LuaJIT 运行库。可用 `VSS_GCC`、`VSS_OBJDUMP`、`HD2_LUA51_DLL` 指定工具路径。完整研究回归还需要未提交的本地游戏采集与菜单源码；缺少这些资料时不会伪报完整通过。通过与源码摘要匹配的检查后，打包脚本将 ZIP 写入仓库外的 `outputs`。

第三方来源见 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)。后续对话产生的新源码、测试和文档按项目约定同步至 GitHub；Releases 由作者管理。
