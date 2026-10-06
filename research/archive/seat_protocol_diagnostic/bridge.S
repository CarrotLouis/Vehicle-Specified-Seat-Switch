.text
.macro BRIDGE idx
.p2align 4
.globl vss_bridge\idx
.def vss_bridge\idx; .scl 2; .type 32; .endef
.seh_proc vss_bridge\idx
vss_bridge\idx:
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
 call vss_capture
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
 jmp *vss_originals+(\idx*8)(%rip)
.seh_endproc
.endm
BRIDGE 0
BRIDGE 1
BRIDGE 2
BRIDGE 3
BRIDGE 4
BRIDGE 5
BRIDGE 6
BRIDGE 7
