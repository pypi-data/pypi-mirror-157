import json
import os
from typing import Union, Any, Dict

from LigralPy.config import get_workdir
from LigralPy.tools.translation import _trans


class Undefined:
    pass


class Property:
    def __init__(self, value, type=None, required=False) -> None:
        self.value = value
        self.type = type
        self.required = required

    def get_type(self):
        return {str: "string", int: "int", float: "float", bool: "bool"}[self.type]


class ProjectConfig:
    def __init__(self) -> None:
        self.python: Union[str, Undefined] = Property(Undefined(), str)
        # self.inner_plotter: Union[bool, Undefined] = Property(
        #     Undefined(), bool)
        self.step_size: Union[float, Undefined] = Property(Undefined(), float)
        self.stop_time: Union[float, Undefined] = Property(Undefined(), float)
        self.realtime: Union[bool, Undefined] = Property(Undefined(), bool)
        self.load()

    def load(self):
        wd = get_workdir()
        settings_file = os.path.join(wd, "ligralpy-project-settings.json")
        if not os.path.exists(settings_file):
            self.dump()
        with open(settings_file, "r") as f:
            loaded_settings = json.load(f)
            settings_keys = list(self.__dict__.keys())
            for settings_key in settings_keys:
                if settings_key in loaded_settings:
                    self.__dict__[settings_key].value = loaded_settings[settings_key]

    def dump(self):
        wd = get_workdir()
        with open(os.path.join(wd, "ligralpy-project-settings.json"), "w") as f:
            settings_to_dump = {
                k: v.value
                for k, v in self.__dict__.items()
                if not isinstance(v.value, Undefined)
            }
            json.dump(settings_to_dump, f)

    def to_ligral_config(self):
        return [
            {"item": k, "value": v.value}
            for k, v in self.__dict__.items()
            if not isinstance(v.value, Undefined)
        ]

    def from_frontend(self, d: Dict[str, Any]):
        """
        加载从前端而来的设置。
        """
        for k, v in d.items():
            if v is None:
                self.__dict__[k].value = Undefined()
            else:
                self.__dict__[k].value = v
        self.dump()

    def get_help(self, help_item: str):
        try:
            help = {
                "python": _trans("The path of python executable. If "),
                "inner_plotter": _trans("If inner plotter is enabled"),
                "step_size": _trans("The time interval of each step."),
                "stop_time": _trans("The stop time of simulation"),
                "realtime": _trans("If realtime simulation is enabled"),
            }[help_item]
            return help
        except KeyError as e:
            raise KeyError(f"{help_item} is not a valid setting item.")

    def to_frontend_struct(self):
        d = {
            k: {
                "Type": prop.get_type(),
                "Default": None,
                "Required": prop.required,
                "Meta": None,
                "Translation": _trans(k),
                "Help": self.get_help(k),
                "Value": prop.value if not isinstance(prop.value, Undefined) else None,
            }
            for k, prop in self.__dict__.items()
        }
        return d
