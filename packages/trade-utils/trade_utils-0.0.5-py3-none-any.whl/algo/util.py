
def format_vars(*args, **kwargs):
    """
    method to shorten dubug ie
    log.info('message', extra=d(1))
    instead of
    log.info('message', extra={'v': 1})
    """
    return {'a': args, 'kwa': kwargs}


d = format_vars
