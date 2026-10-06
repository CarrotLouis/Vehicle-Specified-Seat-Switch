-- Full Enhanced runtime stays resident. Normal is a Lua-only permission subset.
-- Calls asking specifically about native adjacency keep the native group rules.
return function(base,current_mode)
 local policy={seats=base.seats}
 function policy.check(requested,vehicle,source,target,occupied)
  if requested=='enhanced'and current_mode()~='enhanced'then requested='normal'end
  return base.check(requested,vehicle,source,target,occupied)
 end
 function policy.direct_allowed()return current_mode()=='enhanced'end
 return policy
end
