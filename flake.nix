{
  description = "Nucleic Acid Nanotube Plotting Software";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    nix-bundle = {
      url = "github:ralismark/nix-appimage";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
    ...
  } @ inputs:
    flake-utils.lib.eachDefaultSystem (
      system: let
        pkgs = import nixpkgs {inherit system;};
        python = pkgs.python3.withPackages (pyPkgs:
          with pyPkgs; [
            pyqtgraph
            pyopengl
            numpy
            pandas
            xlwt
            openpyxl
            matplotlib
            xlsxwriter
            show-in-file-manager
            pyqt6
            qtpy
            cairosvg
          ]);
      in {
        packages = rec {
          default = natug;
          natug = pkgs.callPackage ./package.nix {};
          natug-appimage = inputs.nix-bundle.lib.${system}.mkAppImage {
            program = "${natug}/bin/natug";
          };
        };
        devShells = {
          default = pkgs.mkShell {
            packages = [
              python
              pkgs.pyright
              pkgs.black
            ];
          };
        };
      }
    );
}
