from pathlib import Path
import zipfile,struct,datetime,hashlib,json
R=Path(__file__).resolve().parent;p=R/'restored-052.zip';data=p.read_bytes()
target='b51703e194f7fbf27fe59b3a86234ae6281a1a5b0ad02b4ed00c746bce66e016'
with zipfile.ZipFile(p)as z:infos=z.infolist();central=z.start_dir
print('timestamps',set(i.date_time for i in infos),'entries',len(infos))
for hours in (0,-8,8,-1,1,-12,12):
 for seconds in (0,-2,2,-4,4):
  out=bytearray(data);off=central
  for info in infos:
   t=datetime.datetime(*info.date_time)+datetime.timedelta(hours=hours,seconds=seconds)
   dos_time=t.hour<<11|t.minute<<5|t.second//2;dos_date=(t.year-1980)<<9|t.month<<5|t.day
   struct.pack_into('<HH',out,info.header_offset+10,dos_time,dos_date)
   assert out[off:off+4]==b'PK\1\2'
   struct.pack_into('<HH',out,off+12,dos_time,dos_date)
   n,e,c=struct.unpack_from('<HHH',out,off+28);off+=46+n+e+c
  if hashlib.sha256(out).hexdigest()==target:
   (R.parent.parent/'outputs/Vehicle-Seat-Authority-Diagnostic-0.5.2.zip').write_bytes(out)
   print('RESTORED EXACT',hours,seconds);raise SystemExit(0)
for sec in range(0,600,2):
 t=datetime.datetime(2026,9,27,3,0,0)+datetime.timedelta(seconds=sec)
 for split in (len(infos),*range(len(infos))):
  out=bytearray(data);off=central
  for k,info in enumerate(infos):
   d=t+datetime.timedelta(seconds=0 if k<split else 2)
   dt=d.hour<<11|d.minute<<5|d.second//2;dd=(d.year-1980)<<9|d.month<<5|d.day
   struct.pack_into('<HH',out,info.header_offset+10,dt,dd)
   struct.pack_into('<HH',out,off+12,dt,dd)
   n,e,c=struct.unpack_from('<HHH',out,off+28);off+=46+n+e+c
  if hashlib.sha256(out).hexdigest()==target:
   (R.parent.parent/'outputs/Vehicle-Seat-Authority-Diagnostic-0.5.2.zip').write_bytes(out)
   print('RESTORED EXACT chronological timestamps',t,split);raise SystemExit(0)
raise RuntimeError('No timestamp-only match')
