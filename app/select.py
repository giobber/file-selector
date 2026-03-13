from pathlib import Path
from typing import Collection

from loguru import logger
from pydantic import BaseModel


class SelectionManager(BaseModel):
    path: Path

    def ensure_exists(self):
        self.path.touch(exist_ok=True)

    def get_paths(self) -> Collection[Path]:
        with open(self.path, "rt") as fp:
            return set(Path(p.strip()) for p in fp.readlines())

    def add_path(self, path: Path):
        with open(self.path, "at") as fp:
            fp.write(f"{path}\n")

    def remove_path(self, path: Path):
        with open(self.path, "rt") as fp:
            paths = [line.strip() for line in fp.readlines()]
        filtered = [line for line in paths if str(path) != line]
        logger.debug(filtered)
        with open(self.path, "wt") as fp:
            fp.write("\n".join(filtered))
