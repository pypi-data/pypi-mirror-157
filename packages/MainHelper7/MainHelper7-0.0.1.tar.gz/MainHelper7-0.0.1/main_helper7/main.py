from .adressbook import main as ab
from .cleanfolder import main as cm


def main():
    while True:
        print('Choose command:',
            '1. AddressBook',
            '2. CleanFolder',
            '3. Close program', sep='\n')
        user_command = input('Choose function: >>> ')
        if user_command == '1':
            print('AddressBook Manager')
            result = ab()
            if result == 'Exit':
                continue

        elif user_command == '2':
            print('CleanFolder')
            result = cm()
            if result == 'Exit':
                continue

        elif user_command == '3':
            print('See you later!')
            break


if __name__ == '__main__':
    main()
