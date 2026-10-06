from pathlib import Path
import zipfile,copy,datetime,hashlib
R=Path(__file__).resolve().parent;P=R.parent.parent
old=P/'outputs/Vehicle-Seat-Authority-Diagnostic-0.5.2.zip'
new=P/'outputs/Vehicle-Seat-Authority-Diagnostic-0.5.3.zip'
new.write_bytes(old.read_bytes())
lib=R.parent/'packaging_research/manager-fixture-106ee902-bcaf-489f-bed5-97d13a3962ae/library/Vehicle-Seat-Authority-Diagnostic-0.5.2'
candidate=R/'restored-052.zip'
with zipfile.ZipFile(new)as src,zipfile.ZipFile(candidate,'w',zipfile.ZIP_DEFLATED)as dst:
 for info in src.infolist():
  p=lib/info.filename
  if not p.is_file():continue
  zi=copy.copy(info)
  zi.date_time=tuple(datetime.datetime.fromtimestamp(p.stat().st_mtime).timetuple()[:6])
  dst.writestr(zi,p.read_bytes())
actual=hashlib.sha256(candidate.read_bytes()).hexdigest()
print('restoration candidate',candidate.stat().st_size,actual)
assert actual=='b51703e194f7fbf27fe59b3a86234ae6281a1a5b0ad02b4ed00c746bce66e016'
old.write_bytes(candidate.read_bytes())
print('Original 0.5.2 archive restored BYTE-FOR-BYTE from verified isolated import')
