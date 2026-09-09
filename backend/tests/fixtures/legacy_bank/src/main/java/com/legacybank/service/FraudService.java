package com.legacybank.service;
import com.legacybank.domain.Account;

public interface FraudService {
    boolean isFraudulent(Account account, double amount);
}