# Arxo through Nix

Binary packaging for `law` and `law-lsp`: Linux x86_64 and macOS Apple Silicon.
The source template has `release.json = null`: no CLI release is currently
pinned. It deliberately refuses to build until a verified candidate is exported.
This is not a claim of publication in nixpkgs or an existing `arxo-nix` repository.

## Prepare a release (product checkout)

Download both `law-VERSION-TARGET.tar.gz` archives and their `.sha256` sidecars,
or use artifacts of `build-cli-release.yml`. Then run:

```sh
python3 apps/delivery/nix/prepare.py --archives /path/to/archives \
  --version 0.2.4 --repository arxohq/law-releases --out /tmp/arxo-nix-candidate
```

The output must not exist. The exporter verifies archive checksums, file names,
public composition, version, target and binary hashes/sizes. It exports only
the recipe, lock, README and release pin; no source checkout or private data.
The version above is an example, not an available release.

## Build and install an exported candidate

Install Nix and enable `nix-command` and `flakes`. From the exported directory:

```sh
nix flake check --no-update-lock-file
nix run .#law -- version
nix profile install .#law
```

Both binaries enter PATH. Once the exported files have been published in a
public repository, replace `.` with its flake URL (for example,
`github:arxohq/arxo-nix` if that repository is created). The archive URLs in
`release.json` must also be anonymously accessible. An authenticated GitHub
download is not evidence of public availability.

Use `path:/absolute/export/path` when testing untracked files inside a Git
checkout; Git flakes omit untracked files.

## Validation and updates

`build-cli-release.yml` prepares the candidate and builds it on both native
platforms before publishing release assets. CI overrides only `src` with the
verified local archive, since the public URL does not exist before release.
It then runs `smoke.py` outside the checkout: create/check a case and perform
an LSP initialize/shutdown exchange. After publication, repeat `nix flake check`
without a source override to verify the actual public downloads.

Linux uses `autoPatchelfHook` and the Nix C/C++ runtime; missing dependencies
fail the build rather than being ignored. ELF fixups can change binary hashes.
The original manifest is preserved as
`share/arxo/upstream-law-dist-manifest.json`, describing upstream bytes, not
patched store binaries. `law version` reports the installed binary's own hash.

For each release regenerate the candidate from both new archives. No mutable
`latest` URLs are used. `flake.lock` pins nixpkgs and its NAR hash, initially
copied from NixOS/nix's upstream lock (nixos-26.05, revision
`c3eea5b2156db11c7eeeada3dc737711255b253e`); update deliberately and retest both
platforms. A binary cache, nixpkgs submission and a NixOS service module are
optional later steps.

Local exporter tests (no Nix or network required):

```sh
python3 -m unittest discover -s apps/delivery/nix -p 'test_*.py'
```
