from os import listdir, path
__all__ = [file.split('.', 1)[0] for file in listdir(path=path.dirname(path.abspath(__file__))) if file.endswith('.py')]
