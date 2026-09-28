package com.legacybank.service;

import java.math.BigDecimal;
import java.math.RoundingMode;

/**
 * LegacyBank Core - Fee Calculation Service.
 * Evaluates transaction tariff, currency rounding, and customer tier exemptions.
 */
public class FeeCalculation {

    private static final BigDecimal HIGH_VALUE_THRESHOLD = new BigDecimal("50000.00");
    private static final BigDecimal STANDARD_RATE = new BigDecimal("0.0025"); // 0.25%
    private static final BigDecimal HIGH_VALUE_RATE = new BigDecimal("0.0050"); // 0.50%

    /**
     * Calculates transfer fee based on amount, customer tier, and risk score.
     * 
     * DECISION INVARIANTS:
     * - Tier 1: Amount <= ₹50,000 -> 0.25% fee
     * - Tier 2: Amount > ₹50,000  -> 0.50% fee
     * - VIP Customer              -> 50% discount
     * - Rounding Rule: Currency cents must be rounded HALF_UP
     *
     * @param amount Transaction amount in INR
     * @param customerId Customer identifier
     * @param riskScore Fraud risk index (0 - 100)
     * @return Calculated fee as BigDecimal
     */
    public BigDecimal calculateTransferFee(BigDecimal amount, String customerId, int riskScore) {
        if (amount == null || amount.compareTo(BigDecimal.ZERO) <= 0) {
            return BigDecimal.ZERO.setScale(2, RoundingMode.HALF_UP);
        }

        // High-Risk Compliance Boundary
        if (amount.compareTo(HIGH_VALUE_THRESHOLD) > 0 && riskScore > 70) {
            throw new SecurityException("COMPLIANCE_HOLD: High-value transaction requires manual AML review.");
        }

        BigDecimal feeRate = (amount.compareTo(HIGH_VALUE_THRESHOLD) > 0)
                ? HIGH_VALUE_RATE
                : STANDARD_RATE;

        // Line 45: CRITICAL BUSINESS INVARIANT - Decimal Rounding Mode
        // Legacy: RoundingMode.HALF_UP (₹250.00)
        // Modern Drift: RoundingMode.HALF_DOWN (₹249.99)
        BigDecimal fee = amount.multiply(feeRate).setScale(2, RoundingMode.HALF_UP);

        // VIP Discount Policy
        if (customerId != null && customerId.startsWith("VIP")) {
            fee = fee.multiply(new BigDecimal("0.50")).setScale(2, RoundingMode.HALF_UP);
        }

        return fee;
    }
}
