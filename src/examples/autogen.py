import json
from itertools import permutations
from pathlib import Path
from typing import Any, Self, TextIO

import yaml
from camel_converter import dict_to_snake
from kubernetes import client  # type: ignore


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
    obj_dict: dict[str, Any], save_to_file: TextIO | None = None
) -> None:
    mapping = {
        "defaultchart": FStr("{self.settings.chart_name}"),
        "chart-instance": FStr("{self.settings.release_name}"),
        "1.16.0": FStr("{self.settings.app_version}"),
        "0.1.0": FStr("{self.settings.chart_version}"),
    }
    mapping_combine = {}
    key_perms = permutations(mapping.keys(), 2)
    for k1, k2 in list(key_perms):
        if k1 != k2:
            mapping_combine[f"{k1}-{k2}"] = mapping[k1] - mapping[k2]

    json_str = json.dumps(obj_dict, sort_keys=True, separators=(",", ":"), indent=2)
    for k, v in mapping_combine.items():
        json_str = json_str.replace(quote(k), repr(v))
    for k, v in mapping.items():
        json_str = json_str.replace(quote(k), repr(v))
    if not save_to_file:
        print(json_str)
    else:
        save_to_file.writelines(json_str)


kube_objs: dict[str, Any] = {}
kinds = {}
dir_ = Path(__file__).parent
print(dir_)
with open(dir_ / ".manifest.yaml", "rt") as f:
    all_k8s = yaml.safe_load_all(f)
    for k8s in all_k8s:
        if k8s["kind"] == "Pod":
            continue
        kinds[k8s["kind"]] = dict_to_snake(k8s)
        constructor = getattr(client, f"V1{k8s['kind']}")
        kube_objs[k8s["kind"]] = constructor(**kinds[k8s["kind"]])
for knd in kube_objs.keys():
    with open(f"{knd}.py", "wt") as f:
        print_with_settings(kinds[knd], save_to_file=f)
