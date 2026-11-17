# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

root = Path(SPECPATH)
analysis = Analysis(
    [str(root / "anyfind" / "__main__.py")],
    pathex=[str(root)],
)

if sys.platform == "win32":
    # Qt uses the Windows ICU API. DLLs from unrelated tools on PATH can
    # shadow the system libraries and prevent Qt from loading.
    analysis.binaries = [
        binary
        for binary in analysis.binaries
        if not Path(binary[0]).name.lower().startswith("icu")
    ]

archive = PYZ(analysis.pure)
executable = EXE(
    archive,
    analysis.scripts,
    [],
    exclude_binaries=True,
    name="AnyFind",
    console=False,
)
bundle = COLLECT(executable, analysis.binaries, analysis.datas, name="AnyFind")

if sys.platform == "darwin":
    app = BUNDLE(bundle, name="AnyFind.app", bundle_identifier="com.anyfind.desktop")
