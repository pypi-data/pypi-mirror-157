# Python clitools
This package removes annoying boilerplate code that you will see you write yourself over and over again to create a pleasant cli-centered user interface.

* [Installation](#installation)
* [Tools](#tools)
* [Menu](#menu)

# Installation
For more information, check out the [PyPi page](https://pypi.org/project/JefvdA-python-clitools/)

to install the newest version, use:
```
pip install JefvdA-python-clitools
```

# Tools
The tools are methods that are used most-often. <br>
These include:
* **clear()** -> OS independant method to clear the terminal
* **wait_for_enter()** -> method to wair for user input before continuing, clears the screen after
* **get_user_input()** -> method to returns user input. This method formats the text printed for the input to add " >>> " after it. Example: "What is your name?", becomes, "What is your name? >>> "

# Menu
A "Menu" class that makes it very easy to display a menu in the terminal, and have different results for all the options the user can choose from.

When initiating a new "Menu" object, make sure to pass it all the options, aswell as their corresponding fucntions. <br>
Example:
```python
menu_options = {
    "Hello world": say_hello_world,
    "Greet by name": ask_for_name,
    "Get random number": get_random_number,
    "Exit": exit
}
menu = Menu(menu_options)
```

When a "Menu" option is created, it can be displayed with the "show()" method.
```python
menu.show()
```
*This will only run the menu once, if you wish to keep displaying the menu. Wrap the "show" in a while loop + add an option to exit the program*