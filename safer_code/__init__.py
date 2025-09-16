from . import controllers
from . import models
from . import leaks


def _post_init_hook(env):
    env.cr.execute("""
        CREATE TABLE IF NOT EXISTS safer_code (
            create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            value VARCHAR
        )
    """)
