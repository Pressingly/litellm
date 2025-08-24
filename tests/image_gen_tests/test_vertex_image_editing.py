import pytest


@pytest.mark.skip(reason="Requires Vertex AI credentials")
def test_vertex_image_edit_integration():
    assert True
