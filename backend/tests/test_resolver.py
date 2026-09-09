"""Tests for RelationshipResolver demonstrating conservative call resolution and source evidence preservation."""

from app.analysis_engine.java_parser import ParsedTypeEntity, ParsedField, ParsedMethod
from app.analysis_engine.resolver import RelationshipResolver
from app.models.code_relationship import RelationshipType


def test_resolver_inheritance_and_implements():
    resolver = RelationshipResolver()

    base = ParsedTypeEntity(
        name="BaseEntity",
        fully_qualified_name="com.legacybank.domain.BaseEntity",
        entity_type="CLASS",
        package_name="com.legacybank.domain",
        relative_file_path="src/main/java/com/legacybank/domain/BaseEntity.java",
        line_start=1,
        line_end=10,
        extends_name=None,
        implements_names=[],
        annotations=[],
        modifiers=["public"],
        fields=[],
        methods=[],
        imports=[],
    )
    acc = ParsedTypeEntity(
        name="Account",
        fully_qualified_name="com.legacybank.domain.Account",
        entity_type="CLASS",
        package_name="com.legacybank.domain",
        relative_file_path="src/main/java/com/legacybank/domain/Account.java",
        line_start=1,
        line_end=20,
        extends_name="BaseEntity",
        implements_names=[],
        annotations=[],
        modifiers=["public"],
        fields=[],
        methods=[],
        imports=[],
    )

    fraud_if = ParsedTypeEntity(
        name="FraudService",
        fully_qualified_name="com.legacybank.service.FraudService",
        entity_type="INTERFACE",
        package_name="com.legacybank.service",
        relative_file_path="src/main/java/com/legacybank/service/FraudService.java",
        line_start=1,
        line_end=10,
        extends_name=None,
        implements_names=[],
        annotations=[],
        modifiers=["public"],
        fields=[],
        methods=[],
        imports=[],
    )
    fraud_impl = ParsedTypeEntity(
        name="FraudServiceImpl",
        fully_qualified_name="com.legacybank.service.FraudServiceImpl",
        entity_type="CLASS",
        package_name="com.legacybank.service",
        relative_file_path="src/main/java/com/legacybank/service/FraudServiceImpl.java",
        line_start=1,
        line_end=20,
        extends_name=None,
        implements_names=["FraudService"],
        annotations=[],
        modifiers=["public"],
        fields=[],
        methods=[],
        imports=[],
    )

    entities = [base, acc, fraud_if, fraud_impl]
    relationships = resolver.resolve_relationships(entities)
    types = [r.relationship_type for r in relationships]

    assert RelationshipType.EXTENDS in types
    assert RelationshipType.IMPLEMENTS in types

    extends_rel = next(r for r in relationships if r.relationship_type == RelationshipType.EXTENDS)
    assert extends_rel.target_entity_name == "com.legacybank.domain.BaseEntity"
    assert extends_rel.is_resolved is True

    impl_rel = next(r for r in relationships if r.relationship_type == RelationshipType.IMPLEMENTS)
    assert impl_rel.target_entity_name == "com.legacybank.service.FraudService"
    assert impl_rel.is_resolved is True


def test_resolver_conservative_calls_resolution():
    resolver = RelationshipResolver()

    repo = ParsedTypeEntity(
        name="AccountRepository",
        fully_qualified_name="com.legacybank.repository.AccountRepository",
        entity_type="INTERFACE",
        package_name="com.legacybank.repository",
        relative_file_path="src/main/java/com/legacybank/repository/AccountRepository.java",
        line_start=1,
        line_end=15,
        extends_name=None,
        implements_names=[],
        annotations=[],
        modifiers=["public"],
        fields=[],
        methods=[
            ParsedMethod(
                name="findByAccountNumber",
                return_type="Account",
                parameters=[{"type": "String", "name": "accNumber"}],
                modifiers=["public"],
                annotations=[],
                is_constructor=False,
                line_start=5,
                line_end=5,
            )
        ],
        imports=[],
    )

    svc = ParsedTypeEntity(
        name="AccountService",
        fully_qualified_name="com.legacybank.service.AccountService",
        entity_type="CLASS",
        package_name="com.legacybank.service",
        relative_file_path="src/main/java/com/legacybank/service/AccountService.java",
        line_start=1,
        line_end=35,
        extends_name=None,
        implements_names=[],
        annotations=[],
        modifiers=["public"],
        fields=[
            ParsedField(
                name="accountRepository",
                field_type="AccountRepository",
                modifiers=["private"],
                annotations=[],
                line_start=10,
                line_end=10,
            )
        ],
        methods=[
            ParsedMethod(
                name="transfer",
                return_type="Account",
                parameters=[],
                modifiers=["public"],
                annotations=[],
                is_constructor=False,
                line_start=15,
                line_end=30,
                method_invocations=[
                    {
                        "target_expression": "accountRepository",
                        "method_name": "findByAccountNumber",
                        "line_number": 18,
                    },
                    {
                        "target_expression": "unknownTarget",
                        "method_name": "ambiguousMethod",
                        "line_number": 25,
                    },
                ],
            )
        ],
        imports=[],
    )

    entities = [repo, svc]
    relationships = resolver.resolve_relationships(entities)
    calls = [r for r in relationships if r.relationship_type == RelationshipType.CALLS]

    assert len(calls) == 2

    # Resolved call site
    resolved_call = next(r for r in calls if r.target_entity_name == "com.legacybank.repository.AccountRepository")
    assert resolved_call.is_resolved is True
    assert resolved_call.line_number == 18

    # Unresolved/ambiguous call site
    unresolved_call = next(r for r in calls if r.is_resolved is False)
    assert unresolved_call.line_number == 25
    assert "Ambiguous method call site" in unresolved_call.evidence_reason
