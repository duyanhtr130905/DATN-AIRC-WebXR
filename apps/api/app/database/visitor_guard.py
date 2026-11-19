import os
import re

from sqlalchemy import text

LOOPBACK_DATABASE_HOSTS = {"127.0.0.1", "localhost", "::1"}
LOCAL_VISITOR_DATABASE = "airc_visitor_local"


def disposable_visitor_database(name: str | None) -> bool:
    return bool(name and re.fullmatch(r"airc_test_catalog_[0-9a-f]{32}", name))


def visitor_database_name(name: str | None) -> bool:
    return name == LOCAL_VISITOR_DATABASE or disposable_visitor_database(name)


def database_identity(connection):
    return connection.execute(text("SELECT current_database(), host(inet_server_addr())")).one()


def verified_local_server(url, name, host) -> bool:
    if url.host not in LOOPBACK_DATABASE_HOSTS or url.query or url.database != name:
        return False
    # In CI the locally published port is forwarded to an isolated service container.
    return host in LOOPBACK_DATABASE_HOSTS or (
        disposable_visitor_database(name) and os.environ.get("AIRC_ALLOW_TEST_DATABASES") == "1"
    )
