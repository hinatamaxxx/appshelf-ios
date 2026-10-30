#!/usr/bin/env python3
"""Package xtool/AppShelf.app (built by ship.sh --device) as an unsigned IPA.

    tools/package-ipa.py [--output DIR]

- removes code signatures that came with prebuilt frameworks (OpenSSL.framework ships Apple-style
  _CodeSignature); the IPA is signed later as a whole
- adds Feather/Resources/ellekit.deb at the app root (kept out of SwiftPM resources: SwiftPM would
  run strip on the ar archive)
- keeps Unix modes in the zip (executables 0755)
"""
import argparse
import hashlib
import plistlib
import shutil
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MACHO = {b"\xcf\xfa\xed\xfe", b"\xca\xfe\xba\xbe", b"\xca\xfe\xba\xbf"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=ROOT / "packages")
    args = ap.parse_args()
    app = ROOT / "xtool" / "AppShelf.app"
    if not (app / "Info.plist").exists():
        raise SystemExit("build first: xtool/AppShelf.app is missing")
    info = plistlib.load(open(app / "Info.plist", "rb"))
    version = info["CFBundleShortVersionString"]
    args.output.mkdir(parents=True, exist_ok=True)
    out = args.output / f"AppShelf-{version}.ipa"
    with tempfile.TemporaryDirectory() as tmp:
        stage = Path(tmp) / "Payload" / "AppShelf.app"
        shutil.copytree(app, stage, symlinks=True)
        for sig in stage.rglob("_CodeSignature"):
            shutil.rmtree(sig)
        for prov in stage.rglob("embedded.mobileprovision"):
            prov.unlink()
        shutil.copy2(ROOT / "Feather" / "Resources" / "ellekit.deb", stage / "ellekit.deb")
        tmp_out = out.with_suffix(".partial")
        with zipfile.ZipFile(tmp_out, "w", zipfile.ZIP_DEFLATED) as z:
            for f in sorted(Path(tmp).joinpath("Payload").rglob("*")):
                if not f.is_file():
                    continue
                zi = zipfile.ZipInfo.from_file(f, f.relative_to(tmp).as_posix())
                with open(f, "rb") as fh:
                    head = fh.read(4)
                zi.create_system = 3
                zi.external_attr = (0o100755 if head in MACHO else 0o100644) << 16
                zi.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(zi, f.read_bytes())
        tmp_out.replace(out)
    print(out, hashlib.sha256(out.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
