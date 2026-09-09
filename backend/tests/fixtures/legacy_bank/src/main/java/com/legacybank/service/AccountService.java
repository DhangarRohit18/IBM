package com.legacybank.service;

import com.legacybank.domain.Account;
import com.legacybank.repository.AccountRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class AccountService {
    @Autowired
    private AccountRepository accountRepository;

    @Autowired
    private FraudService fraudService;

    public Account processTransfer(String fromAcc, String toAcc, double amount) {
        Account source = accountRepository.findByAccountNumber(fromAcc);
        Account target = accountRepository.findByAccountNumber(toAcc);

        // Fraud check
        if (fraudService.isFraudulent(source, amount)) {
            throw new RuntimeException("Fraud detected");
        }

        // Rule 1: Validation - Blocked Account Guard
        if (source.getStatus() == AccountStatus.BLOCKED) {
            throw new IllegalStateException("Account is blocked");
        }

        // Rule 2: Validation - Insufficient Balance
        if (source.getBalance() < amount) {
            throw new IllegalArgumentException("Insufficient balance");
        }

        // Rule 3: Calculation - Transfer Fee
        double fee = amount * 0.02;

        // Rule 4: Threshold Check - High Value Transfer
        if (amount > 50000) {
            requireManagerApproval(source, amount);
            // Rule 5: State Transition
            source.setStatus(AccountStatus.PENDING_APPROVAL);
            return accountRepository.save(source);
        }

        // Action - Notification
        sendTransferNotification(source, amount);

        source.setBalance(source.getBalance() - amount - fee);
        target.setBalance(target.getBalance() + amount);

        // Rule 5: State Transition - Completed
        source.setStatus(AccountStatus.COMPLETED);
        accountRepository.save(source);
        return accountRepository.save(target);
    }

    private void requireManagerApproval(Account account, double amount) {
        System.out.println("Manager approval required for amount: " + amount);
    }

    private void sendTransferNotification(Account account, double amount) {
        System.out.println("Notification sent for transfer amount: " + amount);
    }
}