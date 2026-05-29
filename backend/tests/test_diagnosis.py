import pytest
from app.agents.agronomist import AgronomistAgent


@pytest.mark.asyncio
async def test_agronomist_diagnose():
    agent = AgronomistAgent()
    result = await agent.diagnose(
        query="Daun cabai menguning bagian bawah",
        crop_type="chili",
    )
    assert "diagnosis" in result
    assert "possible_causes" in result
    assert "recommended_actions" in result
    assert "confidence_score" in result
    assert len(result["follow_up_questions"]) > 0


@pytest.mark.asyncio
async def test_yellow_leaves_diagnosis():
    agent = AgronomistAgent()
    result = await agent.diagnose("Daun tanaman menguning dan pertumbuhan terhambat")
    assert result["confidence_score"] > 0


@pytest.mark.asyncio
async def test_spots_diagnosis():
    agent = AgronomistAgent()
    result = await agent.diagnose("Ada bercak coklat pada daun tomat")
    assert result["confidence_score"] > 0
