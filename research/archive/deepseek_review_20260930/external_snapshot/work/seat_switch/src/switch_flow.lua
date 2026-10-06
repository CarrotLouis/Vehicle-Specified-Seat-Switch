-- Drives one ownership-aware switch: plan, acquire, mutate, sync, hand back.
--
-- Everything native is injected, so the sequencing and the failure rules are the
-- only things this module owns and they can be tested without a game:
--
--   capture()               -> state | nil, reason      read the ownership seam
--   plan(state, target)     -> plan  | nil, reason      ownership_state.plan
--   acquire(state, plan)    -> ok    | nil, detail      ask plan.acquire for authority
--   granted(state, plan)    -> bool                     do we hold it now
--   mutate(state, target)   -> ok    | nil, detail      the local seat change and pose
--   sync(state, target)     -> ok    | nil, detail      snapshot/transition/notifications
--   handback(state, plan)   -> ok    | nil, detail      return authority to plan.handback
--   now()                   -> seconds
--
-- Two rules matter more than the happy path. A borrowed chassis must never be left
-- held, so any failure after the grant attempts a hand-back before reporting. And a
-- hand-back that fails is retried rather than abandoned, which is why that outcome
-- has its own terminal state instead of being folded into 'failed'.
--
-- Phases: idle -> (acquire) -> await_grant -> mutate -> sync -> (handback) -> done,
-- plus failed and handback_pending. The keep branch has no acquire or hand-back.
return function(deps)
    local log = deps.log or function() end
    local timeout = deps.timeout or 6
    local flow = {phase = 'idle'}

    function flow:set_phase(phase, detail)
        self.phase = phase
        log('multipeer_phase '..phase..(detail and (' '..tostring(detail)) or ''))
    end

    function flow:clear()
        self.phase = 'idle'; self.state = nil; self.plan = nil; self.target = nil
        self.started = nil; self.reason = nil; self.acquired = false
    end

    -- True while a switch is in flight, including a hand-back still being retried.
    -- The caller must not start another switch while this holds.
    function flow:busy() return self.phase ~= 'idle' end

    -- Report a failure, handing back first if we are holding the chassis. Only the
    -- capture and granted checks decide whether a hand-back is needed; a hand-back
    -- request is never issued blind.
    function flow:abort(why)
        self.reason = why
        if self.plan and self.plan.handback and self.acquired then
            local fresh = deps.capture()
            if fresh and deps.granted(fresh, self.plan) then
                local ok, detail = deps.handback(fresh, self.plan)
                if not ok then
                    self:set_phase('handback_pending', tostring(detail))
                    return 'handback_pending'
                end
                log('multipeer_abort_handed_back '..tostring(why))
            else
                log('multipeer_abort_nothing_held '..tostring(why))
            end
            self.acquired = false
        end
        self:set_phase('failed', why)
        return 'failed'
    end

    -- true on success, or nil plus a reason. A start that fails acquires nothing,
    -- so the flow is left idle and there is nothing to clean up.
    function flow:start(target)
        if self.phase ~= 'idle' then return nil, 'busy' end
        local state, why = deps.capture()
        if not state then return nil, why or 'state_unavailable' end
        local plan, reason = deps.plan(state, target)
        if not plan then return nil, reason or 'no_plan' end
        if plan.handback == state.selfpeer then return nil, 'handback_to_self' end
        if plan.handback and plan.acquire ~= plan.handback then return nil, 'inconsistent_plan' end
        self.state, self.plan, self.target, self.started = state, plan, target, deps.now()
        self.reason, self.acquired = nil, false
        if plan.acquire then
            local ok, detail = deps.acquire(state, plan)
            if not ok then
                self.state, self.plan, self.target = nil, nil, nil
                return nil, detail or 'acquire_failed'
            end
            self.acquired = true
            self:set_phase('await_grant', plan.action)
        else
            self:set_phase('mutate', plan.action)
        end
        return true
    end

    -- One step. Returns true while the flow is still running, or the phase name once
    -- it settles.
    function flow:advance()
        if self.phase == 'await_grant' then
            if deps.granted(self.state, self.plan) then
                self:set_phase('mutate', self.plan.action)
                return true
            end
            if deps.now() - self.started > timeout then return self:abort('grant_timeout') end
            return true
        end
        if self.phase == 'mutate' then
            local ok, detail = deps.mutate(self.state, self.target)
            if not ok then return self:abort('mutate_failed_'..tostring(detail)) end
            self:set_phase('sync', self.plan.action)
            return true
        end
        if self.phase == 'sync' then
            local ok, detail = deps.sync(self.state, self.target)
            if not ok then return self:abort('sync_failed_'..tostring(detail)) end
            if self.plan.handback then
                self:set_phase('handback', self.plan.action)
                return true
            end
            self:set_phase('done', self.plan.action)
            return 'done'
        end
        if self.phase == 'handback' then
            local ok, detail = deps.handback(self.state, self.plan)
            if not ok then
                self:set_phase('handback_pending', tostring(detail))
                return 'handback_pending'
            end
            self.acquired = false
            self:set_phase('done', self.plan.action)
            return 'done'
        end
        return self.phase
    end

    -- Called once per frame. A settled flow is reported exactly once and in the same
    -- call: 'done' on success, or the failure reason string. A failed hand-back is
    -- reported as 'handback_pending' and retried until it succeeds.
    function flow:update()
        if self.phase == 'idle' then return 'idle' end
        if self.phase == 'handback_pending' then
            local ok, detail = deps.handback(self.state, self.plan)
            if not ok then
                log('multipeer_handback_retry '..tostring(detail))
                return 'handback_pending'
            end
            self.acquired = false
            self:set_phase('done', self.plan.action)
        else
            local outcome = self:advance()
            if outcome == true then return self.phase end
            if outcome == 'failed' then
                local why = self.reason or 'failed'
                self:clear()
                return why
            end
            if outcome ~= 'done' then return outcome end
        end
        self:clear()
        return 'done'
    end

    return flow
end
