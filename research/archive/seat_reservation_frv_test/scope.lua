-- New protocol scope excludes drivers. Ordinary native routes are separate.
local M={}
local layouts={m102={transition=26,roles={1,3,3,3,2},mount=4,prepare=4},
 m103={transition=27,roles={1,3,3,3}},m104={transition=28,roles={1,3,2},mount=2,prepare=2}}
function M.layout(s)
 local d=s and layouts[s.vehicle]
 if not d or s.transition~=d.transition or not s.profile or s.profile.row~=8 or #s.profile.roles~=#d.roles then return nil end
 for i,role in ipairs(d.roles)do if s.profile.roles[i]~=role then return nil end end
 return d
end
function M.direction(s,target)
 local d=M.layout(s)
 return d and s.node>=1 and s.node<#d.roles and s.node%1==0 and target>=1 and target<#d.roles and target%1==0 and target~=s.node
end
return M
