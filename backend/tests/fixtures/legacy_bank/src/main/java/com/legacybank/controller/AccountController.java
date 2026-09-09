package com.legacybank.controller;
import com.legacybank.domain.Account;
import com.legacybank.service.AccountService;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.beans.factory.annotation.Autowired;

@RestController
@RequestMapping("/api/accounts")
public class AccountController {
    @Autowired
    private AccountService accountService;

    @PostMapping("/transfer")
    public Account transfer(String from, String to, double amount) {
        return accountService.transfer(from, to, amount);
    }
}