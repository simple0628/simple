"""simple - 一款简单的终端 AI 助手"""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("simple")
except PackageNotFoundError:
    __version__ = "dev"
