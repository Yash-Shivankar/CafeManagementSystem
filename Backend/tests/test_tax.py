"""The bill arithmetic.

Tested on its own, with no database and no HTTP, because this is the part of
the system that has to survive an auditor rather than a code review.

The property every test here is really checking is that **the parts add up to
the whole**: lines + tax + round-off == grand total, and cgst + sgst == tax.
A bill where they do not is a bill a customer disputes and a return that fails
reconciliation, and rounding is where both go wrong.
"""

from decimal import Decimal

import pytest

from app.utils.money import ZERO, add, quantise
from app.utils.tax import (
    ALLOWED_GST_RATES,
    Bill,
    TaxLine,
    compute_bill,
    is_allowed_rate,
)

D = Decimal


def line(desc, qty, price, rate=5):
    return TaxLine(
        description=desc, quantity=D(str(qty)), unit_price=D(str(price)), tax_rate=D(str(rate))
    )


def assert_internally_consistent(bill: Bill):
    """The invariants that must hold for every bill this module produces."""
    assert add(bill.cgst_amount, bill.sgst_amount) == bill.tax_amount

    assert add(bill.taxable_amount, bill.tax_amount, bill.round_off) == bill.grand_total

    for computed in bill.lines:
        assert add(computed.taxable_amount, computed.tax_amount) == computed.line_total

    assert add(*[c.discount_amount for c in bill.lines]) == bill.discount_amount

    assert add(*[b["cgst"] for b in bill.tax_breakup.values()]) == bill.cgst_amount
    assert add(*[b["sgst"] for b in bill.tax_breakup.values()]) == bill.sgst_amount


class TestSimpleBill:
    def test_a_plain_bill_at_five_percent(self):
        bill = compute_bill([line("Cappuccino", 2, 180), line("Croissant", 1, 140)])

        assert bill.subtotal == D("500.00")
        assert bill.taxable_amount == D("500.00")
        assert bill.tax_amount == D("25.00")
        assert bill.cgst_amount == D("12.50")
        assert bill.sgst_amount == D("12.50")
        assert bill.grand_total == D("525.00")
        assert bill.round_off == ZERO
        assert_internally_consistent(bill)

    def test_an_empty_bill_is_zero_rather_than_an_error(self):
        bill = compute_bill([])
        assert bill.grand_total == ZERO
        assert bill.lines == []
        assert_internally_consistent(bill)

    def test_a_zero_rated_line_attracts_no_tax(self):
        bill = compute_bill([line("Packaged water", 1, 20, rate=0)])
        assert bill.tax_amount == ZERO
        assert bill.grand_total == D("20.00")
        assert_internally_consistent(bill)


class TestInclusivePricing:
    """The menu price a customer reads is usually tax-inclusive. Getting this
    backwards is a 5% error on every bill, in one direction or the other."""

    def test_an_inclusive_price_is_unpicked_not_added_to(self):
        bill = compute_bill([line("Latte", 1, 210, rate=5)], prices_include_tax=True)

        assert bill.taxable_amount == D("200.00")
        assert bill.tax_amount == D("10.00")
        assert bill.grand_total == D("210.00")
        assert_internally_consistent(bill)

    def test_exclusive_pricing_adds_tax_on_top(self):
        bill = compute_bill([line("Latte", 1, 200, rate=5)], prices_include_tax=False)
        assert bill.grand_total == D("210.00")


class TestDiscount:
    def test_a_discount_reduces_the_tax_as_well_as_the_total(self):
        bill = compute_bill([line("Cappuccino", 2, 250)], discount_amount=D("100"))

        assert bill.subtotal == D("500.00")
        assert bill.taxable_amount == D("400.00")
        assert bill.tax_amount == D("20.00")
        assert bill.grand_total == D("420.00")
        assert_internally_consistent(bill)

    def test_a_discount_is_spread_across_lines_in_proportion_to_value(self):
        bill = compute_bill(
            [line("Coffee", 1, 300), line("Cake", 1, 100)],
            discount_amount=D("40"),
        )
        assert bill.lines[0].discount_amount == D("30.00")
        assert bill.lines[1].discount_amount == D("10.00")
        assert_internally_consistent(bill)

    def test_an_indivisible_discount_still_adds_up_exactly(self):
        bill = compute_bill(
            [line("A", 1, 100), line("B", 1, 100), line("C", 1, 100)],
            discount_amount=D("10"),
        )
        assert add(*[c.discount_amount for c in bill.lines]) == D("10.00")
        assert_internally_consistent(bill)

    def test_a_discount_larger_than_the_bill_is_refused(self):
        with pytest.raises(ValueError, match="more than the bill"):
            compute_bill([line("Coffee", 1, 100)], discount_amount=D("500"))

    def test_a_negative_discount_is_refused(self):
        with pytest.raises(ValueError, match="cannot be negative"):
            compute_bill([line("Coffee", 1, 100)], discount_amount=D("-500"))

    def test_a_full_discount_leaves_nothing_to_tax(self):
        bill = compute_bill([line("Coffee", 1, 100)], discount_amount=D("100"))
        assert bill.grand_total == ZERO
        assert bill.tax_amount == ZERO
        assert_internally_consistent(bill)


class TestServiceCharge:
    def test_service_charge_is_taxable(self):
        bill = compute_bill([line("Dinner", 1, 1000, rate=5)], service_charge_percent=D("10"))

        assert bill.service_charge == D("100.00")
        assert bill.taxable_amount == D("1100.00")
        assert bill.tax_amount == D("55.00")
        assert bill.grand_total == D("1155.00")
        assert_internally_consistent(bill)

    def test_service_charge_follows_the_discounted_value(self):
        bill = compute_bill(
            [line("Dinner", 1, 1000)],
            discount_amount=D("200"),
            service_charge_percent=D("10"),
        )
        assert bill.service_charge == D("80.00")
        assert_internally_consistent(bill)

    def test_service_charge_takes_the_rate_carrying_the_most_value(self):
        bill = compute_bill(
            [line("Food", 1, 1000, rate=5), line("Bottled drink", 1, 100, rate=18)],
            service_charge_percent=D("10"),
        )
        assert "5" in bill.tax_breakup
        assert bill.tax_breakup["5"]["taxable"] == D("1110.00")
        assert_internally_consistent(bill)


class TestMixedSlabs:
    def test_each_slab_is_reported_separately(self):
        bill = compute_bill([line("Food", 1, 1000, rate=5), line("Merchandise", 1, 1000, rate=18)])

        assert set(bill.tax_breakup) == {"5", "18"}
        assert bill.tax_breakup["5"]["taxable"] == D("1000.00")
        assert bill.tax_breakup["18"]["taxable"] == D("1000.00")
        assert bill.tax_amount == D("230.00")
        assert_internally_consistent(bill)


class TestRounding:
    def test_the_total_rounds_to_the_nearest_rupee_and_says_so(self):
        bill = compute_bill([line("Coffee", 1, D("123.45"))])

        assert bill.grand_total == bill.grand_total.to_integral_value()
        assert bill.round_off != ZERO
        assert_internally_consistent(bill)

    def test_rounding_can_be_turned_off_for_a_digital_settlement(self):
        bill = compute_bill([line("Coffee", 1, D("123.45"))], round_total=False)
        assert bill.round_off == ZERO
        assert bill.grand_total == D("129.62")
        assert_internally_consistent(bill)

    def test_an_odd_paise_tax_still_splits_without_losing_anything(self):
        bill = compute_bill([line("Odd", 1, D("100.10"))])
        assert add(bill.cgst_amount, bill.sgst_amount) == bill.tax_amount
        assert_internally_consistent(bill)

    @pytest.mark.parametrize("price", ["0.01", "0.05", "33.33", "99.99", "1234.56"])
    def test_consistency_holds_for_awkward_amounts(self, price):
        lines = [line("A", 3, price, rate=5), line("B", 7, price, rate=18)]
        discount = quantise(add(*[item.gross for item in lines]) / D("10"))

        bill = compute_bill(
            lines,
            discount_amount=discount,
            service_charge_percent=D("7.5"),
        )
        assert_internally_consistent(bill)


class TestRates:
    def test_the_legal_slabs_are_declared(self):
        assert is_allowed_rate(5)
        assert is_allowed_rate(D("18"))
        assert not is_allowed_rate(7)
        assert set(ALLOWED_GST_RATES) == {D(r) for r in (0, 5, 12, 18, 28)}


class TestMoneyNeverBecomesFloat:
    def test_every_figure_comes_back_as_a_quantised_decimal(self):
        bill = compute_bill([line("Coffee", 3, D("83.33"))], service_charge_percent=D("10"))

        for value in (
            bill.subtotal,
            bill.taxable_amount,
            bill.tax_amount,
            bill.cgst_amount,
            bill.sgst_amount,
            bill.service_charge,
            bill.round_off,
            bill.grand_total,
        ):
            assert isinstance(value, Decimal)
            assert value == quantise(value)
