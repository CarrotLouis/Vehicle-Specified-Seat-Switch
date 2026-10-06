#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <assert.h>
typedef struct {void **slot;void *target;uint8_t head[32];} Binding;
typedef struct {void **slot;void *target;} Guard;
typedef struct {uint64_t cookie,peer;uint32_t car,avatar,source,target;} GateConfig;
typedef struct {uint64_t cookie,tick,peer;uint32_t car,avatar,source,target,chosen,status,repeats,guard_lost;} GateRecord;
int VSST_start(const Binding *,const Guard *);uint32_t VSST_stop(void),VSST_health(void);
int VSST_gate_arm(const GateConfig *),VSST_gate_finish(uint64_t);uint32_t VSST_gate_active(void),VSST_gate_peek(GateRecord *);
void VSST_gate_shutdown(void);
typedef uint64_t(*Fn)(uint64_t,uint64_t,uint64_t,uint64_t,uint64_t,uint64_t,uint64_t,uint64_t);
static void *slots[3];static volatile LONG forwarded;
__attribute__((noinline))static uint64_t target(uint64_t a,uint64_t b,uint64_t c,uint64_t d,uint64_t e,uint64_t f,uint64_t g,uint64_t h){
 (void)a;(void)b;(void)c;(void)d;(void)e;(void)f;(void)g;(void)h;InterlockedIncrement(&forwarded);return 456;
}
static uint32_t values[3]={4123,4107,2};
static struct {uint32_t type,size;void *data;} args[3]={{1,4,&values[0]},{1,4,&values[1]},{1,4,&values[2]}};
static void receive(uint64_t peer,uint32_t hash,uint32_t count){((Fn)slots[2])(peer,hash,109,(uintptr_t)args,count,6,7,8);}
static DWORD WINAPI worker(void *p){for(int i=0;i<1000;i++)receive((uint64_t)(uintptr_t)p,0x2e986f01,3);return 0;}
int main(int argc,char **argv){
 Binding b[3];Guard g[3];void *refs[3];
 for(int i=0;i<3;i++){slots[i]=(void*)target;b[i].slot=&slots[i];b[i].target=(void*)target;memcpy(b[i].head,(void*)target,32);refs[i]=(void*)target;g[i].slot=&refs[i];g[i].target=(void*)target;}
 assert(VSST_start(b,g)==0);
 GateConfig c={73,222,4123,4107,1,2};GateRecord r;
 assert(VSST_gate_arm(&c)==0);assert(VSST_gate_arm(&c)==-2);
 SetLastError(87);receive(222,0x2e986f01,3);assert(GetLastError()==87);
 assert(forwarded==0&&VSST_gate_peek(&r)==1&&r.status==2&&r.chosen==2&&r.repeats==1);
 if(argc>1&&!strcmp(argv[1],"error-stop")){
  assert(VSST_stop()==16);assert(slots[0]==(void*)target&&slots[1]==(void*)target&&slots[2]!=(void*)target);
  receive(222,0x2e986f01,3);assert(!forwarded&&VSST_gate_peek(&r)==1&&r.repeats==2);
  VSST_gate_shutdown();assert(VSST_stop()==0&&slots[2]==(void*)target);puts("PASS error stop retains exact pending gate; actual shutdown restores slot");return 0;
 }
 if(argc>1&&!strcmp(argv[1],"guard-change")){
  refs[2]=NULL;receive(222,0x2e986f01,3);assert(forwarded==1&&VSST_gate_peek(&r)==1&&r.guard_lost==1);
  assert(VSST_gate_finish(73)==-1);VSST_gate_shutdown();assert(VSST_stop()==4);puts("PASS changed session forwards unrelated new world; stale confirmation cannot authorize writes");return 0;
 }
 assert(VSST_gate_finish(74)==-1&&VSST_gate_active());
 /* All unrelated packets preserve forwarding; no descriptor dereference for
    foreign peer/hash. Wrong width, count, tuple and slot remain unchanged. */
 receive(333,0x2e986f01,3);receive(222,0xa7ece676,3);
 receive(222,0x2e986f01,2);values[0]++;receive(222,0x2e986f01,3);values[0]--;
 values[1]++;receive(222,0x2e986f01,3);values[1]--;values[2]=5;receive(222,0x2e986f01,3);values[2]=2;
 args[1].size=8;receive(222,0x2e986f01,3);args[1].size=4;args[1].type=2;receive(222,0x2e986f01,3);args[1].type=1;
 assert(forwarded==8&&VSST_gate_peek(&r)==1&&r.repeats==1&&r.status==2);
 /* Concurrent matched duplicates cannot lose the ACK through observer-ring
    contention/overflow. The independent single ACK remains readable. */
 HANDLE threads[2]={CreateThread(NULL,0,worker,(void*)(uintptr_t)222,0,NULL),CreateThread(NULL,0,worker,(void*)(uintptr_t)333,0,NULL)};
 WaitForMultipleObjects(2,threads,TRUE,INFINITE);for(int i=0;i<2;i++)CloseHandle(threads[i]);
 assert(forwarded==1008&&VSST_gate_peek(&r)==1&&r.repeats==1001&&r.status==2);
 assert(VSST_gate_finish(73)==0&&!VSST_gate_active());
 receive(222,0x2e986f01,3);assert(forwarded==1009);
 c.cookie=74;assert(VSST_gate_arm(&c)==0);values[2]=4;receive(222,0x2e986f01,3);
 assert(forwarded==1009&&VSST_gate_peek(&r)==1&&r.chosen==4&&r.status==2);
 values[2]=3;receive(222,0x2e986f01,3);assert(VSST_gate_peek(&r)==1&&r.status==4&&VSST_gate_finish(74)==-1);
 VSST_gate_shutdown();c.cookie=75;assert(VSST_gate_arm(&c)==0);receive(222,0xf2a7f3e4,2);
 assert(forwarded==1010&&VSST_gate_peek(&r)==1&&r.status==3&&VSST_gate_finish(75)==0);
 c.source=0;assert(VSST_gate_arm(&c)==-1);c.source=1;c.target=4;assert(VSST_gate_arm(&c)==0);values[2]=4;receive(222,0x2e986f01,3);assert(VSST_gate_peek(&r)==1&&r.status==2&&r.chosen==4);assert(VSST_gate_finish(c.cookie)==0);c.source=4;c.target=1;assert(VSST_gate_arm(&c)==0);values[2]=1;receive(222,0x2e986f01,3);assert(VSST_gate_peek(&r)==1&&r.status==2&&r.source==4);assert(VSST_gate_finish(c.cookie)==0);c.target=5;assert(VSST_gate_arm(&c)==-1);
 assert(VSST_stop()==0);puts("PASS exact ACK/denial/fallback capture, normal forwarding, concurrent repeats, lifecycle and source/target exclusions");return 0;
}
