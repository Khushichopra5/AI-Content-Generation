GENERATION_RESPONSE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "variants",
        "hashtags",
        "subject_lines",
        "cta_options",
        "image_prompt",
        "quality_notes",
    ],
    "properties": {
        "variants": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["variant_id", "headline", "body", "cta", "tone_score"],
                "properties": {
                    "variant_id": {"type": "string"},
                    "headline": {"type": "string"},
                    "body": {"type": "string"},
                    "cta": {"type": "string"},
                    "tone_score": {"type": "number"},
                },
            },
        },
        "hashtags": {
            "type": "array",
            "items": {"type": "string"},
        },
        "subject_lines": {
            "type": "array",
            "items": {"type": "string"},
        },
        "cta_options": {
            "type": "array",
            "items": {"type": "string"},
        },
        "image_prompt": {"type": "string"},
        "quality_notes": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
}
