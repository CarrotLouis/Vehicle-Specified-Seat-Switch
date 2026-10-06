载具换座 / Vehicle Specified Seat Switch 0.2.3

留在车内，用快捷键直接切换到指定空位。支持 M-102 Gunner FRV、M-103 Supply FRV、M-104 Incinerator FRV、TD-220 Bastion MK XVI、TD-110 Maelstrom，以及特殊任务油罐车。
两版均检查目标座位，已被队友占用或预留的位置不可切换。

普通版：单人和联机
M-102 / M-103：前排 F1 驾驶、F2 副驾驶；后排 F3 左、F4 右。仅在同一排内互换。
M-104：前排 F1 驾驶、F2 副驾驶。
TD-220 / TD-110：F2 炮位、F3 左乘员、F4 右乘员，仅这三个位之间互换，驾驶位不参与。
任务油罐车：F1 驾驶、F2 炮位。

加强版：跨区域换座仅在单人模式生效
在普通版基础上，允许在下列所有座位之间直接切换，需要载具由本机控制。
M-102：F1 驾驶、F2 副驾驶、F3 后左、F4 后右、F5 机枪。
M-103：F1 驾驶、F2 副驾驶、F3 后左、F4 后右。
M-104：F1 驾驶、F2 副驾驶、F3 喷火。
TD-220 / TD-110：F1 驾驶、F2 炮位、F3 左乘员、F4 右乘员。
任务油罐车：F1 驾驶、F2 炮位。
联机时加强版仅保留普通版的换座范围。说明图展示完整默认键位，普通版仍受上述分组限制。

依赖与安装
需要 Bingus Shared Loader v16：https://github.com/CowboyBingus/BingusSharedLoader
本版本适配 Steam build 25327279 / EXE 1.8.45850.0；后续游戏更新可能需要重新适配。
1. 退出游戏，先安装并启用 Loader。
2. 将 Vehicle-Specified-Seat-Switch-0.2.3.zip 直接导入 Arsenal，在模组选项中选择普通版或加强版，只选一个。
3. 禁用旧版换座包及 Vehicle Seat Diagnostic 诊断包，部署后启动游戏。
4. 更换版本时，退出游戏，在 Arsenal 改选、重新部署，再启动。

自定义按键
首次启动模组后生成：%APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini
两个版本共用此文件；升级保留已有设置。用记事本修改、保存并重启游戏。
支持键盘、鼠标五键（含两个侧键）及 CTRL+1、SHIFT+Q 等组合键。NONE 可禁用单个座位绑定。
完整合法键名、组合规则和冲突说明见本 ZIP 的 KEYS_按键清单.txt；英文见 KEYS_English.txt。
默认 F2/F3/F5 可能同时触发游戏性能面板，建议按自己的游戏设置更换键位。模组不会屏蔽游戏或系统原有快捷键。

已知问题
坦克驾驶时按住 A/D 转向并换座，可能留下持续转向，即使下车也可能继续。建议先松开转向再换座；若发生，重新进入驾驶位并操控可解除。
本次发布整理未改动换座逻辑，该问题尚未修复。

卸载
退出游戏，在 Arsenal 禁用或移除此模组并重新部署。按键文件可以保留。

致谢
CowboyBingus — Bingus Shared Loader；Arsenal 项目 — 模组安装管理。
模组代码开发使用了 AI 辅助；宣传 HUD 图和封面为 AI 生成的座位示意图，并非游戏截图或游戏内新增 HUD。
