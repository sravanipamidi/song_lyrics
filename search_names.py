# This script creates a text file with five names, then allows the user to search for a name.

def create_names_file(filename):
    names = ['Alice', 'Bob', 'Charlie', 'David', 'Eve']
    with open(filename, 'w') as f:
        for name in names:
            f.write(name + '\n')

def search_name(filename, search):
    with open(filename, 'r') as f:
        names = [line.strip() for line in f]
    if search in names:
        print(search)
    else:
        print('Not found')

if __name__ == '__main__':
    filename = 'names.txt'
    create_names_file(filename)
    search = input('Enter a name to search: ')
    search_name(filename, search)
