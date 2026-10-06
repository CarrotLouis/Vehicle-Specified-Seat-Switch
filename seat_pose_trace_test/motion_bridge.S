.text
.macro MOTION_BRIDGE idx
.p2align 4
.globl vssm_bridge\idx
.def vssm_bridge\idx; .scl 2; .type 32; .endef
.seh_proc vssm_bridge\idx
vssm_bridge\idx:
 pushfq
 .seh_stackalloc 8
 push %rax
 .seh_stackalloc 8
 .seh_endprologue
 /* Idle/unrelated calls do no C call, FXSAVE, clock or memory read. */
 cmpl $0,vssm_enabled(%rip)
 je .Lmotion_fast\idx
 cmpl vssm_actor(%rip),%ecx
 jne .Lmotion_fast\idx
 pop %rax
 popfq
 jmp vssm_full\idx
.Lmotion_fast\idx:
 pop %rax
 popfq
 jmp *vssm_originals+(\idx*8)(%rip)
.seh_endproc
.p2align 4
.seh_proc vssm_full\idx
vssm_full\idx:
 pushfq
 .seh_stackalloc 8
 push %rax
 .seh_stackalloc 8
 push %rcx
 .seh_stackalloc 8
 push %rdx
 .seh_stackalloc 8
 push %r8
 .seh_stackalloc 8
 push %r9
 .seh_stackalloc 8
 push %r10
 .seh_stackalloc 8
 push %r11
 .seh_stackalloc 8
 sub $0x228,%rsp
 .seh_stackalloc 0x228
 .seh_endprologue
 fxsave64 0x20(%rsp)
 lea 0x228(%rsp),%rcx
 mov $\idx,%edx
 call vssm_capture
 fxrstor64 0x20(%rsp)
 add $0x228,%rsp
 pop %r11
 pop %r10
 pop %r9
 pop %r8
 pop %rdx
 pop %rcx
 pop %rax
 popfq
 jmp *vssm_originals+(\idx*8)(%rip)
.seh_endproc
.endm
MOTION_BRIDGE 0
MOTION_BRIDGE 1
