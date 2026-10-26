from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from src.ingestion.processor import process_file


TEXT_FILE_PATH = "data/tests/text.txt"
@pytest.mark.asyncio
@patch("src.ingestion.processor.vector_store_module.get_client")
async def test_process_file(mock_get_client):
    """Test for ingesting file"""
    mock_client = MagicMock()
    mock_client.upsert = AsyncMock(return_value=True)
    mock_get_client.return_value = mock_client

    value = await process_file(file_path=TEXT_FILE_PATH)
    assert value == True
