import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

spec_litellm = importlib.util.spec_from_file_location("litellm", ROOT / "litellm/__init__.py")
litellm = importlib.util.module_from_spec(spec_litellm)
spec_litellm.loader.exec_module(litellm)

spec_handler = importlib.util.spec_from_file_location(
    "vertex_handler", ROOT / "litellm/llms/vertex_ai/image_generation/image_generation_handler.py"
)
vertex_handler = importlib.util.module_from_spec(spec_handler)
spec_handler.loader.exec_module(vertex_handler)
VertexImageGeneration = vertex_handler.VertexImageGeneration

spec_cost = importlib.util.spec_from_file_location(
    "vertex_cost", ROOT / "litellm/llms/vertex_ai/cost_calculator.py"
)
vertex_cost = importlib.util.module_from_spec(spec_cost)
spec_cost.loader.exec_module(vertex_cost)
image_edit_cost = vertex_cost.image_edit_cost

spec_types = importlib.util.spec_from_file_location("types_utils", ROOT / "litellm/types/utils.py")
types_utils = importlib.util.module_from_spec(spec_types)
spec_types.loader.exec_module(types_utils)
ImageResponse = types_utils.ImageResponse
from openai.types.image import Image


def test_transform_image_edit_request():
    handler = VertexImageGeneration()
    req = handler.transform_image_edit_request(
        image_b64="image-data",
        prompt="edit",
        mask_b64="mask-data",
        optional_params={"sampleCount": 1},
    )
    instance = req["instances"][0]
    assert instance["prompt"] == "edit"
    assert instance["image"]["bytesBase64Encoded"] == "image-data"
    assert instance["mask"]["bytesBase64Encoded"] == "mask-data"


def test_image_edit_cost(monkeypatch):
    def fake_get_model_info(model, custom_llm_provider="vertex_ai"):
        return {"output_cost_per_image": 0.02}

    monkeypatch.setattr(litellm, "get_model_info", fake_get_model_info)
    resp = ImageResponse(data=[Image(b64_json="a"), Image(b64_json="b")])
    cost = image_edit_cost("imagen-3.0-edit-001", resp)
    assert cost == 0.04
