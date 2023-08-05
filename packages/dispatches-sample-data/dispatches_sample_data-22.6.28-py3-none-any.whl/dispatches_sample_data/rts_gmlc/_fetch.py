from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import (
    Optional,
)

from .. import rts_gmlc


def fetch_data(
        clone_url: Optional[str] = "https://github.com/GridMod/RTS-GMLC",
        dest_base_dir: Optional[Path] = rts_gmlc.path,
    ):
    with tempfile.TemporaryDirectory() as tmp:
        clone_dir = Path(tmp)
        subprocess.run([
            "git", "clone",
            str(clone_url),
            "--depth=1",
            clone_dir,
        ])
        src_base_dir = clone_dir / "RTS_Data"
        dirs_to_keep = [
            src_base_dir / "SourceData",
            src_base_dir / "timeseries_data_files",
        ]
        ignore_func = shutil.ignore_patterns(
            "*.R",
            "*.png",
        )
        for src_dir in dirs_to_keep:
            dest_dir = dest_base_dir / src_dir.name
            shutil.copytree(src_dir, dest_dir, ignore=ignore_func)
    return dest_base_dir


if __name__ == '__main__':
    fetch_data()
