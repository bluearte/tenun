import json
import pathlib

import pydantic

import tenun.schemas


def main():
    # current_file = pathlib.Path(__file__).absolute()
    # preset_dir = current_file.parent.joinpath("generated_presets")

    # default_preset = tenun.schemas.Preset()
    # target_path = preset_dir.joinpath("default.json").as_posix()
    # with open(target_path, "w", encoding="utf8") as tgt:
    #     data = default_preset.model_dump()
    #     tgt.write(json.dumps(data, indent=4))

    # coord = tenun.schemas.Coordinate()
    # text = tenun.schemas.Text(value="SAMPLE TEXT", position=coord)
    # image = tenun.schemas.Image(burn_ins=[text])
    # preset = tenun.schemas.Preset(target=image)
    # target_path = preset_dir.joinpath("default_burnins.json").as_posix()
    # with open(target_path, "w", encoding="utf8") as tgt:
    #     data = preset.model_dump()
    #     tgt.write(json.dumps(data, indent=4))

    # text = tenun.schemas.Text(value="TEXT")
    # line = tenun.schemas.Line()
    # box = tenun.schemas.Box()
    # burnins = tenun.schemas.BurnIns([text, line, box])

    # burn_ins_path = preset_dir.joinpath("box-line-text.json").as_posix()
    # with open(burn_ins_path, "w", encoding="utf8") as obj:
    #     data = burnins.model_dump()
    #     obj.write(json.dumps(data,indent=4))

    mdl = [{'resolution': {'width': {'value': 0, 'scale': 1, 'description': 'if value is 0, it will use image native resolution.'}, 'height': {'value': 0, 'scale': 1, 'description': 'if value is 0, it will use image native resolution. '}}, 'position': {'x': {'value': 0, 'scale': 1}, 'y': {'value': 0, 'scale': 1}}, 'colorspace': {'fromspace': 'ACEScg', 'tospace': 'sRGB'}, 'burn_ins': [{'type': 'text', 'value': '{FRAME:05d}'}]}]

    for mod in [tenun.schemas.Image, tenun.schemas.Images]:
        print(mod.__name__)
        try:
            return mod.model_validate(mdl)
        except pydantic.ValidationError:
            pass


if __name__ == "__main__":
    print(main())
