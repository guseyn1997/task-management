import os
from sqlalchemy import engine_from_config

def run_migrations_online():
    # ...
    config = context.config
    config.set_main_option("sqlalchemy.url", os.environ.get("DATABASE_URL"))
