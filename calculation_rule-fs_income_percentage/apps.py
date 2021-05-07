import importlib
import inspect
from django.apps import AppConfig
from calculation.apps import CALCULATION_RULES

from core.abs_calculation_rule import AbsCalculationRule


MODULE_NAME = "calculation_rule-fs_income_percentage"
DEFAULT_CFG = {}


def read_all_calculation_rules():
    """function to read all calculation rules from that module"""
    for name, cls in inspect.getmembers(importlib.import_module(".calculation_rule", "calculation_rule-fs_income_percentage"), inspect.isclass):
        if 'calculation' in cls.__module__.split('.')[0]:
            CALCULATION_RULES.append(cls)
            cls.ready()


class CalculationRuleFSIncomePercentageConfig(AppConfig):
    name = MODULE_NAME

    def ready(self):
        from core.models import ModuleConfiguration
        cfg = ModuleConfiguration.get_or_default(MODULE_NAME, DEFAULT_CFG)
        read_all_calculation_rules()
