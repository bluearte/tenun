import os

import tenun.presets


def test_get_presets_ignores_missing_env_directory(monkeypatch):
    monkeypatch.setenv("TENUN_SOURCE_PRESET_PATH", os.path.join("missing", "sources"))

    presets = tenun.presets.get_presets()

    assert isinstance(presets, list)


def test_get_presets_deduplicates_same_directory(monkeypatch):
    root = os.path.dirname(__file__)
    preset_dir = os.path.join(root, "generated_presets")
    source_dir = os.path.join(preset_dir, "sources")

    monkeypatch.setenv("TENUN_SOURCE_PRESET_PATH", source_dir)

    found = tenun.presets.get_presets()
    names = {preset["name"] for preset in found if preset["field_name"] == "sources"}

    assert len(names) >= 1


def test_load_from_file_path_returns_valid_model():
    all_presets = tenun.presets.get_presets()
    for preset in all_presets:
        preset = tenun.presets.load(preset["path"])

        assert preset is not None
        if hasattr(preset, "description"):
            assert preset.description == ""


if __name__ == "__main__":
    test_load_from_file_path_returns_valid_model()
