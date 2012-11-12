#!/usr/bin/env python
# Copyright (C) 2012 Buttinsky Developers.
# See 'COPYING' for copying permission.

import os

from stack import LayerPlugin

from modules.reporting.base_logger import BaseLogger


class ModuleImporter(object):

    def _get_logger_names(self, path='modules/reporting/'):
        names = os.listdir(path)
        for name in reversed(names):
            if (name == 'base_logger.py' or ".pyc" in name
                    or name == 'hpfeeds.py' or name == '__init__.py'):
                names.remove(name)
        return names

    def get_loggers(self, create_tables=True):
        loggers = []
        try:
            BaseLogger()
            for name in self._get_logger_names():
                module_name = "modules.reporting." + name.split('.', 1)[0]
                __import__(module_name, globals(), locals(), [], -1)
            logger_classes = BaseLogger.__subclasses__()
        except ImportError as e:
            print e
            return None
        else:
            for logger_class in logger_classes:
                logger = logger_class(create_tables=create_tables)
                if logger.options['enabled'] == 'True':
                    loggers.append(logger)
            return loggers


class ReporterHander(LayerPlugin):

    def __init__(self):
        self.reporting_handler = ModuleImporter()
        self.loggers = self.reporting_handler.get_loggers()

    def receive(self, msg):
        self.log(msg.data)
        return msg

    def transmit(self, msg):
        if len(msg.data) > 0:
            self.log(msg.data)
        return msg

    def log(self, msg):
        for logger in self.loggers:
            logger.insert(msg)