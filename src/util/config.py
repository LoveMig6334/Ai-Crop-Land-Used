import pathlib
import yaml

_config_path = pathlib.Path(__file__).parent.parent.parent / "config.yaml"

with open(_config_path, encoding="utf-8") as _f:
    CFG = yaml.safe_load(_f)
