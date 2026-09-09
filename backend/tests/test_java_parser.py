"""Tests for deterministic Java AST Parser using javalang 0.13.0."""

from pathlib import Path
import pytest
from app.analysis_engine.java_parser import JavaASTParser

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "legacy_bank"


def test_java_parser_valid_file():
    parser = JavaASTParser()
    file_path = FIXTURES_DIR / "src/main/java/com/legacybank/service/AccountService.java"
    assert file_path.exists(), f"Fixture file not found at {file_path}"

    entities = parser.parse_file(file_path, "src/main/java/com/legacybank/service/AccountService.java")
    assert len(entities) == 1

    entity = entities[0]
    assert entity.name == "AccountService"
    assert entity.package_name == "com.legacybank.service"
    assert entity.fully_qualified_name == "com.legacybank.service.AccountService"
    assert entity.entity_type == "CLASS"
    assert "Service" in [a.name for a in entity.annotations]

    # Verify fields
    assert len(entity.fields) == 2
    field_names = [f.name for f in entity.fields]
    assert "accountRepository" in field_names
    assert "fraudService" in field_names

    # Verify methods
    assert len(entity.methods) >= 1
    method = next(m for m in entity.methods if m.name == "processTransfer")
    assert method.name == "processTransfer"
    assert method.return_type == "Account"
    assert len(method.parameters) == 3

    # Verify method invocations extracted
    assert len(method.method_invocations) > 0
    inv_methods = [inv["method_name"] for inv in method.method_invocations]
    assert "findByAccountNumber" in inv_methods
    assert "isFraudulent" in inv_methods


def test_java_parser_inheritance_and_annotations():
    parser = JavaASTParser()
    file_path = FIXTURES_DIR / "src/main/java/com/legacybank/domain/Account.java"
    entities = parser.parse_file(file_path, "src/main/java/com/legacybank/domain/Account.java")

    assert len(entities) == 1
    entity = entities[0]
    assert entity.name == "Account"
    assert entity.extends_name == "BaseEntity"
    assert "Entity" in [a.name for a in entity.annotations]


def test_java_parser_interface_and_implementation():
    parser = JavaASTParser()

    # Test Interface
    if_path = FIXTURES_DIR / "src/main/java/com/legacybank/service/FraudService.java"
    if_entities = parser.parse_file(if_path, "src/main/java/com/legacybank/service/FraudService.java")
    assert if_entities[0].entity_type == "INTERFACE"

    # Test Implementation
    impl_path = FIXTURES_DIR / "src/main/java/com/legacybank/service/FraudServiceImpl.java"
    impl_entities = parser.parse_file(impl_path, "src/main/java/com/legacybank/service/FraudServiceImpl.java")
    assert "FraudService" in impl_entities[0].implements_names


def test_java_parser_malformed_file_resilience():
    parser = JavaASTParser()
    malformed_path = FIXTURES_DIR / "src/main/java/com/legacybank/Malformed.java"

    # Must safely return empty list or parsed entities without throwing unhandled exception
    entities = parser.parse_file(malformed_path, "src/main/java/com/legacybank/Malformed.java")
    assert isinstance(entities, list)
