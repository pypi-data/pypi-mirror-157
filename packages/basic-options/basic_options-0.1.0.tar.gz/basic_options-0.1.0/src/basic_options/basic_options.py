import json
from typing import Any, Dict
from abc import ABC, abstractmethod
from typing_extensions import Self


class BasicOptions(ABC):
    def __init__(self):
        self.set_defaults()
        self._defaults: Dict = self.__dict__.copy()
        self._wrappers: Dict[str, Any] = {}
        for key in self._defaults.keys():
            self._wrappers[key] = None

    @abstractmethod
    def set_defaults(self) -> None:
        """Sets the default values. This function needs to be overriden by any class inheriting BasicOptions.
        """
        pass

    def set_option_wrapper(self, option: str, wrapper: Any) -> None:
        """Sets a wrapper object for an option, and sets the value in the wrapper to the option's current value.

        Args:
            option (str): Exact name of the option.
            wrapper (Any): An object with .set() and .get() functions.
        """
        wrapper.set(self.get_option(option))
        self._wrappers[option] = wrapper

    def to_dict(self) -> dict:
        """Converts the options into a dictionary.

        Returns:
            dict: A dictionary containing all options.
        """
        options = {}
        for key in self._defaults.keys():
            options[key] = self.get_option(key)
        return options

    def to_json(self) -> str:
        """Converts the options into a json string.

        Returns:
            str: A json string containing all options.
        """
        return json.dumps(self.to_dict(), indent=4)

    def save_file(self, file_path: str) -> None:
        """Saves a json string containing all options to the specified file path.

        Args:
            file_path (str): The file path to save to.
        """
        with open(file_path, "w+") as f:
            f.write(self.to_json())

    def load_dict(self, new_values_dict: dict) -> Self:
        """Loads a dictionary into the options object.

        Args:
            new_values_dict (dict): The dictionary to load.

        Returns:
            Self: The options object.
        """
        for key in new_values_dict.keys():
            if key in self._defaults.keys() and type(new_values_dict[key]) == type(self._defaults[key]) and not key.startswith("_"):
                self.set_option(key, new_values_dict[key])
        return self

    def load_json(self, json_string: str) -> Self:
        """Loads a json string into the options object.

        Args:
            json_string (str): The json string to load.

        Returns:
            Self: The options object.
        """
        return self.load_dict(json.loads(json_string))

    def load_file(self, file_path: str) -> Self:
        """Loads a file containing a json string into the options object.

        Args:
            file_path (str): The path of the file to load.

        Returns:
            Self: The options object.
        """
        with open(file_path, "r") as f:
            self.load_json(f.read())
        return self

    def try_load_file(self, file_path: str) -> Self:
        """Loads a file containing a json string into the options object. This function will

        Args:
            file_path (str): The path of the file to load.

        Returns:
            Self: The options object.
        """
        try:
            self.load_file(file_path)
        except:
            pass
        return self

    def _json(self) -> dict:
        return {"type": self.__class__.__name__, "options": self.to_dict()}

    def set_options(self, **options) -> Self:
        """Sets multiple options. For example:
        o.set_options(value_a=20, name="Profile A")

        Returns:
            Self: The options object.
        """
        return self.load_dict(options)

    def set_option(self, option: str, value: Any) -> Self:
        """Sets a single option.

        Args:
            option (str): The option that will be set.
            value (Any): The value to change option to.

        Returns:
            Self: The options object.
        """
        self.__dict__[option] = value
        if self._wrappers[option]:
            self._wrappers[option].set(value)
        return self

    def get_option(self, option: str) -> Any:
        """Retrieves an option.

        Args:
            option (str): The name of the option.

        Returns:
            Any: The value of the option.
        """
        if self._wrappers[option]:
            self.__dict__[option] = self._wrappers[option].get()
        return self.__dict__[option]

    def __repr__(self) -> str:
        return self.__class__.__name__ + " " + self.to_json()

    def __str__(self) -> str:
        return self.__repr__()

    __getitem__ = get_option
    __setitem__ = set_option


if __name__ == "__main__":
    # EXAMPLE USAGE

    # Create an options class inheriting BasicOptions, and override the set_defaults function
    class ExampleOptions(BasicOptions):
        def set_defaults(self) -> None:
            self.value_a = 1
            self.valueB = "2"
            self.c = [3, 4, 5]
            self.delta = 6.0
            self.Eee = {"value": 7}

    # Create an instance of the options
    example = ExampleOptions()

    # Change a value in the options using .set_option() or item notation
    example["delta"] += 0.6666
    # You can do `example.delta += 0.6666`, however that would not activate the wrappers from .set_option_wrappers()

    # Retreiving options can be done with .get_option(), or item notation
    print(example.get_option("delta"))
    print(example["c"])

    # Loading and saving options can be done easily with .save_file(), .try_load_file() and .load_file()
    # example2 = ExampleOptions().load_file("old_save.json").
    # example2.save_file("new_save.json")
    # Retreiving dictionaries and json strings with .to_json() and .to_dict()
