-- ABI recovered from Steam build 25327279. This is an in-game TEST adapter.
-- Native code has no recoverable Lua exception boundary; profile and identity
-- checks must complete before calling it. No arbitrary address is accepted.
return function(api,game,profile,pose_factory,trace,driver_factory,mode)
 local ffi=api.ffi
 local n={}
 local transaction=0
 local function mark(stage)
  if trace then pcall(trace,'direct_stage id='..transaction..' stage='..stage) end
 end
 local function bind(name,ctype)
  local p=assert(profile.functions[name],name)
  assert(api.read(game+p.rva,#p.bytes)==p.bytes,'Native signature mismatch: '..name)
  return ffi.cast(ctype,game+p.rva)
 end
 n.next=bind('next','void (*)(void *,uint32_t)')
 n.previous=bind('previous','void (*)(void *,uint32_t)')
 -- Normal never depends on Enhanced's weapon, driver or animation interfaces.
 if mode=='normal' or (profile.capabilities and not profile.capabilities.enhanced) then
  local reason=profile.capabilities and profile.capabilities.enhanced_reason or 'normal_variant'
  function n.available()return false,'enhanced_unavailable '..tostring(reason)end
  function n.prepare()error('enhanced_not_available')end
  function n.direct()error('enhanced_not_available')end
  return n
 end
 local reserve=bind('reserve','void (*)(void *,uint32_t,int32_t)')
 local release=bind('release','void (*)(void *,uint32_t,int32_t)')
 local authority=bind('authority','void (*)(void *,uint32_t,int32_t,uint32_t)')
 local set_role=bind('set_role','void (*)(void *,uint32_t,uint32_t)')
 local restore_seated=bind('restore_seated','void (*)(void *,void *,uint32_t,uint32_t,int32_t,bool)')
 local ownership_busy=bind('ownership_busy','bool (*)(void *,uint32_t)')
 local active_passenger=bind('active_passenger','void (*)(void *,uint32_t,bool)')
 local clear_weapon=bind('clear_vehicle_weapon','void (*)(void *,uint32_t)')
 local restore_personal=bind('restore_personal_weapon','void (*)(void *)')
 local equip_personal=bind('equip_current_personal_weapon','void (*)(void *)')
 local refresh_weapon=bind('refresh_weapon_context','void (*)(void *)')
 local remove_flag=bind('remove_avatar_flag','void (*)(void *,uint32_t)')
 local action=bind('seat_action','float (*)(uint32_t,uint32_t,int32_t,int32_t)')
 local rotation=bind('avatar_rotation','void (*)(void *,uint32_t,bool)')
 local pose
 local driver
 -- The native equip-current helper assumes a live inventory component. Validate
 -- its map, entity identity and selected weapon before any seat mutation.
 local function personal_ready(s)
  local function get(a,n)local b=api.read(a,n);assert(b and #b==n,'Unreadable personal inventory');return b end
  local function ptr(b)local p=api.pointer(b);assert(p,'Invalid personal inventory pointer');return p end
  local function u32(b,o)local a,c,d,e=b:byte(o+1,o+4);return a+c*256+d*65536+e*16777216 end
  local inv=ptr(get(game+profile.globals.inventory,8))
  local h=get(inv+0x28,20);local cap,empty,mult=u32(h,8),u32(h,12),u32(h,16)
  local bit=require('bit')
  assert(cap>0 and cap<=4096 and bit.band(cap,cap-1)==0,'Invalid inventory map')
  local rows=ptr(h)
  local start=tonumber(ffi.cast('uint32_t',ffi.new('uint64_t',s.avatar)*ffi.new('uint64_t',mult)))
  local index
  for j=0,math.min(cap,64)-1 do
   local row=get(rows+8*bit.band(start+j,cap-1),8)
   if u32(row,0)==s.avatar then index=u32(row,4);break end
   if u32(row,0)==empty then break end
  end
  assert(index and index<1024,'Missing personal inventory')
  local owner=ptr(get(ptr(get(inv+0x40,8))+index*8,8))
  assert(owner==s.avatar_address,'Personal inventory identity mismatch')
  local data=get(ptr(get(inv+0x50,8))+index*48,48)
  local slot=u32(data,0x1c);assert(slot<=6,'Invalid personal weapon selection')
  -- Native completion preserves slots 1..4 and falls back to 1 otherwise.
  local offset=({[1]=0,[2]=4,[3]=8,[4]=16})[slot] or 0
  local weapon=u32(data,offset)
  assert(weapon~=0 and weapon~=0xffffffff,'Missing selected personal weapon')
  return true
 end
 local function pose_ready(s)
  if not pose then pose=assert(pose_factory,'Missing pose adapter')(api,profile) end
  return pose.check(s)
 end
 function n.available(s)
  if not s.owned then return false,'vehicle_owned_by_other_peer' end
  -- The first gameplay test must establish local pose/control correctness before
  -- enabling the unverified multiplayer restore protocol. Native group switches
  -- still use the game's normal owner arbitration in either package variant.
  if not profile.direct_solo_only or s.player_count~=1 or s.peer_count>1 then return false,'direct_multiplayer_not_validated' end
  local systems=api.pointer(api.read(game+profile.globals.entities,8))
  if not systems then return false,'missing_engine' end
  -- The native request checks the entity system -> +8 before ownership handoff.
  local engine=api.pointer(api.read(systems+8,8))
  if not engine then return false,'missing_engine' end
  if s.collection_unit~=0x7fff and ownership_busy(engine,s.collection_unit) then
   return false,'vehicle_authority_changing'
  end
  local ok,why=pcall(pose_ready,s)
  if not ok then return false,'direct_pose_unavailable '..tostring(why) end
  return true
 end
 function n.prepare(s)active_passenger(s.seaters,s.avatar,false) end
 function n.direct(s,target)
  assert(type(target)=='number' and target%1==0 and target>=0 and target<#s.profile.roles and target~=s.node and s.occupied[target]==false,'Invalid direct target')
  assert(s.owned and not s.active,'Direct operation requires local vehicle authority')
  assert(profile.direct_solo_only and s.player_count==1 and s.peer_count<=1,'Multiplayer direct restore not validated')
  assert(pose_ready(s))
  local personal_target=s.profile.roles[target+1]==3 or (s.profile.roles[target+1]==1 and
   (s.vehicle=='m102' or s.vehicle=='m103' or s.vehicle=='m104'))
  if personal_target then assert(personal_ready(s)) end
  local neutralize
  if s.profile.roles[s.node+1]==1 then
   if not driver then driver=assert(driver_factory,'Missing driver adapter')(api,game,profile) end
   neutralize=driver.prepare(s)
  end
  -- These routines update the replicated seat mask and linked interactables.
  -- They are only called on the owning peer after fresh occupancy checks.
  transaction=transaction+1
  if neutralize then mark('neutralize_driver_commands');neutralize() end
  mark('reserve_target')
  reserve(s.collections,s.collection_index,target)
  -- The original switch/exit paths stop a mounted weapon before unbinding it.
  -- Both channels matter: tanks use channel 1 for the coaxial gun, and the
  -- Maelstrom driver uses channel 0 for the smoke launcher.
  mark('stop_old_weapon_0')
  clear_weapon(s.avatar_address,0)
  mark('stop_old_weapon_1')
  clear_weapon(s.avatar_address,1)
  mark('restore_personal_weapon')
  restore_personal(s.avatar_address)
  mark('refresh_weapon_context')
  refresh_weapon(s.avatar_address)
  mark('clear_old_seat_flags')
  if s.vehicle=='maelstrom' then remove_flag(s.avatar_address,44) end
  if (s.vehicle=='m102' or s.vehicle=='m104') and s.profile.roles[s.node+1]==2 then
   rotation(nil,s.avatar,true)
  end
  mark('release_old_seat')
  release(s.collections,s.collection_index,s.node)
  mark('set_new_role')
  set_role(s.seaters,s.seater_index,s.profile.roles[target+1])
  -- FRV late-join restore only runs the final gun attachment action. Its
  -- preceding action configures the gunner camera, holster and body modes.
  mark('prepare_target')
  if s.profile.roles[target+1]==2 then
   if s.vehicle=='m102' then action(s.transition,s.avatar,4,target)
   elseif s.vehicle=='m104' then action(s.transition,s.avatar,2,target) end
  end
  mark('restore_target')
  restore_seated(s.seaters,nil,s.avatar,s.collection,target,false)
  if personal_target then
   -- Same sequence as native tank gunner->passenger completion (actions 8/9).
   -- The earlier notification restores visuals only; this restores the current
   -- personal weapon on channel 0, without restoring the old turret/coax.
   -- FRV drivers need it too: their later native driver->passenger transition
   -- assumes this binding survives. Tank drivers retain their own native setup.
   mark('equip_current_personal_weapon')
   equip_personal(s.avatar_address)
   restore_personal(s.avatar_address)
  end
  -- Same callback, before another rendered/simulation frame: replace the entry
  -- clip with its final seated state; never run an exit action or clear collection.
  mark('apply_final_pose')
  n.last_detail=pose.apply(s,target)..' old_weapon_channels_cleared=0,1'
  mark('transfer_authority')
  authority(s.collections,s.collection_index,target,s.avatar)
  mark('complete')
  -- Kept for protocol research only. A late-join snapshot alone does not update
  -- remote role/input state. Never send this incomplete sequence in the test.
 end
 return n
end
