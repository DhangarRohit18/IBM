"""
Unit tests for Phase 4 AI Gateway abstraction and safety.
"""

import pytest
from app.ai.gateway import AIGateway
from app.ai.providers.mock_provider import MockAIProvider


@pytest.mark.asyncio
async def test_ai_gateway_explanation_with_mock_provider():
    gateway = AIGateway(provider=MockAIProvider())
    context = {
        "rule_type": "THRESHOLD",
        "title": "Threshold check: amount > 50000",
        "condition_expression": "amount > 50000",
        "action_expression": "requireManagerApproval()",
        "threshold_value": "50000",
        "threshold_operator": ">",
        "file": "TransferService.java",
        "lines": "67-69",
    }

    success, explanation = await gateway.generate_rule_explanation(context)
    assert success is True
    assert "Business Logic Summary" in explanation
    assert "50000" in explanation


def test_ai_gateway_secret_redaction():
    gateway = AIGateway(provider=MockAIProvider())
    sensitive_context = {
        "rule_type": "VALIDATION",
        "condition_expression": "apiKey = 'secret_token_12345'",
        "action_expression": "authenticate()",
        "password": "my_password_xyz",
    }

    sanitized = gateway._redact_secrets_from_context(sensitive_context)
    assert "[REDACTED_SECRET]" in sanitized["condition_expression"]
    assert sanitized["password"] == "[REDACTED_SECRET]"
