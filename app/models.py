import datetime as dt
from pathlib import Path

from pydantic import BaseModel, Field, computed_field

from app.settings import ByteSize


class File(BaseModel):
    name: str
    path: Path = Field(repr=False)

    def stat(self, follow_symlinks: bool = False):
        return self.path.stat(follow_symlinks=follow_symlinks)

    @computed_field
    def weight(self) -> int:
        return self.stat().st_size

    @computed_field
    def created(self) -> dt.datetime:
        return dt.datetime.fromtimestamp(self.stat().st_ctime)

    @computed_field
    def modified(self) -> dt.datetime:
        return dt.datetime.fromtimestamp(self.stat().st_mtime)

    @classmethod
    def from_path(cls, path: Path):
        return cls(name=path.stem, path=path)


def format_size(default_byte_size: ByteSize):
    def func(size: int, byte_size: ByteSize = default_byte_size) -> str:
        match byte_size:
            case "TB":
                size >>= 40
            case "GB":
                size >>= 30
            case "MB":
                size >>= 20
            case "KB":
                size >>= 10
        return f"{size} {byte_size}"

    return func
