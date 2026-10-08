"""
ClaimGraph AI — Multimodal Analysis Tests.
"""

import pytest
from app.multimodal.provider import LocalMultimodalProvider
from app.multimodal.schemas import MultimodalAnalysisRequest


@pytest.mark.asyncio
async def test_multimodal_damage_analysis_consistent():
    """Verify standard damage analysis and narrative consistency."""
    provider = LocalMultimodalProvider()
    req = MultimodalAnalysisRequest(
        claim_id="CLM-DMG-01",
        claim_description="Accidentally dropped phone on concrete pavement, shattering front screen glass.",
        claim_amount=249.00,
        invoice_text="Repair invoice #8921: Front screen replacement and labor totaling $249.00",
    )

    result = await provider.analyze(req)
    assert result.claim_description_consistency is True
    assert len(result.visible_damage) > 0
    assert any("glass" in d.lower() or "screen" in d.lower() or "display" in d.lower() for d in result.visible_damage)
    assert result.confidence >= 0.80
    assert "corroborating evidence only" in result.evidence_disclaimer.lower()


@pytest.mark.asyncio
async def test_multimodal_inconsistency_detection():
    """Verify detection of inconsistencies between description and document."""
    provider = LocalMultimodalProvider()
    # Narrative says stolen, but invoice is for a cracked screen repair
    req = MultimodalAnalysisRequest(
        claim_id="CLM-MISMATCH-01",
        claim_description="Device was stolen out of my bag while on the subway.",
        claim_amount=950.00,
        invoice_text="Authorized store repair invoice: Screen crack fix totaling $150.00",
    )

    result = await provider.analyze(req)
    assert result.claim_description_consistency is False
    assert len(result.possible_inconsistencies) > 0
    assert any("diverges" in inc.lower() or "theft" in inc.lower() for inc in result.possible_inconsistencies)
