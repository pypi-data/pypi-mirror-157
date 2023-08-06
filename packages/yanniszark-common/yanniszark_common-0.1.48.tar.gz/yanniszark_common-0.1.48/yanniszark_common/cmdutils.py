from subprocess import run as subprocess_run


def run(*args, **kwargs):
    """Run commands idiomatically.

    Differences from default subprocess.run:
    - Errors raise an exception instead of having to check."""
    return subprocess_run(*args, check=True, **kwargs)
