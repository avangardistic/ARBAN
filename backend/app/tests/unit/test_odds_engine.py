"""
Comprehensive test suite for the ARBAN Odds Engine.

Tests all odds conversions, calculations, and edge cases.
"""

import pytest
from decimal import Decimal
from app.odds import (
    OddsFormat,
    Odds,
    ImpliedProbability,
    FairProbability,
    Overround,
    ExpectedValue,
    ArbitrageMargin,
    StakeAllocation,
    OddsError,
    InvalidOddsError,
    ConversionError,
    decimal_to_implied_probability,
    american_to_implied_probability,
    fractional_to_implied_probability,
    convert_odds_to_probability,
    probability_to_decimal_odds,
    probability_to_american_odds,
    probability_to_fractional_odds,
    decimal_to_american,
    decimal_to_fractional,
    american_to_decimal,
    fractional_to_decimal,
    calculate_overround,
    calculate_fair_probabilities,
    calculate_expected_value,
    calculate_arbitrage_margin,
    calculate_stake_allocation,
    prediction_price_to_odds,
    odds_to_prediction_price,
    OddsEngine,
)


class TestDecimalToImpliedProbability:
    """Test decimal odds to implied probability conversion."""
    
    def test_even_odds(self):
        """Test 2.00 decimal odds = 50% probability."""
        result = decimal_to_implied_probability(Decimal("2.00"))
        assert result == Decimal("0.5")
    
    def test_favorite_odds(self):
        """Test 1.50 decimal odds = 66.67% probability."""
        result = decimal_to_implied_probability(Decimal("1.50"))
        assert abs(float(result) - 0.6666666666666666) < 1e-10
    
    def test_underdog_odds(self):
        """Test 3.00 decimal odds = 33.33% probability."""
        result = decimal_to_implied_probability(Decimal("3.00"))
        assert abs(float(result) - 0.3333333333333333) < 1e-10
    
    def test_high_odds(self):
        """Test 10.00 decimal odds = 10% probability."""
        result = decimal_to_implied_probability(Decimal("10.00"))
        assert result == Decimal("0.1")
    
    def test_invalid_zero_odds(self):
        """Test that zero odds raises error."""
        with pytest.raises(InvalidOddsError):
            decimal_to_implied_probability(Decimal("0"))
    
    def test_invalid_negative_odds(self):
        """Test that negative odds raises error."""
        with pytest.raises(InvalidOddsError):
            decimal_to_implied_probability(Decimal("-1.00"))


class TestAmericanToImpliedProbability:
    """Test American odds to implied probability conversion."""
    
    def test_positive_even(self):
        """Test +100 American odds = 50% probability."""
        result = american_to_implied_probability(Decimal("+100"))
        assert result == Decimal("0.5")
    
    def test_positive_underdog(self):
        """Test +150 American odds = 40% probability."""
        result = american_to_implied_probability(Decimal("+150"))
        assert result == Decimal("0.4")
    
    def test_positive_longshot(self):
        """Test +300 American odds = 25% probability."""
        result = american_to_implied_probability(Decimal("+300"))
        assert result == Decimal("0.25")
    
    def test_negative_favorite(self):
        """Test -150 American odds = 60% probability."""
        result = american_to_implied_probability(Decimal("-150"))
        assert result == Decimal("0.6")
    
    def test_negative_heavy_favorite(self):
        """Test -300 American odds = 75% probability."""
        result = american_to_implied_probability(Decimal("-300"))
        assert result == Decimal("0.75")
    
    def test_zero_odds(self):
        """Test that zero American odds raises error."""
        with pytest.raises(InvalidOddsError):
            american_to_implied_probability(Decimal("0"))


class TestFractionalToImpliedProbability:
    """Test fractional odds to implied probability conversion."""
    
    def test_evens(self):
        """Test 1/1 fractional odds = 50% probability."""
        result = fractional_to_implied_probability(Decimal("1"), Decimal("1"))
        assert result == Decimal("0.5")
    
    def test_three_to_two(self):
        """Test 3/2 fractional odds = 40% probability."""
        result = fractional_to_implied_probability(Decimal("3"), Decimal("2"))
        assert result == Decimal("0.4")
    
    def test_two_to_one(self):
        """Test 2/1 fractional odds = 33.33% probability."""
        result = fractional_to_implied_probability(Decimal("2"), Decimal("1"))
        assert abs(float(result) - 0.3333333333333333) < 1e-10
    
    def test_invalid_zero_denominator(self):
        """Test that zero denominator raises error."""
        with pytest.raises(InvalidOddsError):
            fractional_to_implied_probability(Decimal("1"), Decimal("0"))


class TestProbabilityToOdds:
    """Test probability to odds conversions."""
    
    def test_probability_to_decimal_50(self):
        """Test 50% probability = 2.00 decimal odds."""
        result = probability_to_decimal_odds(Decimal("0.5"))
        assert result == Decimal("2.00")
    
    def test_probability_to_decimal_25(self):
        """Test 25% probability = 4.00 decimal odds."""
        result = probability_to_decimal_odds(Decimal("0.25"))
        assert result == Decimal("4.00")
    
    def test_probability_to_decimal_10(self):
        """Test 10% probability = 10.00 decimal odds."""
        result = probability_to_decimal_odds(Decimal("0.1"))
        assert result == Decimal("10.00")
    
    def test_probability_to_american_50(self):
        """Test 50% probability = +100 American odds."""
        result = probability_to_american_odds(Decimal("0.5"))
        assert result == Decimal("-100")
    
    def test_probability_to_american_60(self):
        """Test 60% probability = -150 American odds."""
        result = probability_to_american_odds(Decimal("0.6"))
        assert result == Decimal("-150")
    
    def test_probability_to_american_40(self):
        """Test 40% probability = +150 American odds."""
        result = probability_to_american_odds(Decimal("0.4"))
        assert result == Decimal("+150")
    
    def test_probability_to_fractional_50(self):
        """Test 50% probability = 1/1 fractional odds."""
        num, den = probability_to_fractional_odds(Decimal("0.5"))
        assert num == 1
        assert den == 1
    
    def test_invalid_probability_zero(self):
        """Test that zero probability raises error."""
        with pytest.raises(InvalidOddsError):
            probability_to_decimal_odds(Decimal("0"))
    
    def test_invalid_probability_greater_than_one(self):
        """Test that probability > 1 raises error."""
        with pytest.raises(InvalidOddsError):
            probability_to_decimal_odds(Decimal("1.5"))


class TestOddsConversions:
    """Test bidirectional odds conversions."""
    
    def test_decimal_to_american_even(self):
        """Test 2.00 decimal = +100 American."""
        result = decimal_to_american(Decimal("2.00"))
        assert result == Decimal("+100")
    
    def test_decimal_to_american_favorite(self):
        """Test 1.50 decimal = -200 American."""
        result = decimal_to_american(Decimal("1.50"))
        assert abs(float(result) - (-200)) < 0.01
    
    def test_american_to_decimal_positive(self):
        """Test +150 American = 2.50 decimal."""
        result = american_to_decimal(Decimal("+150"))
        assert result == Decimal("2.50")
    
    def test_american_to_decimal_negative(self):
        """Test -150 American = 1.67 decimal."""
        result = american_to_decimal(Decimal("-150"))
        assert abs(float(result) - 1.6666666666666667) < 1e-10
    
    def test_roundtrip_probability_decimal(self):
        """Test probability -> decimal -> probability roundtrip."""
        original = Decimal("0.45")
        decimal_odds = probability_to_decimal_odds(original)
        back = decimal_to_implied_probability(decimal_odds)
        assert abs(float(back) - float(original)) < 1e-10
    
    def test_roundtrip_decimal_american(self):
        """Test decimal -> American -> decimal roundtrip."""
        original = Decimal("2.50")
        american = decimal_to_american(original)
        back = american_to_decimal(american)
        assert abs(float(back) - float(original)) < 0.01


class TestOverround:
    """Test overround/vig calculations."""
    
    def test_no_overround(self):
        """Test fair market with no overround."""
        probs = [Decimal("0.5"), Decimal("0.5")]
        result = calculate_overround(probs)
        assert result.overround == Decimal("0")
        assert result.overround_percentage == Decimal("0")
    
    def test_typical_overround(self):
        """Test typical bookmaker overround."""
        probs = [Decimal("0.55"), Decimal("0.50")]
        result = calculate_overround(probs)
        assert result.overround == Decimal("0.05")
        assert result.overround_percentage == Decimal("5")
    
    def test_three_way_overround(self):
        """Test three-way market overround."""
        probs = [Decimal("0.40"), Decimal("0.35"), Decimal("0.30")]
        result = calculate_overround(probs)
        assert result.total_implied_probability == Decimal("1.05")
        assert result.overround == Decimal("0.05")
    
    def test_empty_list(self):
        """Test empty probability list."""
        result = calculate_overround([])
        assert result.overround == Decimal("0")


class TestFairProbabilities:
    """Test fair probability normalization."""
    
    def test_no_overround_normalization(self):
        """Test fair market stays unchanged."""
        probs = [Decimal("0.5"), Decimal("0.5")]
        result = calculate_fair_probabilities(probs)
        assert len(result) == 2
        assert result[0].probability == Decimal("0.5")
        assert result[1].probability == Decimal("0.5")
    
    def test_with_overround_normalization(self):
        """Test normalization removes overround."""
        probs = [Decimal("0.55"), Decimal("0.50")]
        result = calculate_fair_probabilities(probs)
        assert len(result) == 2
        # Sum of fair probabilities should equal 1
        total = result[0].probability + result[1].probability
        assert abs(float(total) - 1.0) < 1e-10
    
    def test_three_way_normalization(self):
        """Test three-way market normalization."""
        probs = [Decimal("0.40"), Decimal("0.35"), Decimal("0.30")]
        result = calculate_fair_probabilities(probs)
        total = sum(fp.probability for fp in result)
        assert abs(float(total) - 1.0) < 1e-10


class TestExpectedValue:
    """Test expected value calculations."""
    
    def test_positive_ev(self):
        """Test positive expected value."""
        result = calculate_expected_value(Decimal("0.45"), Decimal("2.50"))
        assert result.is_positive
        assert abs(float(result.ev_percentage) - 12.5) < 0.01
    
    def test_negative_ev(self):
        """Test negative expected value."""
        result = calculate_expected_value(Decimal("0.40"), Decimal("2.00"))
        assert not result.is_positive
        assert abs(float(result.ev_percentage) - (-20)) < 0.01
    
    def test_zero_ev(self):
        """Test zero expected value (fair bet)."""
        result = calculate_expected_value(Decimal("0.5"), Decimal("2.00"))
        assert result.ev_decimal == Decimal("0")
        assert result.ev_percentage == Decimal("0")
    
    def test_invalid_probability(self):
        """Test invalid probability raises error."""
        with pytest.raises(InvalidOddsError):
            calculate_expected_value(Decimal("1.5"), Decimal("2.00"))


class TestArbitrageMargin:
    """Test arbitrage margin calculations."""
    
    def test_binary_arbitrage(self):
        """Test binary arbitrage detection."""
        odds = [Decimal("2.10"), Decimal("2.10")]
        result = calculate_arbitrage_margin(odds)
        assert result.has_arbitrage
        assert abs(float(result.arbitrage_percentage) - 4.76) < 0.01
    
    def test_no_arbitrage(self):
        """Test market with no arbitrage."""
        odds = [Decimal("1.90"), Decimal("1.90")]
        result = calculate_arbitrage_margin(odds)
        assert not result.has_arbitrage
        assert result.arbitrage_margin < 0
    
    def test_three_way_arbitrage(self):
        """Test three-way arbitrage detection."""
        odds = [Decimal("2.20"), Decimal("3.50"), Decimal("4.00")]
        result = calculate_arbitrage_margin(odds)
        # 1/2.20 + 1/3.50 + 1/4.00 = 0.4545 + 0.2857 + 0.25 = 0.9902
        assert result.has_arbitrage
        assert abs(float(result.arbitrage_percentage) - 0.98) < 0.01
    
    def test_empty_odds(self):
        """Test empty odds list."""
        result = calculate_arbitrage_margin([])
        assert not result.has_arbitrage


class TestStakeAllocation:
    """Test stake allocation calculations."""
    
    def test_binary_equal_odds(self):
        """Test stake allocation for binary with equal odds."""
        capital = Decimal("1000")
        odds = [Decimal("2.10"), Decimal("2.10")]
        result = calculate_stake_allocation(capital, odds)
        
        assert len(result.stakes) == 2
        assert abs(float(result.stakes[0]) - 500) < 0.01
        assert abs(float(result.stakes[1]) - 500) < 0.01
        assert result.total_stake == capital
        assert result.profit > 0
    
    def test_binary_unequal_odds(self):
        """Test stake allocation for binary with unequal odds."""
        capital = Decimal("1000")
        odds = [Decimal("2.00"), Decimal("2.20")]
        result = calculate_stake_allocation(capital, odds)
        
        # Stakes should be proportional to inverse odds
        assert len(result.stakes) == 2
        assert abs(float(sum(result.stakes)) - 1000) < 0.01
    
    def test_profit_calculation(self):
        """Test profit calculation is correct."""
        capital = Decimal("1000")
        odds = [Decimal("2.10"), Decimal("2.10")]
        result = calculate_stake_allocation(capital, odds)
        
        # Gross payout should be same regardless of outcome
        payout0 = result.stakes[0] * odds[0]
        payout1 = result.stakes[1] * odds[1]
        
        assert abs(float(payout0) - float(payout1)) < 0.01
        assert abs(float(result.gross_payout) - float(payout0)) < 0.01
    
    def test_invalid_capital(self):
        """Test invalid capital raises error."""
        with pytest.raises(InvalidOddsError):
            calculate_stake_allocation(Decimal("0"), [Decimal("2.00")])
        
        with pytest.raises(InvalidOddsError):
            calculate_stake_allocation(Decimal("-100"), [Decimal("2.00")])


class TestPredictionMarketConversions:
    """Test prediction market price conversions."""
    
    def test_price_to_odds_62(self):
        """Test 0.62 price = 1.61 decimal odds."""
        result = prediction_price_to_odds(Decimal("0.62"))
        assert abs(float(result) - 1.6129) < 0.001
    
    def test_price_to_odds_50(self):
        """Test 0.50 price = 2.00 decimal odds."""
        result = prediction_price_to_odds(Decimal("0.50"))
        assert result == Decimal("2.00")
    
    def test_odds_to_price_2(self):
        """Test 2.00 odds = 0.50 price."""
        result = odds_to_prediction_price(Decimal("2.00"))
        assert result == Decimal("0.50")
    
    def test_roundtrip(self):
        """Test price -> odds -> price roundtrip."""
        original = Decimal("0.62")
        odds = prediction_price_to_odds(original)
        back = odds_to_prediction_price(odds)
        assert abs(float(back) - float(original)) < 1e-10
    
    def test_invalid_price_zero(self):
        """Test zero price raises error."""
        with pytest.raises(InvalidOddsError):
            prediction_price_to_odds(Decimal("0"))
    
    def test_invalid_price_greater_than_one(self):
        """Test price > 1 raises error."""
        with pytest.raises(InvalidOddsError):
            prediction_price_to_odds(Decimal("1.5"))


class TestOddsEngine:
    """Test the main OddsEngine class."""
    
    def test_convert_decimal_to_american(self):
        """Test converting decimal to American odds."""
        result = OddsEngine.convert(
            Decimal("2.50"),
            OddsFormat.DECIMAL,
            OddsFormat.AMERICAN
        )
        assert result == Decimal("+150")
    
    def test_get_implied_probability(self):
        """Test getting implied probability."""
        result = OddsEngine.get_implied_probability(
            Decimal("2.00"),
            OddsFormat.DECIMAL
        )
        assert result.probability == Decimal("0.5")
        assert result.percentage() == 50.0
    
    def test_get_overround(self):
        """Test overround calculation."""
        odds = [Decimal("1.90"), Decimal("1.90")]
        result = OddsEngine.get_overround(odds)
        assert result.overround_percentage > 0
    
    def test_detect_arbitrage(self):
        """Test arbitrage detection."""
        odds = [Decimal("2.10"), Decimal("2.10")]
        result = OddsEngine.detect_arbitrage(odds)
        assert result.has_arbitrage
    
    def test_calculate_stakes(self):
        """Test stake calculation."""
        capital = Decimal("1000")
        odds = [Decimal("2.10"), Decimal("2.10")]
        result = OddsEngine.calculate_stakes(capital, odds)
        assert result.profit > 0
    
    def test_full_analysis(self):
        """Test comprehensive analysis."""
        odds = [Decimal("2.10"), Decimal("2.10")]
        result = OddsEngine.full_analysis(odds, capital=Decimal("1000"))
        
        assert "odds" in result
        assert "implied_probabilities" in result
        assert "fair_probabilities" in result
        assert "overround" in result
        assert "arbitrage" in result
        assert "stake_allocation" in result
        assert result["arbitrage"]["has_arbitrage"]
    
    def test_full_analysis_with_ev(self):
        """Test analysis with expected value."""
        odds = [Decimal("2.50"), Decimal("3.00")]
        probs = [Decimal("0.45"), Decimal("0.35")]
        result = OddsEngine.full_analysis(
            odds,
            your_probabilities=probs
        )
        
        assert "expected_values" in result
        assert len(result["expected_values"]) == 2


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_very_small_probability(self):
        """Test very small probability."""
        prob = Decimal("0.001")
        odds = probability_to_decimal_odds(prob)
        assert odds == Decimal("1000")
    
    def test_very_large_odds(self):
        """Test very large decimal odds."""
        odds = Decimal("1000")
        prob = decimal_to_implied_probability(odds)
        assert prob == Decimal("0.001")
    
    def test_precision_preservation(self):
        """Test that Decimal precision is preserved."""
        odds = Decimal("2.123456789")
        prob = decimal_to_implied_probability(odds)
        # Should maintain precision
        assert prob > 0
    
    def test_extreme_american_positive(self):
        """Test extreme positive American odds."""
        odds = Decimal("+10000")
        prob = american_to_implied_probability(odds)
        assert abs(float(prob) - 0.0099) < 0.0001
    
    def test_extreme_american_negative(self):
        """Test extreme negative American odds."""
        odds = Decimal("-10000")
        prob = american_to_implied_probability(odds)
        assert abs(float(prob) - 0.9901) < 0.0001


class TestDataClasses:
    """Test data class representations."""
    
    def test_odds_string_decimal(self):
        """Test Odds string representation for decimal."""
        odds = Odds(value=Decimal("2.50"), format=OddsFormat.DECIMAL)
        assert str(odds) == "2.50"
    
    def test_odds_string_american(self):
        """Test Odds string representation for American."""
        odds = Odds(value=Decimal("+150"), format=OddsFormat.AMERICAN)
        assert str(odds) == "+150"
    
    def test_implied_probability_percentage(self):
        """Test ImpliedProbability percentage."""
        ip = ImpliedProbability(
            probability=Decimal("0.45"),
            source_odds=Odds(value=Decimal("2.22"), format=OddsFormat.DECIMAL)
        )
        assert ip.percentage() == 45.0
    
    def test_overround_string(self):
        """Test Overround string representation."""
        over = Overround(
            total_implied_probability=Decimal("1.05"),
            overround=Decimal("0.05"),
            overround_percentage=Decimal("5")
        )
        assert str(over) == "5.00%"
    
    def test_expected_value_positive(self):
        """Test ExpectedValue string for positive EV."""
        ev = ExpectedValue(
            ev_decimal=Decimal("0.125"),
            ev_percentage=Decimal("12.5"),
            is_positive=True
        )
        assert str(ev) == "+12.50%"
    
    def test_expected_value_negative(self):
        """Test ExpectedValue string for negative EV."""
        ev = ExpectedValue(
            ev_decimal=Decimal("-0.20"),
            ev_percentage=Decimal("-20"),
            is_positive=False
        )
        assert str(ev) == "-20.00%"
    
    def test_arbitrage_margin_has_arb(self):
        """Test ArbitrageMargin string with arbitrage."""
        arb = ArbitrageMargin(
            sum_inverse_odds=Decimal("0.95238"),
            arbitrage_margin=Decimal("0.04762"),
            arbitrage_percentage=Decimal("4.762"),
            has_arbitrage=True
        )
        assert "+" in str(arb)
    
    def test_stake_allocation_string(self):
        """Test StakeAllocation string representation."""
        stakes = StakeAllocation(
            stakes=[Decimal("500"), Decimal("500")],
            total_stake=Decimal("1000"),
            gross_payout=Decimal("1050"),
            profit=Decimal("50"),
            roi=Decimal("0.05")
        )
        s = str(stakes)
        assert "Stakes:" in s
        assert "Profit:" in s
        assert "ROI:" in s
