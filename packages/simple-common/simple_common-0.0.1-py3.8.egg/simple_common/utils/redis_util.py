def get_dsn(password=None, host=None, port=None, db=None):
    if password:
        return "redis://:{password}@{host}:{port}/{db}".format(
            password=password,
            host=host,
            port=port,
            db=db)
    else:
        return "redis://{host}:{port}/{db}".format(
            host=host,
            port=port,
            db=db)
