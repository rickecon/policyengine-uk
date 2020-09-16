from openfisca_core.model_api import *
from openfisca_uk.entities import *


class income_tax(Variable):
    value_type = float
    entity = Person
    label = u"Income tax paid per week"
    definition_period = ETERNITY

    def formula(person, period, parameters):
        return 0.45 * person("taxable_income", period)


class NI(Variable):
    value_type = float
    entity = Person
    label = u"National Insurance paid per week"
    definition_period = ETERNITY
    reference = ["https://www.gov.uk/national-insurance"]

    def formula(person, period, parameters):
        return 0.12 * person("taxable_income", period)


class basic_income(Variable):
    value_type = float
    entity = Person
    label = u"Amount of basic income received per week"
    definition_period = ETERNITY

    def formula(person, period, parameters):
        return person("is_adult", period) * 190


class family_basic_income(Variable):
    value_type = float
    entity = Family
    label = u"Amount of total basic income per week across the family"
    definition_period = ETERNITY

    def formula(family, period, parameters):
        return family.sum(family.members("basic_income", period))


class family_net_income(Variable):
    value_type = float
    entity = Family
    label = u"Net income after taxes and benefits"
    definition_period = ETERNITY

    def formula(family, period, parameters):
        return (
            family("family_total_income", period)
            + family("child_tax_credit", period)
            + family("working_tax_credit", period)
            + family("child_benefit", period)
            + family("income_support", period)
            + family("housing_benefit_actual", period)
            + family("contributory_JSA", period)
            + family("income_JSA", period)
            + family("family_basic_income", period)
            - family.sum(family.members("income_tax", period))
            - family.sum(family.members("NI", period))
            - family("benefit_cap_reduction", period)
        )


class simulation_4(Reform):
    def apply(self):
        for changed_var in [income_tax, NI, family_net_income]:
            self.update_variable(changed_var)
        for added_var in [basic_income, family_basic_income]:
            self.add_variable(added_var)