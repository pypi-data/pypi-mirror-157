from tools import get_user_input, clear, wait_for_enter

class Menu():
    def __init__(self, options) -> None:
            self.option_texts = list(options.keys())
            self.option_functions = list(options.values())

    def add_option(self, text, function):
        self.option_texts.append(text)
        self.option_functions.append(function)

    def show(self):
        clear() # Clear the console

        # Print the menu
        print("Menu:")
        for i in range(len(self.option_texts)):
            print(str(i+1) + ": " + self.option_texts[i])

        # Get the user input
        try:
            choice = int(get_user_input("Select an option:")) - 1
        except ValueError: # If the user didn't enter a number, warn him, and show the menu again
            self._warn_invalid_input()
            return

        # Call the function of the selected option
        choosen_option = self._choose(choice, self.option_functions, self._warn_invalid_input)
        choosen_option()

        # Wait until the user presses enter
        wait_for_enter()

    def _warn_invalid_input(self):
        print("Invalid input, you need to give the number of the option as input!")
        wait_for_enter()
        self.show()

    def _choose(self, choice, options, default):
        """Choose a choice from the choises given
        """
        return options[choice] if choice < len(options) else default