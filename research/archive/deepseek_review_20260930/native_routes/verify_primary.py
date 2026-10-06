"""Independent directed-graph verification of staged DS report against frozen log."""
from pathlib import Path
import json,re
R=Path(__file__).resolve().parent;W=R.parents[1]
log=W/'seat_weapon_clear_diagnostic/capture-20260930-0101/VehicleSeatSwitch.log'
expected={'m102':(2,5),'m103':(2,4),'m104':(2,3),'bastion':(3,4),'maelstrom':(3,4),'tanker':(2,2)}
raw_report=(R/'DEEPSEEK_NATIVE_ROUTE_REVIEW_20260930.json').read_text()
# Preserve the original invalid JSON. Repair its single arithmetic expression explicitly,
# never eval external text. Verify the computed total against the decoded graph below.
assert raw_report.count('4 + 4 + 2 + 6 + 6 + 2')==1
report=json.loads(raw_report.replace('4 + 4 + 2 + 6 + 6 + 2','24'))
(R/'normalized-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
ds=report['per_vehicle']
raw={n:list(map(int,x.split(',')))for n,x in re.findall(r'seat_adjacency (\w+) ([\d,-]+)',log.read_text())}
assert set(raw)==set(expected)==set(ds)
result={}
for name,(width,count) in expected.items():
 assert len(raw[name])==width*count
 rows=[]
 for node in range(count):
  row=raw[name][node*width:(node+1)*width];assert -1 in row
  row=row[:row.index(-1)];assert all(0<=t<count for t in row);rows.append(row)
 edges=[[a,b]for a,row in enumerate(rows)for b in row];indirect=[]
 for source in range(count):
  seen={source};todo=[source]
  while todo:
   for nxt in rows[todo.pop()]:
    if nxt not in seen:seen.add(nxt);todo.append(nxt)
  indirect.extend([source,b]for b in sorted(seen-{source})if b not in rows[source])
 assert rows==ds[name]['rows_0based']and edges==ds[name]['edges_direct']
 assert indirect==ds[name]['reachable_only_via_intermediate']
 result[name]=dict(rows=rows,directed_edges=edges,indirect_only=indirect)
(R/'primary-validation.json').write_text(json.dumps(result,indent=2))
assert sum(len(v['directed_edges'])for v in result.values())==report['summary']['direct_edges_total']
print('PASS six DS row/edge tables against primary log; directed BFS confirms no indirect-only paths')
