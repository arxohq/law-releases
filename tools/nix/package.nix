{ lib, stdenv, fetchurl, autoPatchelfHook, release ? builtins.fromJSON (builtins.readFile ./release.json), src ? null }:
let
  system = stdenv.hostPlatform.system;
  pin = if release == null then
    throw "Arxo Nix: no CLI release pinned; run prepare.py with both release archives"
  else release.platforms.${system} or (throw "Arxo Nix: unsupported platform ${system}");
in stdenv.mkDerivation {
  pname = "arxo-law-bin";
  version = if release == null then
    throw "Arxo Nix: no CLI release pinned; run prepare.py with both release archives"
    else release.version;
  src = if src != null then src else fetchurl { inherit (pin) url hash; };
  sourceRoot = ".";
  nativeBuildInputs = lib.optionals stdenv.hostPlatform.isLinux [ autoPatchelfHook ];
  buildInputs = lib.optionals stdenv.hostPlatform.isLinux [ stdenv.cc.cc.lib ];
  dontBuild = true;
  dontStrip = true;
  installPhase = ''
    runHook preInstall
    install -Dm755 law "$out/bin/law"
    install -Dm755 law-lsp "$out/bin/law-lsp"
    # Upstream hashes describe original bytes, before Nix ELF fixups.
    install -Dm644 law-dist-manifest.json "$out/share/arxo/upstream-law-dist-manifest.json"
    install -Dm644 -t "$out/share/doc/arxo-law" LICENSE NOTICE THIRD-PARTY-NOTICES.txt
    runHook postInstall
  '';
  doInstallCheck = true;
  installCheckPhase = ''
    runHook preInstallCheck
    "$out/bin/law" version | grep -F '${release.version}'
    "$out/bin/law-lsp" --help
    runHook postInstallCheck
  '';
  meta = {
    description = "Arxo executable rules CLI and language server";
    homepage = "https://www.arxo.io";
    license = lib.licenses.asl20;
    platforms = [ "x86_64-linux" "aarch64-darwin" ];
    mainProgram = "law";
    sourceProvenance = [ lib.sourceTypes.binaryNativeCode ];
  };
}
