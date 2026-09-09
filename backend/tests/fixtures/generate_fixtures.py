"""Script to generate test ZIP fixtures for Phase 2 and Phase 3 testing."""

import io
from pathlib import Path
import zipfile

fixtures_dir = Path(__file__).parent
fixtures_dir.mkdir(parents=True, exist_ok=True)

# LegacyBank source files mapping
LEGACY_BANK_FILES = {
    "pom.xml": """<project>
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.legacybank</groupId>
    <artifactId>legacy-bank</artifactId>
    <version>1.0.0</version>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
    </dependencies>
</project>""",

    "src/main/java/com/legacybank/domain/BaseEntity.java": """package com.legacybank.domain;
import java.time.LocalDateTime;

public abstract class BaseEntity {
    protected String id;
    protected LocalDateTime createdAt;

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
}""",

    "src/main/java/com/legacybank/domain/Account.java": """package com.legacybank.domain;
import javax.persistence.Entity;
import javax.persistence.Table;

@Entity
@Table(name = "accounts")
public class Account extends BaseEntity {
    private String accountNumber;
    private double balance;
    private String ownerName;

    public String getAccountNumber() { return accountNumber; }
    public double getBalance() { return balance; }
    public void setBalance(double balance) { this.balance = balance; }
}""",

    "src/main/java/com/legacybank/repository/AccountRepository.java": """package com.legacybank.repository;
import com.legacybank.domain.Account;
import org.springframework.stereotype.Repository;

@Repository
public interface AccountRepository {
    Account findByAccountNumber(String accountNumber);
    Account save(Account account);
}""",

    "src/main/java/com/legacybank/service/FraudService.java": """package com.legacybank.service;
import com.legacybank.domain.Account;

public interface FraudService {
    boolean isFraudulent(Account account, double amount);
}""",

    "src/main/java/com/legacybank/service/FraudServiceImpl.java": """package com.legacybank.service;
import com.legacybank.domain.Account;
import org.springframework.stereotype.Service;

@Service
public class FraudServiceImpl implements FraudService {
    @Override
    public boolean isFraudulent(Account account, double amount) {
        return amount > 10000.0;
    }
}""",

    "src/main/java/com/legacybank/service/AccountService.java": """package com.legacybank.service;
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

    public Account transfer(String fromAcc, String toAcc, double amount) {
        Account source = accountRepository.findByAccountNumber(fromAcc);
        if (fraudService.isFraudulent(source, amount)) {
            throw new RuntimeException("Fraud detected");
        }
        Account target = accountRepository.findByAccountNumber(toAcc);
        source.setBalance(source.getBalance() - amount);
        target.setBalance(target.getBalance() + amount);
        accountRepository.save(source);
        return accountRepository.save(target);
    }
}""",

    "src/main/java/com/legacybank/controller/AccountController.java": """package com.legacybank.controller;
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
}""",

    "src/main/java/com/legacybank/util/CurrencyUtils.java": """package com.legacybank.util;

public class CurrencyUtils {
    public static String formatUSD(double amount) {
        return String.format("$%.2f", amount);
    }
}""",

    "src/main/java/com/legacybank/config/AppConfig.java": """package com.legacybank.config;
import org.springframework.context.annotation.Configuration;

@Configuration
public class AppConfig {
}""",

    "src/main/java/com/legacybank/Malformed.java": """package com.legacybank;

public class Malformed {
    public void broken( {
"""
}

# 1. valid-legacybank-app.zip
buf_lb = io.BytesIO()
with zipfile.ZipFile(buf_lb, "w") as zf:
    for path, content in LEGACY_BANK_FILES.items():
        zf.writestr(path, content)
(fixtures_dir / "valid-legacybank-app.zip").write_bytes(buf_lb.getvalue())

# Write files directly to legacy_bank folder as well
lb_dir = fixtures_dir / "legacy_bank"
lb_dir.mkdir(parents=True, exist_ok=True)
for rel_path, content in LEGACY_BANK_FILES.items():
    dest = lb_dir / rel_path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")

# 2. valid-legacy-java.zip
buf1 = io.BytesIO()
with zipfile.ZipFile(buf1, "w") as zf:
    zf.writestr("src/com/bank/Account.java", "package com.bank;\npublic class Account { private String id; }")
    zf.writestr("src/com/bank/Transaction.java", "package com.bank;\npublic class Transaction { private double amount; }")
(fixtures_dir / "valid-legacy-java.zip").write_bytes(buf1.getvalue())

# 3. valid-spring-maven.zip
buf2 = io.BytesIO()
with zipfile.ZipFile(buf2, "w") as zf:
    zf.writestr("pom.xml", "<project><modelVersion>4.0.0</modelVersion><groupId>com.legacybank</groupId><artifactId>legacy-bank</artifactId><version>1.0.0</version><dependencies><dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-web</artifactId></dependency></dependencies></project>")
    zf.writestr("src/main/java/com/legacybank/Application.java", "package com.legacybank;\nimport org.springframework.boot.autoconfigure.SpringBootApplication;\n@SpringBootApplication\npublic class Application {}")
    zf.writestr("src/main/resources/application.properties", "server.port=8080\n")
(fixtures_dir / "valid-spring-maven.zip").write_bytes(buf2.getvalue())

# 4. valid-gradle.zip
buf3 = io.BytesIO()
with zipfile.ZipFile(buf3, "w") as zf:
    zf.writestr("build.gradle", 'plugins { id "org.springframework.boot" version "3.1.0" }')
    zf.writestr("src/main/java/com/example/Main.java", "package com.example;\npublic class Main {}")
(fixtures_dir / "valid-gradle.zip").write_bytes(buf3.getvalue())

# 5. malicious-zip-slip.zip
buf4 = io.BytesIO()
with zipfile.ZipFile(buf4, "w") as zf:
    zf.writestr("../evil.txt", "malicious path traversal content")
(fixtures_dir / "malicious-zip-slip.zip").write_bytes(buf4.getvalue())

print("Test fixtures generated successfully!")
