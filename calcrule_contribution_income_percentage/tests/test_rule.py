import uuid

from django.test import TestCase

from calcrule_contribution_income_percentage.calculation_rule import ContributionValuationRule
from contract.models import Contract, ContractDetails, ContractContributionPlanDetails
from contribution_plan.tests.helpers import create_test_contribution_plan, create_test_contribution_plan_bundle
from insuree.test_helpers import create_test_insuree
from policyholder.tests.helpers import create_test_policy_holder, create_test_policy_holder_insuree
from product.test_helpers import create_test_product


class IncomePercentageRuleTest(TestCase):
    """OP-3322: the income is read from the enrolment with the contract's policy holder."""

    rule = ContributionValuationRule

    @classmethod
    def setUpTestData(cls):
        product = create_test_product("INCPCT", custom_props={"insurance_period": 12})
        cls.plan = create_test_contribution_plan(
            product=product,
            calculation=cls.rule.uuid,
            custom_props={"json_ext": {"calculation_rule": {"rate": 10}}},
        )
        cls.insuree = create_test_insuree()
        cls.policy_holder_low = create_test_policy_holder(custom_props={"code": "PHLOW"})
        cls.policy_holder_high = create_test_policy_holder(custom_props={"code": "PHHIGH"})
        cls.policy_holder_none = create_test_policy_holder(custom_props={"code": "PHNONE"})
        for policy_holder, income in ((cls.policy_holder_low, 1000), (cls.policy_holder_high, 5000)):
            create_test_policy_holder_insuree(
                policy_holder=policy_holder,
                insuree=cls.insuree,
                custom_props={"json_ext": {"calculation_rule": {"income": income}}},
            )

    def _ccpd(self, policy_holder, plan=None):
        contract_details = ContractDetails(
            contract=Contract(policy_holder=policy_holder),
            insuree=self.insuree,
            json_ext={},
        )
        return ContractContributionPlanDetails(
            contribution_plan=plan or self.plan, contract_details=contract_details
        )

    def test_value_uses_the_income_with_the_contract_policy_holder(self):
        self.assertEqual(self.rule.calculate(self._ccpd(self.policy_holder_high), context="value"), 500)
        self.assertEqual(self.rule.calculate(self._ccpd(self.policy_holder_low), context="value"), 100)

    def test_value_without_enrolment_with_the_policy_holder(self):
        # the insuree is enrolled with other policy holders only: no income to use
        self.assertFalse(self.rule.calculate(self._ccpd(self.policy_holder_none), context="value"))

    def test_members_without_json_ext(self):
        product = create_test_product("INCPCT2", custom_props={"insurance_period": 12})
        plan = create_test_contribution_plan(
            product=product, calculation=self.rule.uuid, custom_props={"json_ext": None}
        )
        members = self.rule.calculate(self._ccpd(self.policy_holder_high, plan=plan), context="members")
        self.assertEqual(members, [self.insuree])

    def test_check_calculation_matches_if_any_fk_matches(self):
        empty_bundle = create_test_contribution_plan_bundle()
        ccpd = ContractContributionPlanDetails(
            contribution_plan=self.plan,
            contract_details=ContractDetails(contribution_plan_bundle=empty_bundle),
        )
        self.assertTrue(self.rule.check_calculation(ccpd))

    def test_check_calculation_no_fk_matches(self):
        product = create_test_product("INCPCT3", custom_props={"insurance_period": 12})
        other_plan = create_test_contribution_plan(product=product, calculation=str(uuid.uuid4()))
        ccpd = ContractContributionPlanDetails(
            contribution_plan=other_plan,
            contract_details=ContractDetails(contribution_plan_bundle=create_test_contribution_plan_bundle()),
        )
        self.assertFalse(self.rule.check_calculation(ccpd))
