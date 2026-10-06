-- Native source release on the NEW actual owner after taking an empty driver.
return function(api,game,p,scope)
 local f=assert(p.functions.release)
 assert(api.read(game+f.rva,#f.bytes)==f.bytes,'acquired_release_code')
 local release=api.ffi.cast('void (*)(void *,uint32_t,int32_t)',game+f.rva)
 return {prepare=function(_,s,slot,grant)
  assert(scope.layout(s)and s.owned and slot==s.node and slot>=1 and slot<#s.profile.roles and grant and grant.source==slot and grant.target==0 and grant:check(),'acquired_release_real_grant_required')
  local used=false
  return function()
   assert(not used and grant:check(),'acquired_release_grant_changed')
   assert(api.read(game+f.rva,#f.bytes)==f.bytes,'acquired_release_code_changed')
   used=true;release(s.collections,s.collection_index,slot)
  end
 end}
end
