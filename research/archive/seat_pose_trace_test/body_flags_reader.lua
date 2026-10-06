-- Reproduce the complete native body getter leaf through the already validated
-- physics context. Bounded reads only; no new native calls or state writes.
return function(api,game,p,compat)
 local bit=require('bit');local exe=assert(api.module('helldivers2.exe'))
 local spec=assert(p.pose_watch);local self={}
 local function u32(b,o)local a,c,d,e=b:byte(o+1,o+4);assert(e,'body_flags_short_read');return a+c*256+d*65536+e*16777216 end
 local function get(a,n)local b=api.read(a,n);assert(b and #b==n,'body_flags_unreadable');return b end
 local function ptr(b)return assert(api.pointer(b),'body_flags_pointer')end
 local r=assert(p.motion.refs.physics_worlds);local f=assert(p.engine_functions[r.record]);local at=exe+f.rva+r.offset
 local function reference()
  local b=get(at,r.size);assert((b:sub(1,3):gsub('.',function(x)return string.format('%02x',x:byte())end))==r.opcode_hex,'body_flags_reference')
  local n=u32(b,r.disp);if n>=2^31 then n=n-2^32 end
  return at+r.size+n,b
 end
 function self:read(physical)
  assert(physical and physical.read_only and physical.world>=0 and physical.world<=3 and physical.physics_body_id and
   physical.body_api_methods and physical.body_api_methods['112'],'body_flags_scope')
  local global,b=reference();local root_at=global+physical.world*0xb0
  local root_bytes=get(root_at,8);local root=ptr(root_bytes)
  local vt_bytes=get(root,8);local vt=ptr(vt_bytes)
  local fn_bytes=get(vt+0x70,8);local fn=ptr(fn_bytes)
  assert(tonumber(fn-exe)==physical.body_api_methods['112'],'body_flags_getter_association_changed')
  assert(get(fn,#spec.body_lookup_bytes)==spec.body_lookup_bytes,'body_flags_getter_leaf_changed')
  local array_header=get(root+0x18,12);local array=ptr(array_header);local count=u32(array_header,8)
  local index=bit.band(physical.physics_body_id,0xffffff)
  assert(count>0 and count<=1048576 and index<count,'body_flags_body_index')
  local body=array+index*160;local flags=u32(get(body+0x44,4),0)
  assert(get(at,r.size)==b and get(root_at,8)==root_bytes and get(root,8)==vt_bytes and get(vt+0x70,8)==fn_bytes and
   get(root+0x18,12)==array_header,'body_flags_context_changed')
  return {read_only=true,flags=flags,pose_callback_clears_velocity=bit.band(flags,1)==0,
   body_index=index,body_count=count,getter_via_validated_physics_context=true,
   caution='Flag predicts captured pose callback branch; does not prove callback ran or remote peer motion.'}
 end
 return self
end
