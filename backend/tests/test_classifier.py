"""Tests for ComponentClassifier ensuring evidence-backed classifications."""

from app.analysis_engine.classifier import ComponentClassifier
from app.analysis_engine.java_parser import ParsedTypeEntity, ParsedAnnotation
from app.models.code_entity import ComponentType


def test_classifier_controller():
    classifier = ComponentClassifier()
    entity = ParsedTypeEntity(
        name="AccountController",
        fully_qualified_name="com.legacybank.controller.AccountController",
        entity_type="CLASS",
        package_name="com.legacybank.controller",
        relative_file_path="src/main/java/com/legacybank/controller/AccountController.java",
        line_start=1,
        line_end=25,
        extends_name=None,
        implements_names=[],
        annotations=[ParsedAnnotation(name="RestController")],
        modifiers=["public"],
        fields=[],
        methods=[],
        imports=[],
    )
    comp_type, evidence = classifier.classify(entity)
    assert comp_type == ComponentType.CONTROLLER
    assert len(evidence) > 0
    assert any("Annotated with @Controller or @RestController" in e for e in evidence)
    # MANDATORY RULE: No confidence scores or percentages
    for item in evidence:
        assert "%" not in item
        assert "confidence" not in item.lower()


def test_classifier_service():
    classifier = ComponentClassifier()
    entity = ParsedTypeEntity(
        name="AccountService",
        fully_qualified_name="com.legacybank.service.AccountService",
        entity_type="CLASS",
        package_name="com.legacybank.service",
        relative_file_path="src/main/java/com/legacybank/service/AccountService.java",
        line_start=1,
        line_end=30,
        extends_name=None,
        implements_names=[],
        annotations=[ParsedAnnotation(name="Service")],
        modifiers=["public"],
        fields=[],
        methods=[],
        imports=[],
    )
    comp_type, evidence = classifier.classify(entity)
    assert comp_type == ComponentType.SERVICE
    assert any("Annotated with Spring @Service" in e for e in evidence)


def test_classifier_repository():
    classifier = ComponentClassifier()
    entity = ParsedTypeEntity(
        name="AccountRepository",
        fully_qualified_name="com.legacybank.repository.AccountRepository",
        entity_type="INTERFACE",
        package_name="com.legacybank.repository",
        relative_file_path="src/main/java/com/legacybank/repository/AccountRepository.java",
        line_start=1,
        line_end=15,
        extends_name=None,
        implements_names=[],
        annotations=[ParsedAnnotation(name="Repository")],
        modifiers=["public"],
        fields=[],
        methods=[],
        imports=[],
    )
    comp_type, evidence = classifier.classify(entity)
    assert comp_type == ComponentType.REPOSITORY
    assert any("Annotated with Spring @Repository" in e for e in evidence)


def test_classifier_entity():
    classifier = ComponentClassifier()
    entity = ParsedTypeEntity(
        name="Account",
        fully_qualified_name="com.legacybank.domain.Account",
        entity_type="CLASS",
        package_name="com.legacybank.domain",
        relative_file_path="src/main/java/com/legacybank/domain/Account.java",
        line_start=1,
        line_end=20,
        extends_name="BaseEntity",
        implements_names=[],
        annotations=[ParsedAnnotation(name="Entity")],
        modifiers=["public"],
        fields=[],
        methods=[],
        imports=[],
    )
    comp_type, evidence = classifier.classify(entity)
    assert comp_type == ComponentType.MODEL
    assert any("Annotated with JPA @Entity" in e for e in evidence)


def test_classifier_configuration():
    classifier = ComponentClassifier()
    entity = ParsedTypeEntity(
        name="AppConfig",
        fully_qualified_name="com.legacybank.config.AppConfig",
        entity_type="CLASS",
        package_name="com.legacybank.config",
        relative_file_path="src/main/java/com/legacybank/config/AppConfig.java",
        line_start=1,
        line_end=10,
        extends_name=None,
        implements_names=[],
        annotations=[ParsedAnnotation(name="Configuration")],
        modifiers=["public"],
        fields=[],
        methods=[],
        imports=[],
    )
    comp_type, evidence = classifier.classify(entity)
    assert comp_type == ComponentType.CONFIG


def test_classifier_utility():
    classifier = ComponentClassifier()
    entity = ParsedTypeEntity(
        name="CurrencyUtils",
        fully_qualified_name="com.legacybank.util.CurrencyUtils",
        entity_type="CLASS",
        package_name="com.legacybank.util",
        relative_file_path="src/main/java/com/legacybank/util/CurrencyUtils.java",
        line_start=1,
        line_end=15,
        extends_name=None,
        implements_names=[],
        annotations=[],
        modifiers=["public"],
        fields=[],
        methods=[],
        imports=[],
    )
    comp_type, evidence = classifier.classify(entity)
    assert comp_type == ComponentType.UTILITY
    assert any("indicates utility" in e for e in evidence)
