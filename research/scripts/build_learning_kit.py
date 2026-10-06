"""Bundle authored learning material, no game captures or third-party code.

The small renderer supports the Markdown subset used in this authored guide.
Only explicitly selected files enter the ZIP (no recursive workspace dump).
"""
from pathlib import Path
import hashlib
import html
from html.parser import HTMLParser
import json
import re
import shutil
from urllib.parse import unquote, urlsplit
import zipfile

WORK = Path(__file__).resolve().parent
PROJECT = WORK.parent
OUT = PROJECT / 'outputs/Vehicle-Specified-Seat-Switch-Learning'
OUT.mkdir(parents=True, exist_ok=True)
selected = {
    '先读这里.txt', '从零制作载具换座MOD.md', '项目时间线与证据.md',
    'tools/summarize_network_log.py', 'tools/test_summarize_network_log.py',
}
index = []


def include(source, relative):
    target = OUT / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    selected.add(relative)
    index.append({'file': relative, 'original': source.relative_to(PROJECT).as_posix(),
                  'sha256': hashlib.sha256(target.read_bytes()).hexdigest()})


for source in sorted((WORK / 'seat_switch/src').glob('*.lua')):
    include(source, 'source/gameplay/' + source.name)
for source in sorted((WORK / 'seat_switch/tests').iterdir()):
    if source.is_file() and source.suffix in ('.lua', '.py', '.sha256'):
        include(source, 'source/gameplay_tests/' + source.name)
for name in ('build_gameplay.py', 'build_diagnostic.py', 'generate_profile.py', 'package_release.py'):
    include(WORK / 'seat_switch' / name, 'source/gameplay_build/' + name)
for name in ('platform.lua', 'sampler.lua', 'recorder.lua', 'entry.lua', 'build.py',
             'test_sampler.lua', 'test_recorder.lua', 'test_entry.lua', 'README_English.txt'):
    include(WORK / 'seat_network_diagnostic' / name, 'source/network_diagnostic/' + name)
include(WORK / 'seat_network_diagnostic/README_双人诊断步骤.txt', '双人诊断步骤.txt')
for name in ('reverse.py', 'emulate_seats.py', 'extract_lua.py', 'extract_animation.py',
             'parse_animation.py', 'inspect_dump.py', 'research_multiplayer.py', 'run_lua.py'):
    include(WORK / name, 'source/research/' + name)
for name in ('test_diagnostic_package.cjs', 'test_variant_package.cjs'):
    include(WORK / 'packaging_research' / name, 'source/packaging/' + name)
for name in ('STATE_0.2.1_20260923.md', 'STATE_0.2.2_20260923.md', 'STATE_0.2.3_20260923.md',
             'STATE_RELEASE_0.2.3_20260923.md', 'STATE_NETWORK_DIAGNOSTIC_20260924.md'):
    include(WORK / name, 'history/' + name)
for name in ('RESEARCH_STATE.md', 'RESEARCH_25327279.md'):
    include(WORK / 'reverse' / name, 'history/' + name)
include(WORK / 'multiplayer-research/RESEARCH_20260924.md', 'history/RESEARCH_MULTIPLAYER_20260924.md')
with zipfile.ZipFile(PROJECT / 'outputs/Vehicle-Specified-Seat-Switch-0.2.3.zip') as release:
    for name, relative in [('KEYS_按键清单.txt', '按键清单.txt'),
                           ('Source/SeatSwitch.ini.example', 'SeatSwitch.ini.example')]:
        body = release.read(name)
        (OUT / relative).write_bytes(body)
        selected.add(relative)
        index.append({'file': relative, 'original': 'outputs/Vehicle-Specified-Seat-Switch-0.2.3.zip::' + name,
                      'sha256': hashlib.sha256(body).hexdigest()})


def inline(text):
    pattern = r'`([^`]+)`|\[([^\]]+)\]\(([^)]+)\)|\*\*([^*]+)\*\*'
    output, position = [], 0
    for match in re.finditer(pattern, text):
        output.append(html.escape(text[position:match.start()]))
        code, label, href, bold = match.groups()
        if code is not None:
            output.append('<code>' + html.escape(code) + '</code>')
        elif label is not None:
            output.append('<a href="' + html.escape(href, quote=True) + '">' + html.escape(label) + '</a>')
        else:
            output.append('<strong>' + html.escape(bold) + '</strong>')
        position = match.end()
    output.append(html.escape(text[position:]))
    return ''.join(output)


def render(source):
    lines = source.splitlines()
    body, nav, i = [], [], 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith('```'):
            language, block = line[3:].strip(), []
            i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                block.append(lines[i]); i += 1
            assert i < len(lines), 'unclosed code fence'
            body.append('<figure class="code"><figcaption>' + html.escape(language or 'text') +
                        '</figcaption><pre><code>' + html.escape('\n'.join(block)) + '</code></pre></figure>')
            i += 1
            continue
        heading = re.match(r'^(#{1,6}) (.+)$', line)
        if heading:
            level, title = len(heading[1]), heading[2]
            anchor = 'section-' + str(len(nav) + 1) if level == 2 else 'heading-' + str(i)
            body.append(f'<h{level} id="{anchor}">{inline(title)}</h{level}>')
            if level == 2:
                nav.append(f'<a href="#{anchor}">{inline(title)}</a>')
            i += 1
            continue
        if line.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                cells = [x.strip() for x in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?', x) for x in cells):
                    tag = 'th' if not rows else 'td'
                    rows.append('<tr>' + ''.join(f'<{tag}>{inline(c)}</{tag}>' for c in cells) + '</tr>')
                i += 1
            body.append('<div class="table-wrap"><table><thead>' + rows[0] + '</thead><tbody>' +
                        ''.join(rows[1:]) + '</tbody></table></div>')
            continue
        item = re.match(r'^(\d+\. |[-*] )(.+)$', line)
        if item:
            tag = 'ol' if item[1][0].isdigit() else 'ul'
            items = []
            while i < len(lines):
                item = re.match(r'^(\d+\. |[-*] )(.+)$', lines[i])
                if not item:
                    break
                items.append('<li>' + inline(item[2]) + '</li>'); i += 1
            body.append(f'<{tag}>' + ''.join(items) + f'</{tag}>')
            continue
        paragraph = [line]; i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r'^(#|```|\||\d+\. |[-*] )', lines[i]):
            paragraph.append(lines[i]); i += 1
        body.append('<p>' + inline(' '.join(paragraph)) + '</p>')
    return '\n'.join(body), '\n'.join(nav)


CSS = '''
:root {color-scheme:light;--ink:#24282b;--sub:#626970;--line:#d9ddda;--gold:#8c7025;--paper:#fcfcf8}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:26px}
body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.85 "Microsoft YaHei","Segoe UI",sans-serif}
a{color:#3b6176;text-decoration:none}a:hover{text-decoration:underline}code{font-family:Consolas,monospace;font-size:.88em}
.layout{max-width:1500px;margin:auto;display:grid;grid-template-columns:264px minmax(0,1fr)}
nav{position:sticky;top:0;height:100vh;overflow:auto;padding:30px 22px;border-right:1px solid var(--line);font-size:13px;background:#f1f2ed}
nav strong{display:block;color:var(--gold);letter-spacing:1px;font-size:12px;margin-bottom:14px}
nav a{display:block;color:#454e54;padding:6px 0;line-height:1.5}
main{min-width:0;padding:42px 52px 70px;max-width:1120px}
.eyebrow{color:var(--gold);font-size:12px;letter-spacing:2px;font-weight:700}
.meta{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0 24px}.meta span{font-size:12px;padding:3px 10px;border:1px solid var(--line);border-radius:3px}
.start{padding:18px 22px;border-left:4px solid var(--gold);background:#f2f1e7;margin-bottom:24px}
.start p{margin:0}.start a{display:inline-block;margin-right:20px;font-size:14px}
h1{font-size:32px;line-height:1.45;font-weight:700;margin:26px 0 22px;letter-spacing:-.5px}
h2{font-size:23px;line-height:1.5;margin:48px 0 20px;padding-top:15px;border-top:1px solid var(--line)}
h3{font-size:18px;line-height:1.55;margin:30px 0 13px}p{margin:13px 0}li{padding:3px 0}
p code,td code,li code{background:#eceeea;padding:2px 4px;border-radius:3px;overflow-wrap:anywhere}
.table-wrap{overflow-x:auto;margin:20px 0}table{width:100%;border-collapse:collapse;font-size:14px;line-height:1.65}
th,td{text-align:left;vertical-align:top;border:1px solid var(--line);padding:11px 13px}th{background:#eceee8;font-weight:600}tr:nth-child(even){background:#f5f6f1}
.code{margin:20px 0;border:1px solid #d5d9d5;border-radius:4px;background:#eff1ec;overflow:hidden}
figcaption{font:11px/1.4 Consolas,monospace;text-transform:uppercase;color:#666e6b;padding:7px 14px;border-bottom:1px solid #d5d9d5}
pre{padding:15px;margin:0;overflow-x:auto;line-height:1.7;font-size:14px}pre code{font-size:inherit}footer{margin-top:45px;color:var(--sub);font-size:13px;border-top:1px solid var(--line);padding-top:15px}
@media(max-width:900px){.layout{display:block}nav{position:static;height:auto;padding:18px 24px}nav a{display:inline-block;margin-right:16px}main{padding:26px 22px}h1{font-size:27px}}
@media print{nav,.start,.meta{display:none}.layout{display:block}main{padding:0;max-width:none}body{font-size:10pt;background:white}h2,h3{break-after:avoid}pre{white-space:pre-wrap;font-size:9pt}.table-wrap{overflow:visible}a{color:inherit;text-decoration:underline}}
'''

guide = OUT / '从零制作载具换座MOD.md'
body, navigation = render(guide.read_text(encoding='utf-8'))
page = '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
page += '<title>从零制作载具换座 MOD · Vehicle Specified Seat Switch</title><style>' + CSS + '</style></head><body><div class="layout">'
page += '<nav aria-label="章节目录"><strong>VEHICLE SPECIFIED SEAT SWITCH</strong>' + navigation + '</nav><main>'
page += '<div class="eyebrow">开发记录 · 学习范本</div><div class="meta"><span>2026-09-24</span><span>Build 25327279</span><span>Loader v16 / API 1</span><span>含失败尝试与验证边界</span></div>'
page += '<div class="start"><p>普通版与单人加强版已有实测；联机跨区仍在研究，坦克自旋仍未解决。</p><a href="双人诊断步骤.txt">本轮双人诊断步骤 →</a><a href="项目时间线与证据.md">项目时间线 →</a><a href="从零制作载具换座MOD.md">可编辑 Markdown →</a><a href="先读这里.txt">目录与依赖说明 →</a></div>'
page += body + '<footer>记录实际证据与验证范围。历史笔记的旧结论以最新用户实测为准。</footer></main></div></body></html>'
html_path = OUT / '从零制作载具换座MOD.html'
html_path.write_text(page, encoding='utf-8')
selected.add(html_path.name)


class LinkCheck(HTMLParser):
    def __init__(self):
        super().__init__(); self.links = []; self.ids = set(); self.h2 = 0

    def handle_starttag(self, tag, attrs):
        props = dict(attrs)
        if 'id' in props:
            assert props['id'] not in self.ids, 'duplicate heading id'
            self.ids.add(props['id'])
        if tag == 'a':
            self.links.append(props['href'])
        if tag == 'h2':
            self.h2 += 1


check = LinkCheck(); check.feed(page)
for href in check.links:
    parts = urlsplit(href)
    if parts.scheme:
        assert parts.scheme == 'https'
    elif parts.path:
        assert (OUT / unquote(parts.path)).is_file(), href
    else:
        assert parts.fragment in check.ids, href
assert check.h2 == 16
(OUT / 'SOURCE_INDEX.json').write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding='utf-8')
selected.add('SOURCE_INDEX.json')
destination = PROJECT / 'outputs/Vehicle-Specified-Seat-Switch-Learning.zip'
with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as package:
    for relative in sorted(selected):
        file = OUT / relative
        assert file.is_file(), relative
        package.write(file, relative)
with zipfile.ZipFile(destination) as package:
    assert package.testzip() is None
    assert len(package.namelist()) == len(selected)
    assert all(not name.endswith(('.bin', '.dmp', '.dll', '.pyc')) for name in package.namelist())
report = {'file': str(destination), 'files': len(selected), 'bytes': destination.stat().st_size,
          'sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
          'guide_sections': check.h2, 'checked_html_links': len(check.links)}
(WORK / 'learning-kit-validation.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
