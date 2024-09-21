{python3Packages, ...}:
python3Packages.buildPythonApplication {
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
  src = ./.;
  pyproject = true;
}
