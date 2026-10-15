#!/usr/bin/env python3
"""Export a standalone Nix candidate from verified public CLI archives. No network."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
import shutil
import tarfile

PLATFORMS = {
    "x86_64-linux": "x86_64-unknown-linux-gnu",
    "aarch64-darwin": "aarch64-apple-darwin",
}
TEMPLATE = Path(__file__).resolve().parent


def inspect_archive(path, version, target):
    digest = hashlib.sha256(path.read_bytes()).digest()
    checksum = path.with_name(path.name + ".sha256").read_text().split()
    if checksum != [digest.hex(), path.name]:
        raise ValueError(f"{path.name}: checksum or filename mismatch")
    with tarfile.open(path, "r:gz") as archive:
        members = archive.getmembers()
        expected = {"law", "law-lsp", "law-dist-manifest.json", "LICENSE", "NOTICE", "THIRD-PARTY-NOTICES.txt"}
        if len(members) != len(expected) or {m.name for m in members} != expected or not all(m.isfile() for m in members):
            raise ValueError(f"{path.name}: expected exactly the binaries, the manifest and the legal files")
        manifest = json.load(archive.extractfile("law-dist-manifest.json"))
        if (manifest.get("tool"), manifest.get("target"), manifest.get("composition")) != (version, target, "public"):
            raise ValueError(f"{path.name}: version, target or public composition mismatch")
        for name in ("law", "law-lsp"):
            member = archive.getmember(name)
            if not member.mode & 0o111:
                raise ValueError(f"{path.name}: {name} is not executable")
            payload = archive.extractfile(member).read()
            actual = {"sha256": hashlib.sha256(payload).hexdigest(), "size": len(payload)}
            if manifest.get("artifacts", {}).get(name) != actual:
                raise ValueError(f"{path.name}: {name} artifact hash/size mismatch")
            if name == "law" and any(manifest.get(k) != v for k, v in actual.items()):
                raise ValueError(f"{path.name}: primary binary hash/size mismatch")
    return "sha256-" + base64.b64encode(digest).decode()


def prepare(archives, version, repository, output):
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9.-]+)?", version):
        raise ValueError("expected a release version, e.g. 0.2.4")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("expected owner/repository")
    if output.exists():
        raise ValueError("output must be a new directory")
    platforms = {}
    for system, target in PLATFORMS.items():
        name = f"law-{version}-{target}.tar.gz"
        matches = list(archives.rglob(name))
        if len(matches) != 1:
            raise ValueError(f"expected exactly one {name}, found {len(matches)}")
        platforms[system] = {
            "url": f"https://github.com/{repository}/releases/download/law-v{version}/{name}",
            "hash": inspect_archive(matches[0], version, target),
        }
    output.mkdir(parents=True)
    for name in ("flake.nix", "flake.lock", "package.nix", "README.md"):
        shutil.copyfile(TEMPLATE / name, output / name)
    (output / "release.json").write_text(json.dumps({"version": version, "platforms": platforms}, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archives", type=Path, required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--repository", default="arxohq/law-releases")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        prepare(args.archives, args.version, args.repository, args.out)
    except (ValueError, OSError, tarfile.TarError) as error:
        parser.exit(1, f"arxo-nix: {error}\n")
