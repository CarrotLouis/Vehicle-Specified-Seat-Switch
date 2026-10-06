"""Extract reviewed app backend into workspace for isolated package validation."""
import json
from pathlib import Path
import shutil
import struct

source = Path(r'D:\games\Helldivers2\HD2Arsenal\resources\app.asar')
destination = Path(__file__).resolve().parent / 'arsenal_source'
destination.mkdir(exist_ok=True)
with source.open('rb') as stream:
    sizes = struct.unpack('<4I', stream.read(16))
    header = json.loads(stream.read(sizes[3]))
    data_start = 8 + sizes[1]
    count = total = 0
    def extract_tree(tree, prefix=''):
        global count, total
        for name, item in tree['files'].items():
            relative = prefix + name
            if 'files' in item:
                if relative == 'obfuscated_src' or relative.startswith('obfuscated_src/main') or relative.startswith('node_modules'):
                    extract_tree(item, relative + '/')
                continue
            if not (relative == 'package.json' or relative.startswith('obfuscated_src/main/') or relative.startswith('node_modules/')):
                continue
            target = (destination / relative).resolve()
            assert target.is_relative_to(destination)
            target.parent.mkdir(parents=True, exist_ok=True)
            if item.get('unpacked'):
                shutil.copyfile(source.with_name('app.asar.unpacked') / relative, target)
            elif 'link' not in item:
                stream.seek(data_start + int(item['offset']))
                target.write_bytes(stream.read(item['size']))
            count += 1
            total += item.get('size', 0)
    extract_tree(header)
print(json.dumps({'files_extracted':count,'bytes':total,'destination':str(destination)}))
