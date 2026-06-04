from apps.generation.prompting import build_prompt_hash, normalize_generation_payload


def test_normalize_generation_payload_trims_and_sorts():
    payload = {
        "b": "  hello   world ",
        "a": {"z": " two ", "y": ["  x  ", "y"]},
    }

    normalized = normalize_generation_payload(payload)

    assert list(normalized.keys()) == ["a", "b"]
    assert normalized["b"] == "hello world"
    assert normalized["a"]["z"] == "two"
    assert normalized["a"]["y"] == ["x", "y"]


def test_build_prompt_hash_is_stable_for_equivalent_payloads():
    left = {"text": "Hello   world", "items": [" a ", "b"]}
    right = {"items": ["a", "b"], "text": "Hello world"}

    assert build_prompt_hash(left) == build_prompt_hash(right)
