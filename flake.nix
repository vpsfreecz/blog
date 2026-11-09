{
  description = "vpsFree.cz bilingual blog";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";

  outputs = { self, nixpkgs }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" ];
      eachSystem = nixpkgs.lib.genAttrs systems;
    in {
      devShells = eachSystem (system:
        let pkgs = import nixpkgs { inherit system; };
        in { default = pkgs.mkShell { packages = [ pkgs.hugo pkgs.python3 pkgs.pagefind pkgs.nodejs
            (pkgs.hunspell.withDicts (dicts: [ dicts.cs_CZ dicts.en_US ])) ]; }; });
      packages = eachSystem (system:
        let
          pkgs = import nixpkgs { inherit system; };
          sourceInfo = pkgs.writeText "blog-source.json" (builtins.toJSON {
            revision = self.rev or self.dirtyRev or null;
            source = toString self.outPath;
            sourceNarHash = self.narHash;
            nixpkgsRevision = nixpkgs.rev;
            nixpkgsNarHash = nixpkgs.narHash;
            hugoVersion = pkgs.hugo.version;
            pagefindVersion = pkgs.pagefind.version;
          });
          site = pkgs.stdenvNoCC.mkDerivation {
            pname = "vpsfree-blog";
            version = "0";
            src = self;
            nativeBuildInputs = [ pkgs.hugo pkgs.python3 pkgs.pagefind ];
            postPatch = "patchShebangs bin";
            dontConfigure = true;
            buildPhase = ''
              export HOME="$TMPDIR"
              export BLOG_SOURCE_INFO=${sourceInfo}
              bin/build "$TMPDIR/site"
            '';
            installPhase = ''cp -r "$TMPDIR/site" "$out"'';
          };
        in { inherit site; default = site; });
    };
}
