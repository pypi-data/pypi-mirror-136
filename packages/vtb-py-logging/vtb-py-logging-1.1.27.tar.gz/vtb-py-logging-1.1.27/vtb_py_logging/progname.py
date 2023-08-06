_default_progname = None


def get_default_progname():
    global _default_progname
    return _default_progname


def set_default_progname(progname, force=False):
    global _default_progname
    if progname is not None or force:
        _default_progname = progname
