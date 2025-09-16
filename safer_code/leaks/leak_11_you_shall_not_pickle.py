# Part of Odoo. See LICENSE file for full copyright and licensing details.
import os
import pickle


# https://github.com/odoo/odoo/commit/536e670f8c5ae8fffca03faa80ec3e658d505c77#diff-50dcf309b06e6d1a10ac34179d192a28e3877c8585e832d16eb2602273cad79fR24
class Session:
    def __init__(self, data, sid):
        self.__data = data
        self.sid = sid


class SessionStore:
    def __init__(
        self,
        path,
    ):
        self.path = path

    def get_session_filename(self, sid):
        # scatter sessions across 256 directories
        sha_dir = sid[:2]
        dirname = os.path.join(self.path, sha_dir)
        session_path = os.path.join(dirname, sid)
        return session_path

    def get(self, sid):
        with open(self.get_session_filename(sid), "rb") as f:
            data = pickle.load(f)
        return Session(data, sid)

    def save(self, session):
        filename = self.get_session_filename(session.sid)
        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            os.mkdir(dirname)
        with open(filename, "wb") as f:
            pickle.dump(dict(session._Session__data), f)
