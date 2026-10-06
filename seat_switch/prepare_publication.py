from pathlib import Path
import re

root = Path(__file__).resolve().parent
kit = root.parent.parent / 'outputs' / 'Vehicle-Specified-Seat-Switch-0.2.3-Publishing'
kit.mkdir(exist_ok=True)
for path in [root / 'package_release.py', *list((root / 'release_docs').glob('*.txt'))]:
    s = path.read_text(encoding='utf-8')
    s = s.replace('Vehicle Seat Switch', 'Vehicle Specified Seat Switch').replace('Vehicle-Seat-Switch-', 'Vehicle-Specified-Seat-Switch-')
    path.write_text(s, encoding='utf-8')

for language, filename in [('ZH', 'README_中文.txt'), ('EN', 'README_English.txt')]:
    text = (root / 'release_docs' / filename).read_text(encoding='utf-8')
    (kit / f'Nexus-Description-{language}.txt').write_text(text, encoding='utf-8')
    # Conservative BBCode: bold section titles and ordinary paragraphs, no custom HTML.
    lines = text.splitlines()
    sections = {'普通版：单人和联机', '加强版：跨区域换座仅在单人模式生效', '依赖与安装', '自定义按键', '已知问题', '卸载', '致谢',
                'NORMAL — solo and multiplayer', 'ENHANCED — cross-group switching works ONLY in solo play',
                'REQUIREMENTS AND INSTALLATION', 'CUSTOM BINDINGS', 'KNOWN ISSUE', 'UNINSTALLATION', 'CREDITS'}
    lines[0] = '[b]' + lines[0] + '[/b]'
    for i, line in enumerate(lines):
        if line in sections:
            lines[i] = '[b]' + line + '[/b]'
    (kit / f'Nexus-Description-{language}-BBCode.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')

fields = '''Nexus Mods 投稿字段 / Submission fields

Mod name / 名称
Vehicle Specified Seat Switch

Version / 版本
0.2.3

English summary / 英文简介
Switch to a chosen empty vehicle seat without exiting. Custom keyboard, mouse and modifier bindings. Normal supports solo and multiplayer; Enhanced cross-group switching is solo-only. Includes three FRVs, both tanks and the mission fuel tanker.

中文简介
留在车内，一键切换到指定空位。支持键盘、鼠标及组合键自定义，适配三型 FRV、两型坦克和任务油罐车。普通版支持单人和联机；加强版跨区域换座仅限单人。

Main file / 主文件
Vehicle-Specified-Seat-Switch-0.2.3.zip
File display name: Vehicle Specified Seat Switch - Arsenal Package
File version: 0.2.3
File category: Main Files
File description (EN): Arsenal installer containing Normal and Enhanced variants. Choose one during installation. Requires Bingus Shared Loader v16. Enhanced cross-group switching works ONLY in solo play. Includes English and Chinese key guides.
文件说明（中文）：Arsenal 安装包，内含普通版与加强版，安装时二选一。依赖 Bingus Shared Loader v16。加强版跨区域换座仅在单人模式生效。内附中英文按键指南。

Requirements / 依赖
Bingus Shared Loader v16 — https://github.com/CowboyBingus/BingusSharedLoader
Arsenal — 用于此安装包的版本选择和部署 / required for the packaged variant selection and deployment.

Description / 详细介绍
分别提供中英文纯文本和 BBCode 文件；粘贴到对应编辑模式，并使用预览确认排版。可将英文放在上方、中文放在下方。
封面使用 cover.png；图库另附五张座位图。图片展示加强版完整默认键位；普通版的范围以正文为准。图片为座位示意，不是游戏内截图或新增 HUD。

Publication notes / 投稿备注
作者名称使用你自己的 Nexus 账号；许可、转载和捐赠选项由你自行选择，本资料未代为授权。
代码开发有 AI 参与，封面及宣传图为 AI 生成。依照当前 Nexus 规则，本项目应使用 AI-Generated Content（AI 生成代码）及 AI Media（宣传图、封面和页面文案）标签。
已知坦克持续转向问题已在正文披露。本次仅整理发布说明，游戏行为与已测版本一致。
这是一套待投稿资料，未上传或发布到 Nexus Mods。

参考 / References
https://help.nexusmods.com/article/136-best-practices-for-mod-authors
https://help.nexusmods.com/article/28-file-submission-guidelines
'''
(kit / 'Nexus-Submission-Fields.txt').write_text(fields, encoding='utf-8')
print(kit)
