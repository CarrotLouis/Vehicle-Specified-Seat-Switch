-- Reads six bounded, image-resident tables after compat resolves their addresses.
-- No native game calls, hooks, writes, entity traversal or network capture.
local M={}
M.ranges={
 {vehicle='m102',rows=10,row=8,seats=5},
 {vehicle='m103',rows=8,row=8,seats=4},
 {vehicle='m104',rows=6,row=8,seats=3},
 {vehicle='bastion',rows=8,row=12,seats=4},
 {vehicle='maelstrom',rows=8,row=12,seats=4},
 {vehicle='tanker',rows=5,row=8,seats=2},
}
function M.extend(profile)
 for _,r in ipairs(M.ranges)do
  local t=assert(profile.tables[r.vehicle],'missing_table')
  assert(t.row==r.row and #t.roles==r.seats,'table_shape_changed')
  t.size=r.row*r.rows -- compat bounds-checks this entire range in the PE image.
 end
 return profile
end
function M.capture(api,game,profile)
 local out={event='entry_tables',schema='seat-entry-tables-v1',tables={},total_bytes=0}
 for _,r in ipairs(M.ranges)do
  local t=assert(profile.tables[r.vehicle])
  assert(t.row==r.row and t.size==r.row*r.rows,'table_shape_changed')
  local a=api.read(game+t.rva,t.size)
  assert(a and #a==t.size,'table_unreadable_'..r.vehicle)
  assert(api.read(game+t.rva,t.size)==a,'table_changed_during_read_'..r.vehicle)
  local values,terminators,ended={},0,false
  for i=1,#a,4 do
   local b,c,d,e=a:byte(i,i+3);local n=b+c*256+d*65536+e*16777216
   if n>=2147483648 then n=n-4294967296 end
   if (i-1)%r.row==0 then ended=false end
   if not ended then assert(n>=-1 and n<r.rows,'table_value_out_of_range_'..r.vehicle)end
   if n==-1 then ended=true end
   values[#values+1]=n
   if i%r.row==r.row-3 then
    assert(ended,'table_row_terminator_changed_'..r.vehicle);terminators=terminators+1
   end
  end
  assert(terminators==r.rows,'table_row_count_changed')
  out.tables[#out.tables+1]={vehicle=r.vehicle,transition=t.transition,rva=t.rva,row=r.row,rows=r.rows,
   seat_count=r.seats,hex=(a:gsub('.',function(c)return string.format('%02x',c:byte())end)),values=values}
  out.total_bytes=out.total_bytes+#a
 end
 assert(out.total_bytes==424,'capture_size_changed')
 return out
end
return M
