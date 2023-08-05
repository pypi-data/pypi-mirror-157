# -*- coding: utf-8 -*-
"""
ui driver proxy
"""
from flybirds.core.global_context import GlobalContext


def air_bdd_screen_size(dr_instance):
    return GlobalContext.ui_driver.air_bdd_screen_size(dr_instance)


def init_driver():
    return GlobalContext.ui_driver.init_driver()


def init_ocr():
    return GlobalContext.ui_driver.init_ocr()


def close_driver():
    return GlobalContext.ui_driver.close_driver()
