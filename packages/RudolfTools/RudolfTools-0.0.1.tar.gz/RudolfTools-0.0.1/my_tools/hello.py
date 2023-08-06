import sys


def hello_world(name: str = None):
    name = name if name else "world"

    print(f'Hello {name}!!')

if __name__ == '__main__':
    try:
        name = sys.argv[1]
    except IndexError:
        name = None

    hello_world(name)