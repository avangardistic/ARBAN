"""Unit tests for arbitrage calculator."""

from decimal import Decimal

from backend.app.arbitrage.calculator import (
    calculate_binary_arbitrage,
    calculate_multi_outcome_arbitrage,
    calculate_stakes,
    calculate_fees,
    calculate_net_metrics,
    classify_opportunity,
)


class TestBinaryArbitrage:
    """Test binary arbitrage calculations."""

    def test_arbitrage_exists(self):
        """Test detection of valid arbitrage (YES=0.43, NO=0.51)."""
        yes = Decimal("0.43")
        no = Decimal("0.51")

        is_arb, cost, profit, roi = calculate_binary_arbitrage(yes, no)

        assert is_arb is True
        assert cost == Decimal("0.94")
        assert profit == Decimal("0.06")
        # ROI = 0.06 / 0.94 = 0.0638297872...
        assert abs(float(roi) - 0.0638297872) < 0.0001

    def test_no_arbitrage_sum_equals_one(self):
        """Test boundary case where sum equals exactly 1."""
        yes = Decimal("0.50")
        no = Decimal("0.50")

        is_arb, cost, profit, roi = calculate_binary_arbitrage(yes, no)

        assert is_arb is False
        assert cost == Decimal("1.00")
        assert profit == Decimal("0")
        assert roi == Decimal("0")

    def test_no_arbitrage_sum_greater_than_one(self):
        """Test case where sum > 1 (no arbitrage)."""
        yes = Decimal("0.52")
        no = Decimal("0.51")

        is_arb, cost, profit, roi = calculate_binary_arbitrage(yes, no)

        assert is_arb is False
        assert cost == Decimal("1.03")
        assert profit == Decimal("0")

    def test_large_arbitrage(self):
        """Test with larger arbitrage opportunity."""
        yes = Decimal("0.30")
        no = Decimal("0.40")

        is_arb, cost, profit, roi = calculate_binary_arbitrage(yes, no)

        assert is_arb is True
        assert cost == Decimal("0.70")
        assert profit == Decimal("0.30")
        # ROI = 0.30 / 0.70 = 0.428571...
        assert abs(float(roi) - 0.428571) < 0.001


class TestMultiOutcomeArbitrage:
    """Test multi-outcome arbitrage calculations."""

    def test_three_way_arbitrage(self):
        """Test three-outcome arbitrage (A=0.40, Draw=0.30, B=0.25)."""
        prices = [
            Decimal("0.40"),
            Decimal("0.30"),
            Decimal("0.25"),
        ]

        is_arb, cost, profit, roi = calculate_multi_outcome_arbitrage(prices)

        assert is_arb is True
        assert cost == Decimal("0.95")
        assert profit == Decimal("0.05")
        # ROI = 0.05 / 0.95 = 0.0526315789...
        assert abs(float(roi) - 0.0526315789) < 0.0001

    def test_no_arbitrage_multi(self):
        """Test multi-outcome with no arbitrage."""
        prices = [
            Decimal("0.45"),
            Decimal("0.35"),
            Decimal("0.30"),
        ]

        is_arb, cost, profit, roi = calculate_multi_outcome_arbitrage(prices)

        assert is_arb is False
        assert cost == Decimal("1.10")
        assert profit == Decimal("0")

    def test_four_way_arbitrage(self):
        """Test four-outcome arbitrage."""
        prices = [
            Decimal("0.20"),
            Decimal("0.20"),
            Decimal("0.20"),
            Decimal("0.20"),
        ]

        is_arb, cost, profit, roi = calculate_multi_outcome_arbitrage(prices)

        assert is_arb is True
        assert cost == Decimal("0.80")
        assert profit == Decimal("0.20")
        # ROI = 0.20 / 0.80 = 0.25
        assert roi == Decimal("0.25")


class TestStakeCalculation:
    """Test stake calculation for equal returns."""

    def test_binary_stakes(self):
        """Test stake calculation for binary outcome."""
        capital = Decimal("1000")
        prices = [Decimal("0.43"), Decimal("0.51")]

        stakes = calculate_stakes(capital, prices)

        assert len(stakes) == 2
        # Sum should equal capital
        assert sum(stakes) == capital
        # Individual stakes should be proportional
        assert stakes[0] < stakes[1]  # Lower price gets lower stake

    def test_multi_stakes(self):
        """Test stake calculation for multi-outcome."""
        capital = Decimal("1000")
        prices = [Decimal("0.40"), Decimal("0.30"), Decimal("0.25")]

        stakes = calculate_stakes(capital, prices)

        assert len(stakes) == 3
        assert sum(stakes) == capital

    def test_zero_prices(self):
        """Test handling of zero prices."""
        capital = Decimal("1000")
        prices = [Decimal("0"), Decimal("0")]

        stakes = calculate_stakes(capital, prices)

        assert all(s == Decimal("0") for s in stakes)


class TestFees:
    """Test fee calculations."""

    def test_simple_fees(self):
        """Test basic fee calculation."""
        capital = Decimal("1000")
        fee_rates = [Decimal("0.01"), Decimal("0.02")]  # 1% and 2%

        fees = calculate_fees(capital, fee_rates)

        assert fees == Decimal("30")  # 10 + 20

    def test_fees_with_network(self):
        """Test fee calculation with network fee."""
        capital = Decimal("1000")
        fee_rates = [Decimal("0.01")]
        network_fee = Decimal("5")

        fees = calculate_fees(capital, fee_rates, network_fee)

        assert fees == Decimal("15")  # 10 + 5


class TestNetMetrics:
    """Test net profit/ROI calculations."""

    def test_net_after_fees(self):
        """Test net metrics after fees."""
        gross_profit = Decimal("60")
        capital = Decimal("1000")
        fees = Decimal("10")

        net_profit, net_roi = calculate_net_metrics(gross_profit, capital, fees)

        assert net_profit == Decimal("50")
        # net_roi = 50 / 1010 = 0.0495...
        assert abs(float(net_roi) - 0.0495) < 0.001


class TestClassification:
    """Test opportunity classification."""

    def test_guaranteed(self):
        """Test GUARANTEED classification."""
        result = classify_opportunity(
            is_arbitrage=True,
            settlement_verified=True,
            liquidity=Decimal("1000"),
            min_liquidity=Decimal("100"),
            fees_known=True,
            executable_prices=True,
        )

        assert result == "GUARANTEED"

    def test_executable(self):
        """Test EXECUTABLE classification."""
        result = classify_opportunity(
            is_arbitrage=True,
            settlement_verified=False,
            liquidity=Decimal("1000"),
            fees_known=True,
            executable_prices=True,
        )

        assert result == "EXECUTABLE"

    def test_potential_low_liquidity(self):
        """Test POTENTIAL classification due to low liquidity."""
        result = classify_opportunity(
            is_arbitrage=True,
            settlement_verified=True,
            liquidity=Decimal("50"),
            min_liquidity=Decimal("100"),
            fees_known=True,
            executable_prices=True,
        )

        assert result == "POTENTIAL"

    def test_theoretical(self):
        """Test THEORETICAL classification."""
        result = classify_opportunity(
            is_arbitrage=True,
            settlement_verified=True,
            liquidity=Decimal("1000"),
            executable_prices=False,
        )

        assert result == "THEORETICAL"

    def test_no_arbitrage(self):
        """Test NO_ARBITRAGE classification."""
        result = classify_opportunity(
            is_arbitrage=False,
            settlement_verified=True,
            liquidity=Decimal("1000"),
        )

        assert result == "NO_ARBITRAGE"
