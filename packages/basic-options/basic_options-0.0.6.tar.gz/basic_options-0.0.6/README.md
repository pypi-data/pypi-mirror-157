# Basic Options

This package provides a basic way to create configuration files, especially for tkinter GUI applictions.


```python
# EXAMPLE USAGE

# Create an options class inheriting BasicOptions, and override the _set_defaults function
class ExampleOptions(BasicOptions):
    def _set_defaults(self):
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

# Loading and saving options can be done easily with .save_file() and .load_file()
# example2 = ExampleOptions().load_file("old_save.json").
# example2.save_file("new_save.json")
# Retreiving dictionaries and json strings with .to_json() and .to_dict()
```