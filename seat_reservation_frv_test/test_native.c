#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <assert.h>
typedef struct {void **slot;void *target;uint8_t head[32];} Binding;
typedef struct {void **slot;void *target;} Guard;
typedef struct {uint64_t sequence,tick,qpc,caller;uint32_t kind,thread,message,count,valid,caller_module,peer_count,peer_valid;uint64_t values[8],peers[8];uint32_t types[8],sizes[8];} Record;
int VSST_start(const Binding*,const Guard*);uint32_t VSST_stop(void),VSST_health(void),VSST_drain(Record*,uint32_t);uint64_t VSST_dropped(void);
extern int vsst_test_fail_slot;
typedef uint64_t(*Fn)(uint64_t,uint64_t,uint64_t,uint64_t,uint64_t,uint64_t,uint64_t,uint64_t);
#define TARGET(n) __attribute__((noinline)) uint64_t target##n(uint64_t a,uint64_t b,uint64_t c,uint64_t d,uint64_t e,uint64_t f,uint64_t g,uint64_t h){DWORD err=GetLastError();SetLastError(err+1);return a+3*b+5*c+7*d+11*e+13*f+17*g+19*h+n;}
TARGET(0) TARGET(1) TARGET(2)
__attribute__((noinline)) double floating(double a,double b,double c,double d,double e,double f){return a+2*b+3*c+4*d+5*e+6*f;}
static void *slots[3];static volatile LONG running=1,failures;
static DWORD WINAPI worker(void *arg){
 int i=(int)(uintptr_t)arg;
 while(running){SetLastError(50);Fn f=(Fn)InterlockedCompareExchangePointer(&slots[i],NULL,NULL);uint64_t v=f(1,2,3,4,5,6,7,8);if(v!=454+(uint64_t)i||GetLastError()!=51)InterlockedIncrement(&failures);}
 return 0;
}
int main(int argc,char **argv){
 Binding b[3];Guard g[3];void *refs[3];void *targets[3]={(void*)target0,(void*)target1,(void*)target2};
 int fp=argc>1&&!strcmp(argv[1],"float");if(fp)targets[2]=(void*)floating;
 for(int i=0;i<3;i++){slots[i]=targets[i];b[i].slot=&slots[i];b[i].target=targets[i];memcpy(b[i].head,targets[i],32);refs[i]=targets[i];g[i].slot=&refs[i];g[i].target=refs[i];}
 if(argc>1&&!strcmp(argv[1],"rollback")){
  vsst_test_fail_slot=2;assert(VSST_start(b,g)==102);for(int i=0;i<3;i++)assert(slots[i]==targets[i]);assert(VSST_stop()==0);puts("PASS partial install rollback restores only own slots");return 0;
 }
 b[0].head[0]^=1;assert(VSST_start(b,g)==-6);b[0].head[0]^=1;
 refs[1]=NULL;assert(VSST_start(b,g)==-20);refs[1]=g[1].target;
 for(int i=0;i<3;i++)assert(slots[i]==targets[i]);
 if(fp){assert(VSST_start(b,g)==0);typedef double(*D)(double,double,double,double,double,double);assert(((D)slots[2])(1,2,3,4,5,6)==91);assert(VSST_stop()==0);puts("PASS six floating arguments and return through assembly bridge");return 0;}
 if(argc>1&&!strcmp(argv[1],"slot-change")){
  assert(VSST_start(b,g)==0);slots[1]=targets[2];assert(VSST_health()&2);assert(VSST_stop()==2);
  assert(slots[0]==targets[0]&&slots[1]==targets[2]&&slots[2]==targets[2]);puts("PASS foreign replacement is detected and never overwritten");return 0;
 }
 if(argc>1&&!strcmp(argv[1],"session-change")){
  assert(VSST_start(b,g)==0);void *old=slots[2];refs[2]=NULL;assert(VSST_health()&8);assert(VSST_stop()==4);
  assert(slots[0]==targets[0]&&slots[1]==targets[1]&&slots[2]==old);
  assert(((Fn)old)(1,2,3,4,5,6,7,8)==456);puts("PASS old session slot untouched; retained bridge still forwards after stop");return 0;
 }
 HANDLE threads[3];for(int i=0;i<3;i++)threads[i]=CreateThread(NULL,0,worker,(void*)(uintptr_t)i,0,NULL);
 assert(VSST_start(b,g)==0);assert(VSST_health()==0);
 Sleep(50);InterlockedExchange(&running,0);WaitForMultipleObjects(3,threads,TRUE,INFINITE);assert(!failures);for(int i=0;i<3;i++)CloseHandle(threads[i]);
 uint32_t values[3]={101,0xffffff01,0x3f800000};
 struct {uint32_t type,size;void *data;} args[3]={{1,4,&values[0]},{0,4,&values[1]},{2,4,&values[2]}};
 uint64_t peers[2]={111,222};uint32_t hash=0xa7ece676;
 SetLastError(80);((Fn)slots[0])(hash,111,(uintptr_t)args,3,5,6,7,8);assert(GetLastError()==81);
 ((Fn)slots[1])(hash,(uintptr_t)peers,2,(uintptr_t)args,3,6,7,8);
 ((Fn)slots[2])(222,hash,383,(uintptr_t)args,3,6,7,8);
 Record rows[256];assert(VSST_drain(rows,256)==3);
 for(int i=0;i<3;i++){assert(rows[i].kind==(uint32_t)i&&rows[i].message==hash&&rows[i].count==3&&rows[i].valid==7);assert(rows[i].values[0]==101&&rows[i].values[1]==1&&rows[i].values[2]==0x3f800000);}
 assert(rows[1].peer_count==2&&rows[1].peer_valid==3&&rows[1].peers[1]==222&&rows[2].peers[0]==222);
 /* Live0.4.0 exit_request: [int4,int4,int4,bool1] was valid_mask7.
    Exercise nonzero true and false to prevent accepting a zero placeholder. */
 uint32_t flag=0xffffff01;
 struct {uint32_t type,size;void *data;} exit_args[4]={{1,4,&values[0]},{1,4,&values[0]},{1,4,&values[0]},{0,1,&flag}};
 ((Fn)slots[2])(222,638550375,84,(uintptr_t)exit_args,4,6,7,8);
 assert(VSST_drain(rows,256)==1&&rows[0].valid==15&&rows[0].values[3]==1&&rows[0].sizes[3]==1);
 flag=0xffffff00;((Fn)slots[2])(222,638550375,84,(uintptr_t)exit_args,4,6,7,8);
 assert(VSST_drain(rows,256)==1&&rows[0].valid==15&&rows[0].values[3]==0);
 exit_args[3].size=2;((Fn)slots[2])(222,638550375,84,(uintptr_t)exit_args,4,6,7,8);
 assert(VSST_drain(rows,256)==1&&rows[0].valid==7);
 exit_args[3].size=1;exit_args[3].type=1;((Fn)slots[2])(222,638550375,84,(uintptr_t)exit_args,4,6,7,8);
 assert(VSST_drain(rows,256)==1&&rows[0].valid==7);
 /* Every newly watched message must pass all three routes; unrelated hashes
    must still be forwarded without entering the diagnostic ring. */
 uint32_t extra_hashes[4]={0xc698216f,0x04506cd6,0x4ad5ae34,0xaee38814};
 exit_args[3].type=0;exit_args[3].size=1;flag=1;
 for(int j=0;j<4;j++){
  uint32_t count=j==2?4:2,mask=(1u<<count)-1;
  ((Fn)slots[0])(extra_hashes[j],111,(uintptr_t)exit_args,count,5,6,7,8);
  ((Fn)slots[1])(extra_hashes[j],(uintptr_t)peers,2,(uintptr_t)exit_args,count,6,7,8);
  ((Fn)slots[2])(222,extra_hashes[j],0,(uintptr_t)exit_args,count,6,7,8);
  assert(VSST_drain(rows,256)==3);
  for(int i=0;i<3;i++)assert(rows[i].message==extra_hashes[j]&&rows[i].kind==(uint32_t)i&&rows[i].count==count&&rows[i].valid==mask);
  if(count==4)assert(rows[2].values[3]==1);
 }
 /* Opaque ownership peer: >2^53, low bits significant, all three routes.
    Unsupported descriptors and placement remain invalid, never dereferenced. */
 uint64_t new_peer=UINT64_C(0xfedcba9876543211);
 struct {uint32_t type,size;void *data;} owner_args[2]={{1,4,&values[0]},{9,8,&new_peer}};
 uint32_t owner_hashes[2]={0xe29b4d18,0xf8a9d630};
 for(int j=0;j<2;j++){
  ((Fn)slots[0])(owner_hashes[j],111,(uintptr_t)owner_args,2,5,6,7,8);
  ((Fn)slots[1])(owner_hashes[j],(uintptr_t)peers,2,(uintptr_t)owner_args,2,6,7,8);
  ((Fn)slots[2])(222,owner_hashes[j],0,(uintptr_t)owner_args,2,6,7,8);
  assert(VSST_drain(rows,256)==3);
  for(int i=0;i<3;i++)assert(rows[i].message==owner_hashes[j]&&rows[i].kind==(uint32_t)i&&rows[i].valid==3&&rows[i].values[1]==new_peer&&rows[i].types[1]==9&&rows[i].sizes[1]==8);
 }
 owner_args[1].size=4;((Fn)slots[0])(owner_hashes[0],111,(uintptr_t)owner_args,2,5,6,7,8);
 assert(VSST_drain(rows,256)==1&&rows[0].valid==1);
 owner_args[1].size=8;owner_args[1].data=(void*)1;((Fn)slots[0])(owner_hashes[0],111,(uintptr_t)owner_args,2,5,6,7,8);
 assert(VSST_drain(rows,256)==1&&rows[0].valid==1);
 owner_args[1].data=&new_peer;((Fn)slots[0])(hash,111,(uintptr_t)owner_args,2,5,6,7,8);
 assert(VSST_drain(rows,256)==1&&rows[0].valid==1);
 owner_args[0].type=9;owner_args[0].size=8;owner_args[0].data=&new_peer;
 ((Fn)slots[0])(owner_hashes[0],111,(uintptr_t)owner_args,2,5,6,7,8);
 assert(VSST_drain(rows,256)==1&&rows[0].valid==2);
 SetLastError(80);uint64_t unrelated=((Fn)slots[0])(0x12345678,111,1,0,5,6,7,8);
 assert(unrelated==target0(0x12345678,111,1,0,5,6,7,8));assert(VSST_drain(rows,256)==0);
 ((Fn)slots[0])(hash,111,1,3,5,6,7,8);assert(VSST_drain(rows,256)==1&&rows[0].valid==0);
 for(int i=0;i<8300;i++)((Fn)slots[0])(hash,111,1,0,5,6,7,8);assert(VSST_dropped()>0);
 InterlockedExchange(&running,1);for(int i=0;i<3;i++)threads[i]=CreateThread(NULL,0,worker,(void*)(uintptr_t)i,0,NULL);
 assert(VSST_stop()==0);Sleep(30);InterlockedExchange(&running,0);WaitForMultipleObjects(3,threads,TRUE,INFINITE);assert(!failures);for(int i=0;i<3;i++)CloseHandle(threads[i]);
 for(int i=0;i<3;i++)assert(slots[i]==targets[i]&&!memcmp(targets[i],b[i].head,32));
 puts("PASS concurrent calls, ABI/LastError, all three record layouts, safe bad reads, bounded overflow, slot restoration and unchanged code");
 return 0;
}
