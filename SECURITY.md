# Native helpers / 原生辅助模块

Vehicle Specified Seat Switch contains two small native Windows DLLs. They are shipped inside the ZIP and the Lua resource; the addon extracts its own embedded bytes when needed. It does not download these DLLs. The binaries are **unsigned**. Their public hashes establish which packaged bytes were loaded, not publisher identity or a guarantee that an arbitrary download is safe.

| Helper | Purpose | Static dependencies |
| --- | --- | --- |
| `VSSTransport-<SHA256>.dll` | Synchronously handles a matching pending seat-reservation reply inside the game; forwards other replies to the original handler. | Kernel32, MSVCRT |
| `VSSInputPriority-<SHA256>.dll` | Coordinates selected seat keys on the current game's own GUI thread/window. | Kernel32, User32 |

Native callbacks can execute on game threads outside Lua's update. These helpers keep that thread-sensitive work in C/assembly. They are not standalone applications. The transport uses the game's existing session; the helpers do not open external network connections. The input bridge checks the current process ID and a nonzero window thread ID before attaching; it does not install a desktop-wide keyboard hook. Matched input events stay in a bounded memory queue, and are not recorded as a general keystroke log. Release transport packet recording is compiled out.

## Files and verification

Runtime cache:

```text
%LOCALAPPDATA%\CowboyBingus\Helldivers2\VehicleSeatSwitch\Native\
```

`VehicleSeatSwitch.log` records each loaded helper's full path, size and SHA-256. The ZIP also provides the same two binaries openly under `Native/`, `SHA256SUMS.txt`, `NATIVE_HELPERS.json`, and the relevant sources under `Source/`. Nothing in `Native/` is an additional installer or needs to be run manually. Arsenal deploys the addon patch files; the embedded resource creates the native cache.

Before loading, the addon checks the embedded SHA-256, exact size and byte-for-byte agreement of the cached file. Mismatches are refused rather than executed or silently overwritten. It uses a full Unicode path with `LoadLibraryExW` and restricts dependencies to Windows System32. The verified file is held with read-only sharing through loading, final-file reparse points are rejected, and the loaded module path is checked before exported functions are used. It does not change the process-wide DLL search settings or antivirus policies.

The helper references remain valid until game exit because native callbacks can outlive Lua shutdown. Close the game before removing its cached DLLs. Only the two named helper patterns belong to this release; do not delete unrelated files from the loader's log directory. A required cache is recreated from packaged bytes next time the addon needs it.

Sources: `native/native.c`, `native/gate.c`, `native/bridge.S`, `native/input_native.c`; extraction/loading: `src/native_library.lua`. Build and import audits: `scripts/build_native.py`, `scripts/build_input_native.py`, `scripts/audit_native_helpers.py`. Exact binary reproduction depends on matching compiler/linker versions. The input build checks the reproduced file against the embedded bytes.

These checks assume the installed addon package and the Windows account/system are trusted. They do not create a sandbox for arbitrary malicious mods and are not an independent security audit or Authenticode signature. Obtain the addon from the author's release page, and compare against its published hashes.

## 中文说明

本模组包含两个小型 Windows 原生 DLL，分别处理联机换座确认和游戏窗口内的指定换座按键。文件来自安装包内嵌数据，不通过网络下载；DLL 未使用 Authenticode 签名。文件名中的 SHA-256 用于标识内容，不能单独证明发布者身份或任意来源文件的安全性。

运行时文件位于上面的专用 Native 缓存目录。ZIP 的 `Native/` 目录提供相同 DLL，并附哈希清单、用途清单及源码。游戏日志记录实际加载的路径、大小和哈希。

加载前校验内嵌数据的 SHA-256、磁盘文件大小及完整字节，拒绝不一致文件。使用绝对 Unicode 路径，依赖仅从 Windows System32 加载；验证期间保持只读共享句柄，拒绝最终文件的重解析点，并核对加载后的模块路径。

辅助模块仅在游戏进程中使用。按键模块检查窗口所属进程和线程，不安装全桌面键盘钩子；只处理已匹配的换座输入，不记录通用按键日志。联机模块使用游戏现有会话，发行构建不持续记录通信包。辅助模块没有独立外部网络连接、系统启动项或额外进程启动功能。

完全退出游戏后可删除本模组的 DLL 缓存；下次需要时会重新生成。不要删除其他模组的 DLL 或日志。这些校验以可信的安装包和系统环境为前提，不能替代独立安全审计或代码签名。
