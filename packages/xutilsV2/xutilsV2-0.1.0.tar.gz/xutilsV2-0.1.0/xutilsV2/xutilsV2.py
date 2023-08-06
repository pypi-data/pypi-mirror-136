import os

# Pycenter made by BillyTheGoat
# Github: https://github.com/billythegoat356/

def SetCenter(var:str, space:int=None):
    if not space:
        space = (os.get_terminal_size().columns - len(var.splitlines()[int(len(var.splitlines())/2)])) / 2
    return "\n".join((' ' * int(space)) + var for var in var.splitlines())