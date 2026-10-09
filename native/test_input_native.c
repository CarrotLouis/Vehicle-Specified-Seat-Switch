#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef struct {uint32_t binding,target,held_count,held[255];} Item;
typedef struct {uint64_t sequence,tick,generation;uint32_t binding,source,target,message;} Record;
extern int VSSI_start(HWND);extern int VSSI_arm(const Item*,uint32_t,uint32_t,uint64_t,uint64_t);
#define VSSI_arm(p,n,s,e) VSSI_arm(p,n,s,e,11)
extern uint32_t VSSI_stop(void),VSSI_health(void),VSSI_suppressed(uint32_t),VSSI_drain(Record*,uint32_t),VSSI_dropped(void);
extern uint64_t vssi_test_now;extern int vssi_test_focus,vssi_test_cursor;extern uint8_t vssi_test_keys[256];
#define CHECK(x) do{if(!(x)){fprintf(stderr,"failed line %d: %s\n",__LINE__,#x);exit(1);}}while(0)
static UINT seen_message;static WPARAM seen_w;static LONG forwarded;
static LRESULT CALLBACK original(HWND h,UINT m,WPARAM w,LPARAM l){
 (void)h;(void)l;seen_message=m;seen_w=w;forwarded++;SetLastError(123);return 321;
}
static LRESULT CALLBACK foreign(HWND h,UINT m,WPARAM w,LPARAM l){(void)h;(void)m;(void)w;(void)l;return 654;}
int main(int argc,char **argv){
 (void)argc;WNDCLASSW c={0};c.lpfnWndProc=original;c.hInstance=GetModuleHandleW(NULL);c.lpszClassName=L"VSSInputPrivateTest";CHECK(RegisterClassW(&c));
 HWND h=CreateWindowExW(0,c.lpszClassName,L"",0,0,0,1,1,NULL,NULL,c.hInstance,NULL);CHECK(h);CHECK(!IsWindowVisible(h));
 CHECK(VSSI_start(NULL)==-3);
 CHECK(VSSI_start(h)==0&&VSSI_health()==0);CHECK(VSSI_start(h)==-1);
 Item i={.binding=256*4+VK_RBUTTON,.target=4};CHECK(VSSI_arm(&i,1,1,1200)==0);
 memset(vssi_test_keys,0,256);vssi_test_keys[VK_LCONTROL]=1;vssi_test_keys[VK_RBUTTON]=1;
 LONG n=forwarded;SetLastError(777);CHECK(SendMessageW(h,WM_RBUTTONDOWN,MK_CONTROL|MK_RBUTTON,0)==0);CHECK(forwarded==n);CHECK(VSSI_suppressed(VK_RBUTTON));
 Record r[256];CHECK(VSSI_drain(r,256)==1&&r[0].binding==i.binding&&r[0].target==4&&r[0].source==1&&r[0].tick==1000&&r[0].generation==11);
 CHECK(SendMessageW(h,WM_MOUSEMOVE,MK_RBUTTON|MK_LBUTTON|MK_CONTROL,55)==321);CHECK(seen_message==WM_MOUSEMOVE&&seen_w==(MK_LBUTTON|MK_CONTROL));
 CHECK(SendMessageW(h,WM_INPUT,0,55)==321&&seen_message==WM_INPUT); /* raw movement forwarded unchanged */
 /* Removing modifier first must not leak a delayed aim/button-down. */
 vssi_test_keys[VK_LCONTROL]=0;CHECK(SendMessageW(h,WM_RBUTTONDBLCLK,MK_RBUTTON,0)==0);CHECK(VSSI_drain(r,256)==0);
 CHECK(SendMessageW(h,WM_RBUTTONUP,0,0)==0&&!VSSI_suppressed(VK_RBUTTON));vssi_test_keys[VK_RBUTTON]=0;
 /* Unbound/excess modifier, menu, stale descriptor and same-target input pass. */
 n=forwarded;CHECK(SendMessageW(h,WM_RBUTTONDOWN,MK_RBUTTON,0)==321&&forwarded==n+1);
 vssi_test_keys[VK_LCONTROL]=1;vssi_test_keys[VK_LSHIFT]=1;CHECK(SendMessageW(h,WM_RBUTTONDOWN,0,0)==321);vssi_test_keys[VK_LSHIFT]=0;
 vssi_test_cursor=1;CHECK(SendMessageW(h,WM_RBUTTONDOWN,0,0)==321);vssi_test_cursor=0;
 vssi_test_now=1201;CHECK(SendMessageW(h,WM_RBUTTONDOWN,0,0)==321);vssi_test_now=1000;
 CHECK(VSSI_arm(&i,1,4,1200)==0);CHECK(SendMessageW(h,WM_RBUTTONDOWN,0,0)==321);
 CHECK(VSSI_arm(&i,1,1,1200)==0);vssi_test_focus=0;CHECK(SendMessageW(h,WM_RBUTTONDOWN,0,0)==321);vssi_test_focus=1;
 /* Left/right-specific chord matching; both sides refuse a side-only chord. */
 i.binding=VK_RBUTTON+256*8;CHECK(VSSI_arm(&i,1,1,1200)==0);
 vssi_test_keys[VK_RCONTROL]=1;CHECK(SendMessageW(h,WM_RBUTTONDOWN,0,0)==321);vssi_test_keys[VK_RCONTROL]=0;
 CHECK(SendMessageW(h,WM_RBUTTONDOWN,0,0)==0);CHECK(SendMessageW(h,WM_RBUTTONUP,0,0)==0);VSSI_drain(r,256);
 /* Side mouse buttons are correctly handled and preserve non-seat inputs. */
 memset(vssi_test_keys,0,256);i.binding=VK_XBUTTON2;CHECK(VSSI_arm(&i,1,1,1200)==0);
 CHECK(SendMessageW(h,WM_XBUTTONDOWN,MAKEWPARAM(MK_XBUTTON2,XBUTTON2),0)==TRUE);CHECK(VSSI_suppressed(VK_XBUTTON2));
 CHECK(SendMessageW(h,WM_XBUTTONUP,MAKEWPARAM(0,XBUTTON2),0)==TRUE);CHECK(!VSSI_suppressed(VK_XBUTTON2));CHECK(VSSI_drain(r,256)==1);
 /* Keyboard repeat is never a new deferred edge; key-up stays balanced. */
 i.binding='Q'+256;memset(vssi_test_keys,0,256);vssi_test_keys[VK_LSHIFT]=1;CHECK(VSSI_arm(&i,1,1,1200)==0);
 CHECK(SendMessageW(h,WM_KEYDOWN,'Q',(LPARAM)1<<30)==321);
 CHECK(SendMessageW(h,WM_KEYDOWN,'Q',0)==0);CHECK(VSSI_suppressed('Q'));CHECK(SendMessageW(h,WM_KEYDOWN,'Q',(LPARAM)1<<30)==0);
 CHECK(SendMessageW(h,WM_KEYUP,'Q',0)==0);CHECK(VSSI_drain(r,256)==1);
 /* Focus loss clears queued intents and any swallowed held key. */
 CHECK(SendMessageW(h,WM_KEYDOWN,'Q',0)==0);CHECK(SendMessageW(h,WM_KILLFOCUS,0,0)==321);CHECK(!VSSI_suppressed('Q')&&VSSI_drain(r,256)==0);
 CHECK(VSSI_arm(&i,6,1,1200)==-1);CHECK(VSSI_arm(&i,1,1,1301)==-1);Item bad[2]={{.binding=i.binding,.target=3},{.binding=i.binding,.target=4}};CHECK(VSSI_arm(bad,2,1,1200)==-3);
 /* Arbitrary prerequisites are checked at the actual GUI message, not at
    last arming time. Prefix keys remain game inputs under the user's policy. */
 Item free_key={.binding=65536+'W',.target=4,.held_count=1,.held={VK_XBUTTON1}};
 memset(vssi_test_keys,0,256);CHECK(VSSI_arm(&free_key,1,1,1200)==0);
 CHECK(SendMessageW(h,WM_KEYDOWN,'W',0)==321);
 vssi_test_keys[VK_XBUTTON1]=1;
 CHECK(SendMessageW(h,WM_XBUTTONDOWN,MAKEWPARAM(MK_XBUTTON1,XBUTTON1),0)==321);
 CHECK(!VSSI_suppressed(VK_XBUTTON1));
 CHECK(SendMessageW(h,WM_KEYDOWN,'W',0)==0);CHECK(VSSI_suppressed('W'));
 CHECK(VSSI_drain(r,256)==1&&r[0].binding==free_key.binding);
 vssi_test_keys[VK_XBUTTON1]=0;CHECK(SendMessageW(h,WM_KEYUP,'W',0)==0);
 CHECK(SendMessageW(h,WM_KEYDOWN,'W',0)==321);
 vssi_test_keys[VK_XBUTTON1]=1;CHECK(SendMessageW(h,WM_KEYDOWN,'W',(LPARAM)1<<30)==321);
 free_key.binding=131072+'W';free_key.held_count=8;
 for(uint32_t j=0;j<8;j++){free_key.held[j]='A'+j;vssi_test_keys['A'+j]=1;}
 CHECK(VSSI_arm(&free_key,1,1,1200)==0);
 CHECK(SendMessageW(h,WM_KEYDOWN,'W',0)==0);CHECK(VSSI_drain(r,256)==1&&r[0].binding==free_key.binding);
 CHECK(SendMessageW(h,WM_KEYUP,'W',0)==0);vssi_test_keys['E']=0;
 CHECK(SendMessageW(h,WM_KEYDOWN,'W',0)==321);
 free_key.held_count=256;CHECK(VSSI_arm(&free_key,1,1,1200)==-2);
 free_key.held_count=1;free_key.held[0]=256;CHECK(VSSI_arm(&free_key,1,1,1200)==-2);
 free_key.held[0]=VK_CONTROL;CHECK(VSSI_arm(&free_key,1,1,1200)==-2);
 memset(vssi_test_keys,0,256);vssi_test_keys[VK_LSHIFT]=1;
 /* Backpressure fails open rather than consuming an undeliverable key. */
 CHECK(VSSI_arm(&i,1,1,1200)==0);
 for(int j=0;j<256;j++){CHECK(SendMessageW(h,WM_KEYDOWN,'Q',0)==0);CHECK(SendMessageW(h,WM_KEYUP,'Q',0)==0);}
 CHECK(SendMessageW(h,WM_KEYDOWN,'Q',0)==321&&VSSI_dropped()==1);CHECK(VSSI_drain(r,256)==256);
 if(argv[1]&&strcmp(argv[1],"chain-change")==0){
  SetWindowLongPtrW(h,GWLP_WNDPROC,(LONG_PTR)foreign);CHECK(VSSI_health()==2);CHECK(VSSI_stop()==2);CHECK((WNDPROC)GetWindowLongPtrW(h,GWLP_WNDPROC)==foreign);
 }else{CHECK(VSSI_stop()==0);CHECK((WNDPROC)GetWindowLongPtrW(h,GWLP_WNDPROC)==original);CHECK(SendMessageW(h,WM_KEYDOWN,'Q',0)==321);}
 DestroyWindow(h);puts("PASS private hidden-window input priority: chord/side/mouse, no repeat, raw movement unchanged, latches, focus/menu/expiry/refusal, ring backpressure and callback restoration");return 0;
}
