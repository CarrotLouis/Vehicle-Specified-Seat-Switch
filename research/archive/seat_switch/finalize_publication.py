from pathlib import Path
import zipfile, hashlib, json, struct, zlib, sys

out = Path(__file__).resolve().parents[2] / 'outputs'
kit = out / 'Vehicle-Specified-Seat-Switch-0.2.3-Publishing'
names = ['m102', 'm103', 'm104', 'tanks', 'tanker', 'cover']
info = {}
for name in names:
    path = kit / 'images' / (name + '.png')
    data = path.read_bytes()
    assert data[:8] == b'\x89PNG\r\n\x1a\n'
    width, height, depth, color = struct.unpack('>IIBB', data[16:26])
    info[name] = {'size': [width, height], 'bit_depth': depth, 'png_color_type': color}
    pos = 8
    while pos < len(data):
        length = struct.unpack('>I', data[pos:pos+4])[0]
        chunk = data[pos+4:pos+8+length]
        crc = struct.unpack('>I', data[pos+8+length:pos+12+length])[0]
        assert zlib.crc32(chunk) & 0xffffffff == crc, name
        pos += length + 12
    assert pos == len(data)
for lang in ['ZH', 'EN']:
    text = (kit / ('Nexus-Description-' + lang + '-BBCode.txt')).read_text(encoding='utf-8')
    assert text.count('[b]') == text.count('[/b]')
    assert 'Vehicle Specified Seat Switch' in text
(kit / 'Images-verification.json').write_text(json.dumps(info, indent=2), encoding='utf-8')
dest = out / ('Vehicle-Specified-Seat-Switch-0.2.3-Publishing-Kit' + ('-' + sys.argv[1] if len(sys.argv) > 1 else '') + '.zip')
with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as z:
    for path in sorted(kit.rglob('*')):
        if path.is_file():
            z.write(path, path.relative_to(kit).as_posix())
with zipfile.ZipFile(dest) as z:
    assert z.testzip() is None
    assert len([n for n in z.namelist() if n.endswith('.png')]) == 6
print(json.dumps({'file': str(dest), 'bytes': dest.stat().st_size, 'sha256': hashlib.sha256(dest.read_bytes()).hexdigest(), 'images': info}, indent=2))
