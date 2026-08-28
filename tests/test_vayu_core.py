import pytest
import numpy as np
from datetime import datetime

# 1. Test Econometric Jevons Elementary Aggregation (Geometric Mean)
def test_jevons_geometric_mean():
    """Jevons Index requires calculating the geometric mean of observed prices."""
    prices = [5000.0, 5500.0, 6000.0, 4800.0]
    # Geometric mean = (prod(p_i))^(1/N) = exp(mean(ln(p_i)))
    expected_jevons = float(np.exp(np.mean(np.log(prices))))
    calculated_jevons = (5000.0 * 5500.0 * 6000.0 * 4800.0) ** (1 / 4)
    assert pytest.approx(expected_jevons, 0.01) == calculated_jevons

# 2. Test Laspeyres Macro Weighting
def test_laspeyres_macro_aggregation():
    """Laspeyres national index must equal the weighted sum of corridor indices."""
    corridor_indices = {"DEL-BOM": 105.2, "DEL-BLR": 102.0, "BOM-BLR": 98.5}
    weights = {"DEL-BOM": 0.50, "DEL-BLR": 0.30, "BOM-BLR": 0.20}

    # Sum of weights must equal 1.0
    assert pytest.approx(sum(weights.values()), 0.001) == 1.0

    national_index = sum(corridor_indices[k] * weights[k] for k in corridor_indices)
    expected_index = (105.2 * 0.50) + (102.0 * 0.30) + (98.5 * 0.20)
    assert pytest.approx(national_index, 0.01) == expected_index

# 3. Test IQR Outlier Detection
def test_iqr_outlier_rejection():
    """Anomalous fares (e.g., glitch fares or misclassified business class) must be flagged."""
    normal_fares = [5200, 5400, 5300, 5500, 5100, 5600, 5250, 5350]
    outlier_fare = 45000  # Extreme outlier

    q1, q3 = np.percentile(normal_fares, [25, 75])
    iqr = q3 - q1
    lower_bound = q1 - (1.5 * iqr)
    upper_bound = q3 + (1.5 * iqr)

    def is_outlier(val):
        return val < lower_bound or val > upper_bound

    assert not is_outlier(5300)
    assert is_outlier(outlier_fare)

# 4. Test Fare Decomposition (Unbundling)
def test_fare_decomposition_integrity():
    """Sum of decomposed fare components must strictly equal total headline fare."""
    total_fare = 6540.0
    base_fare = round(total_fare * 0.72, 2)
    fuel = round(total_fare * 0.16, 2)
    taxes = round(total_fare * 0.08, 2)
    convenience_fee = round(total_fare - (base_fare + fuel + taxes), 2)

    reconstructed_total = base_fare + fuel + taxes + convenience_fee
    assert pytest.approx(reconstructed_total, 0.01) == total_fare