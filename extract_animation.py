"""Read local slim archives, using documented FileDiver DSAR/DSAA layout."""
from pathlib import Path
import struct, json, sys
ROOT = Path(r'F:\SteamLibrary\steamapps\common\Helldivers 2\data')
OUT = Path(__file__).parent/'animation_resources'
OUT.mkdir(exist_ok=True)
def lz4(data, expected):
    out=bytearray(); i=0
    while i<len(data):
        token=data[i]; i+=1; n=token>>4
        if n==15:
            while True:
                x=data[i];i+=1;n+=x
                if x<255:break
        out+=data[i:i+n];i+=n
        if i==len(data):break
        off=int.from_bytes(data[i:i+2],'little');i+=2
        assert 0<off<=len(out)
        n=(token&15)+4
        if token&15==15:
            while True:
                x=data[i];i+=1;n+=x
                if x<255:break
        block=out[-off:]
        out+=(block*((n+off-1)//off))[:n]
    assert len(out)==expected,(len(out),expected)
    return bytes(out)
class DSAR:
    def __init__(self,path):
        self.path=path;self.file=path.open('rb')
        h=self.file.read(32);assert h[:4]==b'DSAR',path
        count=struct.unpack_from('<I',h,8)[0]
        self.chunks=[struct.unpack('<QQIIBB6x',self.file.read(32)) for _ in range(count)]
        self.offsets={c[0]:i for i,c in enumerate(self.chunks)}
    def chunk(self,i):
        u,c,us,cs,typ,flags=self.chunks[i]
        self.file.seek(c);b=self.file.read(cs)
        return b if typ==0 else lz4(b,us)
index=DSAR(ROOT/'bundles.nxa')
data=b''.join(index.chunk(i) for i in range(len(index.chunks)))
assert data[:4]==b'DSAA'
nb,na=struct.unpack_from('<II',data,12)
def name(off):return data[off:data.index(b'\0',off)].decode()
bundles=[DSAR(ROOT/name(struct.unpack_from('<I',data,24+24*na+4*i)[0])) for i in range(nb)]
archives=[]
for i in range(na):
    size,no,n,eo=struct.unpack_from('<QIIQ',data,24+24*i)
    fn=name(no)
    entries=[struct.unpack_from('<I4xI3xB',data,eo+16*j) for j in range(n)]
    archives.append((fn,size,entries))
def read_archive(ar,start,length):
    fn,size,entries=ar;res=bytearray();end=start+length
    for k,(ao,bo,bi) in enumerate(entries):
        eend=entries[k+1][0] if k+1<len(entries) else size
        if eend<=start or ao>=end:continue
        bundle=bundles[bi];ci=bundle.offsets[bo];pos=ao
        while pos<eend and pos<end:
            us=bundle.chunks[ci][2]
            if pos+us>start:
                b=bundle.chunk(ci)
                res+=b[max(0,start-pos):min(us,end-pos)]
            pos+=us;ci+=1
    assert len(res)==length,(fn,start,length,len(res))
    return bytes(res)

sys.path.insert(0,str(Path(__file__).parent/'BingusSharedLoader/scripts'))
from archive import resource_hash
records=[];seen=set();count=0
state_type=resource_hash('state_machine')
for ar in archives:
 if '.' in ar[0]:continue
 h=read_archive(ar,0,72)
 if h[:4]!=bytes.fromhex('110000f0'):continue
 nt,nf=struct.unpack_from('<II',h,4)
 table=read_archive(ar,72+32*nt,nf*80)
 for i in range(nf):
  fields=struct.unpack_from('<7Q6I',table,i*80);nh,th,off=fields[:3];sz=fields[7]
  if th!=state_type or nh in seen:continue
  seen.add(nh);count+=1
  b=read_archive(ar,off,sz)
  if struct.pack('<I',0xe86f3c8c) not in b:continue
  path=OUT/(f'{nh:016x}.state_machine.main');path.write_bytes(b)
  records.append(dict(archive=ar[0],name=f'{nh:016x}',size=sz));print(records[-1],flush=True)
(OUT/'index.json').write_text(json.dumps(records,indent=2));print('Done',count,len(records))
