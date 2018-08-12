# coding: utf-8
"""
:module: custom_commands.custom_structure
:synopsis:

:moduleauthor: anthony greau <anthony.greau.infogene@axa-lifeinvest.com>

:seealso: `AppConfig <django.apps.AppConfig>`_
"""
from django.apps import AppConfig


class CustomStructureConfig(AppConfig):
    """
    """
    name = '.'.join(__name__.split('.')[0:-1])
