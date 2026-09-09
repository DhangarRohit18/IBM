package com.legacybank.util;

public class CurrencyUtils {
    public static String formatUSD(double amount) {
        return String.format("$%.2f", amount);
    }
}