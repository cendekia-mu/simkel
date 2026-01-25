import logging
import os
from pyramid.events import BeforeRender, subscriber
from opensipkd.base import BaseApp
from sqlalchemy import engine_from_config
from .models import SimkelBase, SimkelDBSession

log = logging.getLogger(__name__)


class AppClass(BaseApp):
    def __init__(self):
        super().__init__()
        self.base_dir = os.path.split(__file__)[0]
        self.files = ""
        self.settings = {}

    def init(self, config):
        self.settings = config.get_settings()

    def static_views(self, config):
        self.temp_files = self.settings.get("temp_files") + os.sep
        if not os.path.exists(self.temp_files):
            os.makedirs(self.temp_files)

        config.add_static_view("simkel/static", 'simkel:static',
                               cache_max_age=3600)
        self.files = self.settings.get("simkel_files", self.temp_files) + os.sep
        if not os.path.exists(self.files):
            os.makedirs(self.files)
        config.add_static_view("simkel/files", self.files,
                               cache_max_age=0)


def get_connection(config):
    settings = config.get_settings()
    engine = engine_from_config(
        settings, 'sqlalchemy.', client_encoding='utf8',
        max_identifier_length=30)  # , convert_unicode=True
    SimkelDBSession.configure(bind=engine)
    SimkelBase.metadata.bind = engine


SIMKEL_CLASS = AppClass()


def includeme(config):
    get_connection(config)
    SIMKEL_CLASS.init(config)
    SIMKEL_CLASS.static_views(config)
    SIMKEL_CLASS.route_from_csv(config, "simkel.views",
                              template_path="simkel:views/templates/")
    config.scan(".")
    print("+", __name__, "includeme class loaded")


@subscriber(BeforeRender)
def add_global(event):
    event['get_simkel_menus'] = SIMKEL_CLASS.get_menus