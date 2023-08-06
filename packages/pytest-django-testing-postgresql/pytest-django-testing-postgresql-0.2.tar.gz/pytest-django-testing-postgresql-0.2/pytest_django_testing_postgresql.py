import os

from dj_database_url import parse
from django.conf import settings
import pytest
from testing.postgresql import Postgresql

_POSTGRESQLS = []


@pytest.hookimpl(tryfirst=True)
def pytest_load_initial_conftests(early_config, parser, args):
    os.environ['DJANGO_SETTINGS_MODULE'] = early_config.getini('DJANGO_SETTINGS_MODULE')

    db_sets = getattr(settings, "PYTEST_SETUP_DATABASES", [("default",)])
    for db_set in db_sets:
        postgresql = Postgresql()
        if isinstance(db_set, str):
            db_set = [db_set]
        for db in db_set:
            settings.DATABASES[db] = parse(postgresql.url())
        _POSTGRESQLS.append(postgresql)


def pytest_unconfigure(config):
    for postgresql in _POSTGRESQLS:
        postgresql.stop()
