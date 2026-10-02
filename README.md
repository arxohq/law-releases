# Arxo Law — binary releases

Prebuilt `law` and `law-lsp` binaries of Arxo Law: the command-line tool that
pins a canon, asks questions about a case and returns the evaluation document
with its proof.

This repository holds release assets only; it has no source code.

## Install

```sh
npm i -g @arxo/cli          # macOS arm64, Linux x64
brew install arxohq/tap/law
curl -fsSL https://github.com/arxohq/law-releases/releases/latest/download/install.sh | sh
```

Each release `law-v<version>` carries `law-<version>-<target>.tar.gz` with a
`.sha256`, `install.sh` and a Nix candidate. Every archive includes `LICENSE`,
`NOTICE` and `THIRD-PARTY-NOTICES.txt`.

Targets: `aarch64-apple-darwin`, `x86_64-unknown-linux-gnu`.

License: Apache-2.0 (see the files inside each archive).
