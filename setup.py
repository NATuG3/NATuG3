from setuptools import find_packages, setup

setup(
    name="natug",
    version="3.0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "PyQt6",
        "pyqtgraph",
        "PyOpenGL",
        "cairosvg",
        "numpy",
        "show-in-file-manager",
        "pandas",
        "xlwt",
        "openpyxl",
        "PyQt6-sip",
        "matplotlib",
        "xlsxwriter",
    ],
    entry_points={
        "console_scripts": [
            "natug=natug:launch",
        ],
    },
    package_data={
        "natug": ["**/*.ui", "**/*.png", "**/*.svg"],
    },
    author="Wolf Mermelstein",
    author_email="wolfmermelstein@gmail.com",
    description="Nucleic acid nanotube design program",
    url="https://github.com/NATuG3/NATuG",
    python_requires=">=3.10",
)
