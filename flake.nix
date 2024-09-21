{
  description = "Nucleic Acid Nanotube Plotting Software";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
  }:
    flake-utils.lib.eachDefaultSystem (
      system: let
        pkgs = import nixpkgs {inherit system;};
        python = pkgs.python3.withPackages (pyPkgs: [
          pyPkgs.pyqt6
          pyPkgs.pyqtgraph
          pyPkgs.numpy
          pyPkgs.pyopengl
          pyPkgs.show-in-file-manager
          pyPkgs.pandas
          pyPkgs.xlwt
          pyPkgs.openpyxl
          pyPkgs.pyqt6-sip
          pyPkgs.matplotlib
          pyPkgs.xlsxwriter
        ]);
      in {
        packages = rec {
          default = natug;
          natug = pkgs.callPackage ./package.nix {};
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
