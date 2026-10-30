#!/usr/bin/env python3
"""Prepare IDeviceKitten/IDevice.xcframework for the Linux (xtool) build.

The published IDevice.xcframework's static library carries Rust's compiler_builtins and the
compiler-rt C objects it compiles. Apple's ld64 lets the SDK's libclang_rt.ios.a win quietly; the
LLVM linker used by xtool reports every one of them as a duplicate symbol. This takes the official
release zip (checked against the checksum IDeviceKit pins), keeps only the iOS device slice, and drops
the archive members whose global symbols all also come from libclang_rt.ios.a.

    tools/prepare-idevice.py            # idempotent; does nothing when the result is current
"""
import hashlib
import io
import plistlib
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

URL = "https://github.com/jkcoxson/idevice/releases/download/v0.1.57/IDevice.xcframework.zip"
SHA256 = "40cd5c769b60d1879a96c9caa27666037f9d5321844addec40ae99727b142d10"
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "IDeviceKitten" / "IDevice.xcframework"
STAMP = OUT / ".prepared"
TOOLS = Path("/usr/lib/swift/usr/bin")
RT = Path.home() / (".swiftpm/swift-sdks/darwin.artifactbundle/Developer/Toolchains/XcodeDefault.xctoolchain"
                    "/usr/lib/swift/clang/lib/darwin/libclang_rt.ios.a")


def defined(archive: Path, arch: str | None = None) -> dict:
    args = [str(TOOLS / "llvm-nm"), "-g", "--defined-only", "-A"] + (["--arch", arch] if arch else []) + [str(archive)]
    out = subprocess.run(args, capture_output=True, text=True, check=True).stdout
    members = {}
    for line in out.splitlines():
        left, _, rest = line.rpartition(": ")
        parts = rest.split()
        if len(parts) < 2 or not left:
            continue
        # llvm-nm -A names archive members as "lib.a(member)" or "lib.a:member" depending on the version.
        member = left[left.rindex("(") + 1:].rstrip(")") if "(" in left else left.rsplit(":", 1)[-1]
        members.setdefault(member, set()).add(parts[-1])
    return members


def main() -> None:
    if STAMP.exists() and STAMP.read_text().strip() == SHA256:
        print("IDevice.xcframework is ready")
        return
    print("downloading", URL)
    with urllib.request.urlopen(URL, timeout=600) as resp:
        data = resp.read()
    if hashlib.sha256(data).hexdigest() != SHA256:
        sys.exit("IDevice.xcframework.zip does not match the pinned checksum")
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            z.extractall(tmp)
        src = next(tmp.rglob("IDevice.xcframework"))
        info = plistlib.load(open(src / "Info.plist", "rb"))
        lib = next(l for l in info["AvailableLibraries"]
                   if l["SupportedPlatform"] == "ios" and not l.get("SupportedPlatformVariant"))
        slice_dir = src / lib["LibraryIdentifier"]
        archive = slice_dir / lib["LibraryPath"]

        rt_syms = set().union(*defined(RT, "arm64").values())
        drop = sorted(m for m, syms in defined(archive).items() if syms and syms <= rt_syms)
        print(f"dropping {len(drop)} members that libclang_rt.ios.a already provides")
        for i in range(0, len(drop), 200):
            subprocess.run([str(TOOLS / "llvm-ar"), "d", str(archive)] + drop[i:i + 200], check=True)

        if OUT.exists():
            shutil.rmtree(OUT)
        OUT.mkdir(parents=True)
        shutil.copytree(slice_dir, OUT / lib["LibraryIdentifier"], ignore=shutil.ignore_patterns("dSYMs"))
        info["AvailableLibraries"] = [lib]
        plistlib.dump(info, open(OUT / "Info.plist", "wb"))
    STAMP.write_text(SHA256 + "\n")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
