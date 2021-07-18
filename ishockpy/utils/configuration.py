from dataclasses import dataclass
from pathlib import Path

from omegaconf import OmegaConf

# Path to configuration

_config_path = Path("~/.config/ishockpy/").expanduser()

_config_name = Path("ishockpy_config.yml")

_config_file = _config_path / _config_name

# Define structure of configuration with dataclasses


@dataclass
class LogConsole:

    on: bool = True
    level: str = "WARNING"


@dataclass
class LogFile:

    on: bool = True
    level: str = "WARNING"


@dataclass
class Logging:

    debug: bool = False
    console: LogConsole = LogConsole()
    file: LogFile = LogFile()


# @dataclass
# class Cosmology:

#     Om: float = 0.307
#     h0: float = 67.7


@dataclass
class IShockpyConfig:

    logging: Logging = Logging()
#    cosmology: Cosmology = Cosmology()
    show_progress: bool = True


# Read the default config
ishockpy_config: IShockpyConfig = OmegaConf.structured(IShockpyConfig)

# Merge with local config if it exists
if _config_file.is_file():

    _local_config = OmegaConf.load(_config_file)

    ishockpy_config: IShockpyConfig = OmegaConf.merge(ishockpy_config,
                                                      _local_config)

# Write defaults if not
else:

    # Make directory if needed
    _config_path.mkdir(parents=True, exist_ok=True)

    with _config_file.open("w") as f:

        OmegaConf.save(config=ishockpy_config, f=f.name)
