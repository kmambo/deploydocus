import json
import re
from itertools import permutations
from pathlib import Path
from typing import Any, Self, TextIO

import yaml

UPPER_FOLLOWED_BY_LOWER_RE = re.compile("(.)([A-Z][a-z]+)")
LOWER_OR_NUM_FOLLOWED_BY_UPPER_RE = re.compile("([a-z0-9])([A-Z])")


def quote(s: str):
    return f'"{s}"'


class FStr:
    def __init__(self, replacement):
        self.replacement = replacement

    def __repr__(self):
        return r'f"' + self.replacement + '"'

    def __sub__(self, other: Self):
        return FStr("-".join([self.replacement, other.replacement]))


def print_with_settings(
    obj_dict: dict[str, Any], save_to_file: TextIO | None = None, fstring=True
) -> None:
    mapping = (
        {
            "defaultchart": FStr("{self.pkg_settings.pkg_name}"),
            "chart-instance": FStr("{instance_settings.instance_name}"),
            "1.16.0": FStr("{self.pkg_settings.pkg_version}"),
            "0.1.0": FStr("{instance_settings.instance_version}"),
        }
        if fstring
        else {
            "defaultchart": "{chart_name}",
            "chart-instance": "{release_name}",
            "1.16.0": "{app_version}",
            "0.1.0": "{chart_version}",
        }
    )
    mapping_combine = {}
    key_perms = permutations(mapping.keys(), 2)
    for k1, k2 in list(key_perms):
        if k1 != k2:
            mapping_combine[f"{k1}-{k2}"] = (
                mapping[k1] - mapping[k2] if fstring else f"{mapping[k1]}-{mapping[k2]}"
            )

    json_str = json.dumps(obj_dict, sort_keys=True, separators=(",", ": "), indent=2)
    for k, v in mapping_combine.items():
        json_str = json_str.replace(quote(k), repr(v) if fstring else quote(str(v)))
    for k, v in mapping.items():
        json_str = json_str.replace(quote(k), repr(v) if fstring else quote(str(v)))
    # add replace for Helm
    json_str = json_str.replace('"Helm"', '"deploydocus"')
    if not save_to_file:
        print(json_str)
    else:
        save_to_file.writelines(json_str)


def check_object_with_dryrun(k8s_obj, fn_to_call): ...


def main(save_to_file: bool = True, fstring: bool = True):
    kinds = {}
    dir_ = Path(__file__).parent
    with open(dir_ / ".manifest.yaml", "rt") as f:
        all_k8s = yaml.safe_load_all(f)
        k8s: dict[str, Any]
        for k8s in all_k8s:
            if k8s["kind"] == "Pod":
                # skip the test
                continue
            group, _, version = k8s["apiVersion"].partition("/")
            if version == "":
                version = group
                # set group = "core" if needed
            # k8s = {to_snake(k): v for k, v in k8s.items()}
            kind = k8s["kind"]
            kinds[kind] = k8s
            # constructor = getattr(client, f"{version.capitalize()}{kind}")
            # constructor()
    for knd, templ in kinds.items():
        if save_to_file:
            with open(f"{knd.lower()}.json.template", "wt") as f:
                print_with_settings(templ, save_to_file=f, fstring=fstring)
        else:
            print_with_settings(kinds[knd], None, fstring=fstring)


if __name__ == "__main__":
    main()
