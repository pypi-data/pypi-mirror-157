from subprocess import run as subprocess_run


def run(*args, **kwargs):
    return subprocess_run(*args, check=True, **kwargs)
