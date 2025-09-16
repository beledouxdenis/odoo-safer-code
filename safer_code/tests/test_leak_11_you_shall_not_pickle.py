# Part of Odoo. See LICENSE file for full copyright and licensing details.
import os

from odoo.tools import config
from odoo.addons.safer_code.leaks.leak_11_you_shall_not_pickle import Session, SessionStore

from .common import UnsafeCase


class TestUnsafePickle(UnsafeCase):
    def test_unsafe_session_pickle(self):

        # Create a test session
        session_store = SessionStore(config.session_dir)
        sid = 'foo_12345'
        session = Session({'login': self.env.user.login}, sid)
        session_store.save(session)
        filename = session_store.get_session_filename(sid)
        # Cleanup: the above steps created a file in the filesystem holding the session.
        # Remove this file after the test.
        self.addCleanup(os.remove, session_store.get_session_filename(sid))

        # content holds the bytes of a generated pickle injecting code while unpickling
        # generated from
        """
        import pickle
        class ArbitraryCodeExecutor:
            def __reduce__(self):
                return (exec, ('import os; os.system("cp /etc/passwd /tmp/foo")',))
        print(pickle.dumps(ArbitraryCodeExecutor()))
        """
        content = b'\x80\x04\x95K\x00\x00\x00\x00\x00\x00\x00\x8c\x08builtins\x94\x8c\x04exec\x94\x93\x94\x8c/import os; os.system("cp /etc/passwd /tmp/foo")\x94\x85\x94R\x94.'
        # This exploits relies on the fact you are able to write arbitrary on your session file,
        # which normally should not be the case. However, as since in previous exploits, this is not impossible.
        # This exploits assumes you managed to find a way to write on your session file,
        # and you manage to write your own pickle content in your session file.
        with open(filename, 'wb') as f:
            f.write(content)

        session_store.get(sid)
        # Cleanup: the above step, which, during unpickling, copied /etc/passwd to /tmp/foo,
        # we need to remove it after the test
        self.addCleanup(os.remove, '/tmp/foo')

        with open('/tmp/foo', 'rb') as f:
            data = f.read()
        self.assertNotIn(
            b'root',
            data,
            'A user on the SAAS must not be able to run arbitrary server commands during unpickling a pickle file',
        )
