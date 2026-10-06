#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <assert.h>
typedef struct {void **slot;void *target;uint8_t head[32];} Binding;
typedef struct {void **slot;void *target;} Guard;
typedef struct {uint64_t sequence,tick,qpc,caller;uint32_t kind,thread,actor,valid,caller_module,epoch;float values[16];uint64_t reserved;} Record;
int VSSM_start(const Binding*,const Guard*),VSSM_arm(uint32_t,uint32_t,uint32_t);
uint32_t VSSM_stop(void),VSSM_health(void),VSSM_drain(Record*,uint32_t),VSSM_disarm(void);
uint64_t VSSM_dropped(void);extern int vssm_test_fail_slot;
typedef uint64_t(*Fn)(uint64_t,uint64_t,uint64_t,uint64_t,uint64_t,uint64_t,uint64_t,uint64_t);
#define TARGET(n) __attribute__((noinline)) uint64_t target##n(uint64_t a,uint64_t b,uint64_t c,uint64_t d,uint64_t e,uint64_t f,uint64_t g,uint64_t h){DWORD err=GetLastError();SetLastError(err+1);return a+3*b+5*c+7*d+11*e+13*f+17*g+19*h+n;}
TARGET(0) TARGET(1)
__attribute__((noinline)) double floating(uint32_t a,double b,double c,double d,double e,double f){return a+2*b+3*c+4*d+5*e+6*f;}
static void *slots[2];static volatile LONG running=1,failures;
static DWORD WINAPI worker(void *arg){
 int i=(int)(uintptr_t)arg;
 while(running){SetLastError(50);Fn f=(Fn)InterlockedCompareExchangePointer(&slots[i],NULL,NULL);uint64_t v=f(1,2,3,4,5,6,7,8);if(v!=454+(uint64_t)i||GetLastError()!=51)InterlockedIncrement(&failures);}return 0;
}
int main(int argc,char **argv){
 Binding b[2];Guard g[2];void *refs[2];void *targets[2]={(void*)target0,(void*)target1};Record r[256];
 int fp=argc>1&&!strcmp(argv[1],"float");if(fp)targets[1]=(void*)floating;
 for(int i=0;i<2;i++){slots[i]=targets[i];b[i].slot=&slots[i];b[i].target=targets[i];memcpy(b[i].head,targets[i],32);refs[i]=targets[i];g[i].slot=&refs[i];g[i].target=refs[i];}
 if(argc>1&&!strcmp(argv[1],"rollback")){
  vssm_test_fail_slot=1;assert(VSSM_start(b,g)==101);assert(slots[0]==targets[0]&&slots[1]==targets[1]);puts("PASS motion partial-install rollback");return 0;
 }
 b[0].head[0]^=1;assert(VSSM_start(b,g)==-6);b[0].head[0]^=1;
 refs[1]=NULL;assert(VSSM_start(b,g)==-20);refs[1]=g[1].target;
 assert(VSSM_start(b,g)==0&&VSSM_health()==0);
 if(argc>1&&!strcmp(argv[1],"slot-change")){
  slots[1]=targets[0];assert(VSSM_health()&2);assert(VSSM_stop()==2&&slots[1]==targets[0]);puts("PASS motion foreign slot never overwritten");return 0;
 }
 if(argc>1&&!strcmp(argv[1],"root-change")){
  refs[0]=NULL;assert(VSSM_health()&4);assert(VSSM_arm(1,1,2000)==-1);assert(VSSM_stop()==0);puts("PASS motion changed root prevents arming; static slots safely restored");return 0;
 }
 if(fp){
  typedef double(*D)(uint32_t,double,double,double,double,double);
  SetLastError(50);assert(((D)slots[1])(1,2,3,4,5,6)==91);assert(GetLastError()==50);
  assert(VSSM_arm(1,1,2000)==0);assert(((D)slots[1])(1,2,3,4,5,6)==91);assert(GetLastError()==50);
  assert(((D)slots[1])(2,2,3,4,5,6)==92);assert(VSSM_stop()==0);
  puts("PASS armed, idle and unrelated floating ABI and return");return 0;
 }
 assert(VSSM_arm(0,1,2000)==-1&&VSSM_arm(1,0,2000)==-1&&VSSM_arm(1,1,2501)==-1);
 SetLastError(50);assert(((Fn)slots[0])(1,2,3,4,5,6,7,8)==454&&GetLastError()==51);assert(VSSM_drain(r,256)==0);
 float pose[16];for(int i=0;i<16;i++)pose[i]=(float)i;
 float lin[3]={7,-5,2},ang[3]={0,0,.8f};
 assert(VSSM_arm(0xa0001234,8,2000)==0);
 ((Fn)slots[0])(0xa0001235,(uintptr_t)pose,0,0,5,6,7,8);assert(VSSM_drain(r,256)==0);
 SetLastError(80);((Fn)slots[0])(0xa0001234,(uintptr_t)pose,0,0,5,6,7,8);assert(GetLastError()==81);
 ((Fn)slots[1])(0xa0001234,(uintptr_t)lin,(uintptr_t)ang,0,5,6,7,8);
 assert(VSSM_drain(r,256)==2&&r[0].kind==0&&r[0].valid==1&&r[0].epoch==8&&r[0].actor==0xa0001234);
 assert(!memcmp(r[0].values,pose,64)&&r[1].kind==1&&r[1].valid==3&&!memcmp(r[1].values,lin,12)&&!memcmp(r[1].values+4,ang,12));
 assert(!memcmp(pose,r[0].values,64));
 ((Fn)slots[0])(0xa0001234,1,0,0,5,6,7,8);((Fn)slots[1])(0xa0001234,0,1,0,5,6,7,8);
 assert(VSSM_drain(r,256)==2&&r[0].valid==0&&r[1].valid==0);
 assert(VSSM_arm(0xa0001234,9,1)==0);Sleep(10);((Fn)slots[0])(0xa0001234,(uintptr_t)pose,0,0,5,6,7,8);assert(VSSM_drain(r,256)==0);
 assert(VSSM_arm(0xa0001234,10,2000)==0);VSSM_disarm();((Fn)slots[0])(0xa0001234,(uintptr_t)pose,0,0,5,6,7,8);assert(VSSM_drain(r,256)==0);
 assert(VSSM_arm(0xa0001234,11,2000)==0);
 for(int i=0;i<4200;i++)((Fn)slots[0])(0xa0001234,(uintptr_t)pose,0,0,5,6,7,8);assert(VSSM_dropped()>0);
 while(VSSM_drain(r,256)){}
 HANDLE threads[2];assert(VSSM_arm(1,12,2000)==0);
 for(int i=0;i<2;i++)threads[i]=CreateThread(NULL,0,worker,(void*)(uintptr_t)i,0,NULL);
 Sleep(20);assert(VSSM_stop()==0);Sleep(20);InterlockedExchange(&running,0);
 WaitForMultipleObjects(2,threads,TRUE,INFINITE);assert(!failures);
 for(int i=0;i<2;i++){CloseHandle(threads[i]);assert(slots[i]==targets[i]&&!memcmp(targets[i],b[i].head,32));}
 puts("PASS motion actor filter, windows, immutable args, invalid reads, concurrent ABI/LastError, overflow, static slot restoration");return 0;
}
