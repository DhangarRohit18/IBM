package com.legacybank.repository;
import com.legacybank.domain.Account;
import org.springframework.stereotype.Repository;

@Repository
public interface AccountRepository {
    Account findByAccountNumber(String accountNumber);
    Account save(Account account);
}