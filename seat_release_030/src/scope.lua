-- Native owner reservation / own-owner transaction. Normal routes stay native.
local M={}
local layouts={m102={transition=26,row=8,roles={1,3,3,3,2},frv=true,mount=4,prepare=4},
 m103={transition=27,row=8,roles={1,3,3,3},frv=true},
 m104={transition=28,row=8,roles={1,3,2},frv=true,mount=2,prepare=2},
 bastion={transition=43,row=12,roles={1,2,3,3},tank=true,mount=1},
 maelstrom={transition=44,row=12,roles={1,2,3,3},tank=true,mount=1,smoke=true}}
function M.layout(s)
 local d=s and layouts[s.vehicle]
 if not d or s.transition~=d.transition or not s.profile or s.profile.row~=d.row or #s.profile.roles~=#d.roles then return nil end
 for i,role in ipairs(d.roles)do if s.profile.roles[i]~=role then return nil end end
 return d
end
function M.direction(s,target)
 local d=M.layout(s)
 return d and s.node>=0 and s.node<#d.roles and s.node%1==0 and target>=0 and target<#d.roles and target%1==0 and target~=s.node
end
return M
