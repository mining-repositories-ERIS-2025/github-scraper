from models.bcolor import bcolors

class Selector:
    def __init__(self, options: list[tuple[str, callable]]):
        self.options = options

    def display_menu(self):
        print(bcolors.HEADER + "Select an option:" + bcolors.ENDC)
        for index, (option_id, _) in enumerate(self.options, start=1):
            print(f"{bcolors.OKBLUE}{index}. {option_id}{bcolors.ENDC}")

    def run(self):
        self.display_menu()
        try:
            choice = input(bcolors.BOLD + "Enter the number of the function to run (e.g., 1 or 4-6): " + bcolors.ENDC).strip()
            if '-' in choice:
                start, end = map(int, choice.split('-'))
                if 1 <= start <= len(self.options) and 1 <= end <= len(self.options) and start <= end:
                    for i in range(start, end + 1):
                        _, func = self.options[i - 1]
                        print(f"{bcolors.OKCYAN}Running option {i}: {self.options[i - 1][0]}{bcolors.ENDC}")
                        func()
                else:
                    print(bcolors.FAIL + "Invalid range. Please enter a valid range of numbers." + bcolors.ENDC)
            else:
                choice = int(choice)
                if 1 <= choice <= len(self.options):
                    _, func = self.options[choice - 1]
                    print(f"{bcolors.OKCYAN}Running option {choice}: {self.options[choice - 1][0]}{bcolors.ENDC}")
                    func()
                else:
                    print(bcolors.FAIL + "Invalid choice. Please enter a valid number." + bcolors.ENDC)
        except ValueError as e:
            print(bcolors.FAIL + f"Invalid input. Please enter a number or a valid range (e.g., 1 or 4-6). -- err {e}" + bcolors.ENDC)