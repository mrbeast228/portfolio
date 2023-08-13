from backend import Backend


def frontend():
    backend = Backend()
    backend.renderBoard(0)


if __name__ == '__main__':
    frontend()
