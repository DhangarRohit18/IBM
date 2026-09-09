package com.legacybank.service;
import com.legacybank.domain.Account;
import org.springframework.stereotype.Service;

@Service
public class FraudServiceImpl implements FraudService {
    @Override
    public boolean isFraudulent(Account account, double amount) {
        return amount > 10000.0;
    }
}