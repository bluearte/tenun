
import json
import logging
import os
import pathlib

import pydantic

from . import schemas


logger = logging.getLogger(__name__)


def save(filepath: str | os.PathLike[str], data: pydantic.BaseModel) -> None:
    """
    Save a preset as JSON.
    """
    pth = pathlib.Path(filepath)
    pth.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, "w", encoding="utf8") as obj:
        if hasattr(data, "model_dump"):
            data = data.model_dump()
        obj.write(json.dumps(data, indent=4))


def load(name_or_path: str, category: str = ""):
    """
    Load a preset by name or file path.
    """
    all_presets = get_presets()
    preset_raw = None
    data_models = []

    pth = pathlib.Path(name_or_path)
    if pth.is_file():
        preset_raw = _load(pth.as_posix())
        data_models = list({
            mod
            for cfg in all_presets
            if (not category or cfg["field_name"] == category)
            for mod in cfg["data_models"]
        })
    else:
        for preset_config in all_presets:
            if category and preset_config["field_name"] != category:
                continue
            if preset_config["name"] == name_or_path:
                preset_raw = _load(preset_config["path"])
                data_models = preset_config["data_models"]
                break

    if preset_raw is None:
        logger.error("Preset '%s' not found", name_or_path)
        raise FileNotFoundError(f"Preset '{name_or_path}' not found")

    try:
        preset_raw = _expand_preset(preset_raw, all_presets)
    except ValueError as exc:
        logger.error("Preset '%s' contains a circular reference: %s", name_or_path, exc)
        raise

    if not data_models:
        logger.error("Preset '%s' has no matching model", name_or_path)
        raise ValueError(f"Preset '{name_or_path}' has no matching model.")

    for data_mod in data_models:
        try:
            return data_mod.model_validate(preset_raw)
        except pydantic.ValidationError as exc:
            logger.debug("Failed to validate with %s: %s", data_mod.__name__, exc)

    logger.error("Preset '%s' failed all validations", name_or_path)
    raise ValueError(f"Preset '{name_or_path}' could not be validated.")


def get_presets():
    """
    Get all presets available.
    """
    env_mappings = _get_envs_mappings()
    presets = []
    seen_paths = set()

    for mappings in env_mappings:
        env_name = mappings.get("env")
        default_dir_name = mappings.get("default_dir")
        field_name = mappings.get("field_name")
        schms = mappings.get("data_models")

        for dirpath in _get_env(env_name, default_dir_name):
            directory = pathlib.Path(dirpath)
            if not directory.is_dir():
                continue

            real_path = directory.resolve().as_posix()
            if real_path in seen_paths:
                continue
            seen_paths.add(real_path)
            presets.extend(_find_files(directory, field_name, schms))

    return presets


def _get_env(env_name: str, default_dir_name: str) -> list[str]:
    """
    Resolve preset search paths.

    `default_dir_name` is only the built-in fallback. Custom preset collections can
    use any directory name by setting the corresponding environment variable.
    """
    current_root = pathlib.Path(__file__).resolve().parent.parent.parent
    default_dir = current_root.joinpath("presets", default_dir_name)
    paths = []

    if default_dir.is_dir():
        paths.append(default_dir.as_posix())

    env_value = os.getenv(env_name)
    if env_value:
        for item in env_value.split(os.pathsep):
            if item:
                paths.append(item)

    return paths


def _find_files(dirpath, field_name, data_models):
    presets = []
    directory = pathlib.Path(dirpath)
    if not directory.is_dir():
        return presets

    for file in sorted(directory.iterdir()):
        if not file.is_file():
            continue
        presets.append(
            {
                "name": file.stem,
                "path": file.as_posix(),
                "data_models": data_models,
                "field_name": field_name,
            }
        )

    return presets


def _get_envs_mappings():
    envs = [
        {
            "env": "TENUN_PRESET_PATH",
            "data_models": [schemas.Preset],
            "default_dir": "main",
            "field_name": "main",
        },
        {
            "env": "TENUN_SOURCE_PRESET_PATH",
            "data_models": [schemas.Image, schemas.Images],
            "default_dir": "sources",
            "field_name": "sources",
        },
        {
            "env": "TENUN_TARGET_PRESET_PATH",
            "data_models": [schemas.Image],
            "default_dir": "targets",
            "field_name": "target",
        },
        {
            "env": "TENUN_COLORSPACE_PRESET_PATH",
            "data_models": [schemas.Colorspace],
            "default_dir": "colorspaces",
            "field_name": "colorspace",
        },
        {
            "env": "TENUN_BURN_INS_PRESET_PATH",
            "data_models": [schemas.BurnIns],
            "default_dir": "burn-ins",
            "field_name": "burn_ins",
        },
        {
            "env": "TENUN_RESOLUTION_PRESET_PATH",
            "data_models": [schemas.Resolution],
            "default_dir": "resolutions",
            "field_name": "resolution",
        },
    ]
    return envs


def _load(pth):
    with open(pth, "r", encoding="utf8") as lobj:
        return json.load(lobj)


def _expand_preset(preset, mappings, seen=None):
    """
    Recursively replace preset references while guarding against circular references.
    """
    if seen is None:
        seen = set()

    if isinstance(preset, dict):
        expanded = {}
        for field_name, field_value in preset.items():
            matched = False
            for preset_config in mappings:
                if field_name != preset_config["field_name"]:
                    continue

                if field_value == preset_config["name"]:
                    resolved_path = preset_config["path"]
                    if resolved_path in seen:
                        raise ValueError(f"Circular preset reference detected: {resolved_path}")
                    seen.add(resolved_path)
                    try:
                        expanded[field_name] = _expand_preset(_load(resolved_path), mappings, seen)
                    finally:
                        seen.remove(resolved_path)
                    matched = True
                    break

                if isinstance(field_value, list):
                    resolved_items = []
                    for item in field_value:
                        if item == preset_config["name"]:
                            resolved_path = preset_config["path"]
                            if resolved_path in seen:
                                raise ValueError(f"Circular preset reference detected: {resolved_path}")
                            seen.add(resolved_path)
                            try:
                                resolved_items.append(_expand_preset(_load(resolved_path), mappings, seen))
                            finally:
                                seen.remove(resolved_path)
                        else:
                            resolved_items.append(_expand_preset(item, mappings, seen))
                    expanded[field_name] = resolved_items
                    matched = True
                    break

            if not matched:
                expanded[field_name] = _expand_preset(field_value, mappings, seen)

        return expanded

    if isinstance(preset, list):
        return [_expand_preset(item, mappings, seen) for item in preset]

    return preset
