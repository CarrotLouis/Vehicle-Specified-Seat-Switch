"""One-time migration from the preserved 0.5.0 active harness, keeping 0.5.1 evidence."""
from pathlib import Path
import zipfile
R=Path(__file__).resolve().parent;O=R.parent.parent/'outputs'
with zipfile.ZipFile(O/'Vehicle-Seat-Authority-Diagnostic-0.5.0.zip')as z:
 for name in ('entry.lua','test_entry.lua','README_中文.txt','README_English.txt'):
  path='Source/experiment/'+name if name.endswith('.lua')else name
  text=z.read(path).decode('utf-8').replace('0.5.0','0.5.2')
  if name=='README_中文.txt':text=text.replace('禁用/替换0.4.3及所有旧换座诊断','禁用/替换0.5.1、0.5.0及所有旧换座诊断')+'\n0.5.2修复：将散列桶数与包含碰撞区的总槽位数分开；按真实值区基址读取移交序号，不再把两个32位字段误当成第二个玩家身份。保留完整查找证据。运行时修复和主动往返仍需本轮验证。暂时保持其他FRV换座模组禁用。\n'
  if name=='README_English.txt':text+='\n0.5.2 fixes: distinguish hash bucket count from total initialized slots including overflow; read the serial relative to the actual value payload; stop treating two 32-bit words as a second peer identity. Lookup evidence retained. Runtime repair and active roundtrip still require this test. Keep other FRV seat mods disabled for this test.\n'
  (R/name).write_text(text,encoding='utf-8')
 p=R/'build.py';text=p.read_text()
 begin=text.index("readonly=(R/'observe.lua')")
 end=text.index("source+=(R/'entry.lua')",begin)
 text=text[:begin]+"module('authority_observe',R/'observe.lua');module('authority_probe',R/'probe.lua')\n"+text[end:]
 # Restore the explicitly triggered, one-shot diagnostic manifest.
 old=z.read('Source/experiment/build.py').decode('utf-8')
 manifest=old[old.index("manifest={'Version'"):old.index("files.update({'manifest.json'")]
 manifest=manifest.replace('0.5.0','0.5.2').replace('请替换全部旧诊断。','已修正碰撞区读取边界。请替换全部旧诊断。')
 text=text[:text.index("manifest={'Version'")]+manifest+text[text.index("files.update({'manifest.json'"):]
 text=text.replace("run(R/'test_entry.lua')","run(R/'test_entry.lua');run(R/'test_probe.lua')")
 text=text.replace('Vehicle-Seat-Authority-Lookup-Diagnostic-0.5.1.zip','Vehicle-Seat-Authority-Diagnostic-0.5.2.zip')
 text=text.replace("'prepare.py','probe.lua','test_probe.lua','check_hash.lua','analyze_050_capture.py'","'prepare.py','prepare_052.py','update_051_docs.py','observe_readonly.lua','check_hash.lua','analyze_050_capture.py'")
 p.write_text(text,encoding='utf-8')
p=R/'transport.lua';p.write_text(p.read_text().replace("'0.5.1'","'0.5.2'"))
# Fix values whose old interpretation was invalid: row+8 holds two words, not a peer.
p=R/'probe.lua';s=p.read_text()
s=s.replace('o.selected~=o.owner or ','').replace(' or a.selected~=a.owner','').replace(' or b.selected~=b.owner','')
s=s.replace("summary.owner..'/'..summary.selected..'/'", "summary.owner..'/'")
s=s.replace(' and o.selected==localpeer','').replace(' and o.selected==original','')
p.write_text(s)
p=R/'test_probe.lua';s=p.read_text().replace("function(s,o)o.selected='self'end", "function(s,o)o.owner='unknown'end")
p.write_text(s)
# Existing fixtures now provide both array length and hash bucket count.
p=R/'test_observe_body.lua';s=p.read_text().replace("put(E+0x648,ptr(ROWS)..ptr(0)..le(3)..le(8))", "put(E+0x640,le(8)..le(8));put(E+0x648,ptr(ROWS)..ptr(0)..le(3)..le(8))")
s=s.replace('0x232','0x23a').replace('detail.capacity==8','detail.total_slots==8')
s=s.replace('number(a)==E+0x648 and n==24','number(a)==E+0x640 and n==32')
s=s.replace("setup();put(ROWS+indices[4118]*0x248+8,LOCAL);assert(observer:capture(s).selected==LOCAL)", "setup();put(ROWS+indices[4118]*0x248+8,le(77)..le(88));local fields=observer:capture(s);assert(fields.record_word0==77 and fields.record_word1==88 and fields.owner==FRIEND)")
s=s.replace("put(E+0x648,ptr(ROWS)..ptr(0)..le(c.collision and 2 or 1)..le(c.cap))", "put(E+0x640,le(c.total)..le(c.total));put(E+0x648,ptr(ROWS)..ptr(0)..le(c.collision and 2 or 1)..le(c.cap))")
s=s.replace('c.cap*0x248','c.total*0x248').replace('for i=0,c.cap-1','for i=0,c.total-1')
p.write_text(s)
(O/'Vehicle-Seat-Authority-Diagnostic-0.5.2-测试说明.txt').write_bytes((R/'README_中文.txt').read_bytes())
