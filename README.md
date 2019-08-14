Attention! Translated by Google

The module is written for application, with minimal effort, in simple console
applications, includes the ability to parse command line arguments and load/save
the values of certain variables into a file. To start using the module,
simply place the *simple_config.py* file in the project directory to import the
main class and create an object based on it, specifying the necessary variables
and their default values.

```python
from simple_config import SimpleConfig

my_conf = SimpleConfig( ...,
                        flag_var = None,
                        int_var = 5,
                        string_var = 'some_string',
                        bool_var = True
                        some_var = some_val,
                                                ... )
```
The specified default values can be overridden by arguments in command line
(* my_app --var_name new_val *). Especially for the lazy the abbreviation of the
keys is allowed *dash and first letter of the name variable* (*my_app -v
new_value*) but you must consider the names variables starting with the same
letters, if the choice is ambiguous, an exception is thrown. Arguments are
applied in the order they appear on the line. Access to the value of variables
is through the properties of the object:

```python
if my_conf.flag_var
	my_conf.int_var += 100
	my_conf.save('conf.file')
```
### Valid value types for variables
*(variable types are determined by default and should not receive values of
other types.)*

* **flag** - default can have only one value *(flag = **None**)*
which will be changed by the corresponding key to the value **True**
(*my_app -f* or *my_app --flag*).

* **bool** - may take values **False | True**.
With the appropriate key, the current value is inverted or may be assigned
directly but only in short form (*my_app -btrue*).

* **int** - a value can be set in several ways, for example a value **2**
as *--num 2* or *-nn* or *-n2*. In full form *--num 2* if not specified
value will be thrown exception, in short *-n* value will be assigned **1**,
or *-nnn* accordingly **3**.

* **str, float** - require value (*my_app --key value* или *my_app -k value*).
If there is no suitable value, an exception will be thrown.

### Available Methods

* save variable values to file: *my_conf.save('file_name')*
* load variable values from file: *my_conf.load('file_name')*

Method ***.save()*** ignores **flag** type variables, variables whose names
start with "_" and variables undefined when creating an object.
Method ***.load()*** will throw an exception when loading an undefined variable

* show hint: *my_conf.show_help(err = None)*

Tooltip text must be defined in a variable *_help_text*. If he doesn't
defined then the value is taken from *docstring* main module either if he
doesn’t defined, displays current values of variables. The method throws an exception "ConfigError" with message text. This method is also called when processing errors occur., error message is added to the beginning of the text.

### Predefined variables

* "**_**" the last argument is keyless, e.g. ***my_app param1 param2***
value **param2** will be placed
* **_separator** contains a delimiter string used to separate name - values
in the config file.

### Predefined keys

* *my_app --load_conf file_name* - load values from file
* *my_app --save_conf file_name* - save values to file
* *my_app --help* - print help message and quit

