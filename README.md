# openimis-be-calculation-rule-fs_salary_procentage_py
This repository holds the files of the openIMIS Backend calculation rule fs income percentage reference module.
It is dedicated to be deployed as a module of [openimis-be_py](https://github.com/openimis/openimis-be_py). It is an 
extended part of calculation module [openimis-be-calculation_py](https://github.com/openimis/openimis-be-calculation_py) 
and therefore that module is dependent on this core calculation module. This module contains additional calculation rules. 

## Models
  - None (using no database approach for CalculationRule) - Calculation Rule is saved by defining class 
    extending the ABSCalculationClass from core module.


## GraphQl Queries
  None

## Services
  None

## Configuration options (can be changed via core.ModuleConfiguration)
  loading implemented rules from "calculation_rule.py" into global variable "CALCULATION_RULE"

## Income used by the rule
The contribution is `rate` (contribution plan `json_ext.calculation_rule.rate`) percent of the
income. The income is read from the contract detail (`json_ext.calculation_rule.income`), else
from the insuree's enrolment with **the contract's policy holder** (`PolicyHolderInsuree`, not
deleted, latest `date_valid_from`). An insuree may be enrolled with several policy holders, each
with its own income; an enrolment with another policy holder is never used. Without an income,
the rule returns `False`.
