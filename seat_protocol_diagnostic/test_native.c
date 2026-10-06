#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
int VSSP_start(void**,const uint8_t*,uint32_t);
int VSSP_stop(void);
uint32_t VSSP_record_size(void),VSSP_drain(void*,uint32_t);
uint64_t VSSP_dropped(void);
uint32_t VSSP_failure(void *);
extern int vssp_test_fail_protect;
typedef uint64_t (*Fn)(uint64_t,uint64_t,uint64_t,uint64_t,uint64_t,uint64_t,uint64_t,uint64_t);
#define TARGET(N) __attribute__((noinline)) uint64_t target##N(uint64_t a,uint64_t b,uint64_t c,uint64_t d,uint64_t e,uint64_t f,uint64_t g,uint64_t h){ __asm__ volatile(".rept 32; nop; .endr"); DWORD err=GetLastError();SetLastError(err+1);return a+3*b+5*c+7*d+11*e+13*f+17*g+19*h+N; }
TARGET(0) TARGET(1) TARGET(2) TARGET(3) TARGET(4) TARGET(5) TARGET(6)
__attribute__((noinline)) double target7(double a,double b,double c,double d,double e,double f){__asm__ volatile(".rept 32; nop; .endr");return a+2*b+3*c+4*d+5*e+6*f;}
static Fn funcs[]={target0,target1,target2,target3,target4,target5,target6};
static volatile LONG running=1,failures;
static DWORD WINAPI worker(void *arg){
 uintptr_t k=(uintptr_t)arg;
 while(running) {
  SetLastError(76);uint64_t v=funcs[1+k%6](1,2,3,4,5,6,7,8);
  if(v!=454+1+k%6 || GetLastError()!=77)InterlockedIncrement(&failures);
 }
 return 0;
}
#include "captured_heads.h"
int main(int argc,char **argv){
 if(argc>1){
  void *targets[8];uint8_t before[8][32];
  for(int i=0;i<8;i++){
   targets[i]=VirtualAlloc(NULL,4096,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE);assert(targets[i]);
   memcpy(targets[i],captured_heads[i],32);memcpy(before[i],targets[i],32);
   DWORD previous;assert(VirtualProtect(targets[i],4096,PAGE_EXECUTE_READ,&previous));
  }
  if(!strcmp(argv[1],"protection-failure")) {
   unsigned char f[64];vssp_test_fail_protect=1;
   assert(VSSP_start(targets,&before[0][0],8)==310);
   assert(VSSP_failure(f)==1);
   uint32_t error,index,rollback;memcpy(&error,f+4,4);memcpy(&index,f+8,4);memcpy(&rollback,f+60,4);
   assert(error==ERROR_ACCESS_DENIED && index==0 && rollback==0);
   for(int i=0;i<8;i++)assert(!memcmp(before[i],targets[i],32));
   assert(VSSP_stop()==0);
   puts("PASS failed protection: original Windows error/target/page recorded, no retry, no entry changed, rollback succeeds");return 0;
  }
  assert(VSSP_start(targets,&before[0][0],8)==0);assert(VSSP_stop()==0);
  for(int i=0;i<8;i++)assert(!memcmp(before[i],targets[i],32));
  puts("PASS actual captured prologue relocation/install/restore for eight functions (bodies never executed)");return 0;
 }
 void *targets[]={target0,target1,target2,target3,target4,target5,target6,target7};uint8_t before[8][32];
 for(int i=0;i<8;i++)memcpy(before[i],targets[i],32);
 before[0][0]^=1;assert(VSSP_start(targets,&before[0][0],8)==-6);before[0][0]^=1;
 for(int i=0;i<8;i++)assert(!memcmp(before[i],targets[i],32));
 HANDLE threads[3];for(uintptr_t i=0;i<3;i++)threads[i]=CreateThread(NULL,0,worker,(void*)i,0,NULL);
 assert(VSSP_start(targets,&before[0][0],8)==0);
 assert(VSSP_record_size()==192);
 for(int j=0;j<10000;j++)for(int i=0;i<7;i++){
  SetLastError(123);assert(funcs[i](1,2,3,4,5,6,7,8)==(uint64_t)(454+i));assert(GetLastError()==124);
 }
 double (*volatile floating)(double,double,double,double,double,double)=target7;
 for(int i=0;i<1000;i++)assert(floating(1.25,2.5,3.75,4.25,5.5,6.75)==102.5);
 assert(VSSP_dropped()>0); /* saturation/contended producer never blocks gameplay */
 unsigned char records[256][192];uint64_t previous=0;uint32_t total=0,n;
 running=0;WaitForMultipleObjects(3,threads,TRUE,INFINITE);
 while((n=VSSP_drain(records,256))!=0){for(uint32_t i=0;i<n;i++){uint64_t seq;memcpy(&seq,records[i],8);assert(seq>previous);previous=seq;}total+=n;}
 assert(total>0 && !failures);
 /* Test allowlisted send descriptor copying, including unreadable argument. */
 uint32_t values[4]={11,22,33,44};struct{uint32_t type,size;uintptr_t value;}d[4];
 for(int i=0;i<4;i++){d[i].type=1;d[i].size=4;d[i].value=(uintptr_t)&values[i];}d[3].value=1;
 funcs[0](0xa7ece676,0x12345678,(uintptr_t)d,4,0,0,0,0);
 assert(VSSP_drain(records,256)==1);
 uint32_t kind,valid;memcpy(&kind,records[0]+40,4);memcpy(&valid,records[0]+56,4);
 assert(kind==0 && valid==7);uint64_t v;memcpy(&v,records[0]+64+16,8);assert(v==33);
 running=1;for(uintptr_t i=0;i<3;i++){CloseHandle(threads[i]);threads[i]=CreateThread(NULL,0,worker,(void*)i,0,NULL);}
 assert(VSSP_stop()==0);running=0;WaitForMultipleObjects(3,threads,TRUE,INFINITE);
 for(int i=0;i<3;i++)CloseHandle(threads[i]);assert(!failures);
 for(int i=0;i<8;i++)assert(!memcmp(before[i],targets[i],32));
 puts("PASS native hooks: signature refusal, original arguments/returns/LastError, six floating args, live concurrent install/disable, ordered drain, saturation, filtered send descriptors, invalid pointer, exact code restoration");
 return 0;
}
