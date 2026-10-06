-- Reuse the proven owner-local transaction; add narrowly scoped tank cleanup.
return function(api,game,p,base,pose,personal,emit,driver,scope,tank_factory,steering)
 local function tank(a,g,profile,layout,log)
  local original=tank_factory(a,g,profile,layout,log)
  return {prepare=function(_,s)
   local leave=original:prepare(s)
   local reset=steering:prepare(s)
   return function()leave();reset()end
  end}
 end
 local local_switch=base(api,game,p,pose,personal,emit,driver,scope.layout,tank)
 return {prepare=function(_,s,target)
  assert(scope.direction(s,target)and s.owned and s.player_count>=1 and s.player_count<=4 and s.peer_count==s.player_count,'owned_switch_multiplayer_scope')
  local perform=local_switch:prepare(s,target);local used=false
  return function()assert(not used,'owned_switch_single_use');used=true;perform()end
 end}
end
