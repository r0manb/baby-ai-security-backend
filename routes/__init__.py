from . import auth, model, user


def init(app, database):
    auth.init(app, database)
    user.init(app, database)
    model.init(app, database)
