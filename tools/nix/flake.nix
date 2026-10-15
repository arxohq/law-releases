{
  description = "Arxo law and law-lsp release binaries";
  inputs.nixpkgs.url = "https://channels.nixos.org/nixos-26.05/nixexprs.tar.xz";
  outputs = { self, nixpkgs }:
    let
      systems = [ "x86_64-linux" "aarch64-darwin" ];
      eachSystem = nixpkgs.lib.genAttrs systems;
    in {
      packages = eachSystem (system:
        let
          pkgs = import nixpkgs { inherit system; };
          law = pkgs.callPackage ./package.nix { };
        in { inherit law; default = law; });
      apps = eachSystem (system: {
        default = self.apps.${system}.law;
        law = { type = "app"; program = "${self.packages.${system}.law}/bin/law"; };
        law-lsp = { type = "app"; program = "${self.packages.${system}.law}/bin/law-lsp"; };
      });
      checks = eachSystem (system: { package = self.packages.${system}.law; });
    };
}
