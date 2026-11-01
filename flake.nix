# agentic-ledger toolkit — the agentic-nomad flake shape, trimmed to what this repo runs.
#
#   nix develop      → poppler (pdfinfo/pdftotext/pdfimages), python3, uv, gh, git
#   nix fmt          → treefmt (nixfmt + ruff-format)
#   nix flake check  → formatting + toolchain-complete + project-gate (OFFLINE: every skill
#                      script compiles, and link_sources.py answers --help)
#
# NOT in the shell on purpose: Beancount and Fava. The `beancount` plugin builds and serves the
# journal with the fleet's own pin (ADR-0004: "nix-config is the existing installer"); a second
# pin here could build a different journal than the one the plugin reviews.
{
  description = "agentic-ledger — personal financial affairs run from Claude Code, read-only on every portal";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    treefmt-nix = {
      url = "github:numtide/treefmt-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    {
      self,
      nixpkgs,
      treefmt-nix,
    }:
    let
      # x86_64-darwin is absent on purpose: nixpkgs-unstable throws on it.
      systems = [
        "aarch64-darwin"
        "aarch64-linux"
        "x86_64-linux"
      ];
      forAll = f: nixpkgs.lib.genAttrs systems (system: f system nixpkgs.legacyPackages.${system});
      inherit (nixpkgs) lib;

      treefmtEval = forAll (_: pkgs: treefmt-nix.lib.evalModule pkgs ./treefmt.nix);

      # ONE list read by devShells AND toolchain-complete, so they cannot drift.
      devPackagesFor =
        pkgs: with pkgs; [
          poppler-utils
          python3
          uv
          gh
          git
        ];
      # Binaries the skills shell out to. A package name is not a binary name
      # (poppler-utils ships pdfinfo) — that map is what this guards.
      requiredBins = [
        "pdfinfo"
        "pdftotext"
        "pdfimages"
        "python3"
        "uv"
        "gh"
        "git"
      ];
    in
    {
      formatter = forAll (system: _: treefmtEval.${system}.config.build.wrapper);

      devShells = forAll (
        _system: pkgs: {
          default = pkgs.mkShell {
            packages = devPackagesFor pkgs;
            shellHook = ''
              [ -n "''${LEDGER_DRIVE_DIR:-}" ] || echo "agentic-ledger: LEDGER_DRIVE_DIR is unset — see .envrc"
            '';
          };
        }
      );

      checks = forAll (
        system: pkgs:
        let
          gateSrc = lib.fileset.toSource {
            root = ./.;
            fileset = ./.claude/skills;
          };
        in
        {
          formatting = treefmtEval.${system}.config.build.check self;

          toolchain-complete =
            pkgs.runCommandLocal "toolchain-complete" { nativeBuildInputs = devPackagesFor pkgs; }
              ''
                missing=""
                for bin in ${lib.escapeShellArgs requiredBins}; do
                  command -v "$bin" >/dev/null 2>&1 || missing="$missing $bin"
                done
                if [ -n "$missing" ]; then
                  echo "dev shell is missing:$missing" >&2
                  exit 1
                fi
                echo "all ${toString (builtins.length requiredBins)} required binaries resolve." > "$out"
              '';

          # Offline: no Drive, no portal. Each command on its own line — under the builder's
          # `set -e` a failing `a` in an `a && b` list does not stop the script.
          project-gate = pkgs.runCommandLocal "project-gate" { nativeBuildInputs = [ pkgs.python3 ]; } ''
            cp -R ${gateSrc}/. gate
            chmod -R u+w gate
            find gate -name '*.py' -print0 | xargs -0 python3 -m py_compile
            python3 gate/.claude/skills/sync-transactions/link_sources.py --help > /dev/null
            touch "$out"
          '';
        }
      );
    };
}
