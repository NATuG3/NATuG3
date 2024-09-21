{python3Packages, ...}:
python3Packages.buildPythonApplication {
  name = "NATuG";
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
  ];
  src = ./.;
  pyproject = true;

  postFixup = ''
    for file in $(find $out/lib/python3.12/site-packages -name '*.py'); do
      sed -i 's|loadUi("./|loadUi("'"$src/natug/"'/|g' "$file"
    done
  '';
}
