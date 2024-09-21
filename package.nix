{
  python3Packages,
  stdenv,
  rsync,
  ...
}:
python3Packages.buildPythonApplication rec {
  name = "natug";
  version = "3.0.1";
  buildInputs = [python3Packages.setuptools];
  propagatedBuildInputs = with python3Packages; [
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
  ];
  src = stdenv.mkDerivation {
    inherit name version;
    src = ./.;
    dontUnpack = true;
    nativeBuildInputs = [rsync];
    installPhase = ''
      rsync -av --exclude 'pyproject.toml' "$src/" "$out/"
    '';
  };
  pyproject = true;
}
