"""Layered YAML configuration.

    base.yaml <- env/<env>.yaml <- data/<data>.yaml <- `overrides` <- BDSL_DATA_ROOT / BDSL_WORK_DIR

The same code runs locally, on Kaggle and on Colab; only the env layer differs. `${project_root}` and
`${dotted.key}` references inside string values are resolved after merging, so a root changed by an
env var also moves every path built from it.

The config hash identifies the *experiment* settings: it leaves out `_meta`, the `paths` section and
any key ending in `_root` or `_dir`, so the same settings on two machines give the same hash.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

import yaml

from .paths import find_project_root

ENV_NAMES = ("local", "kaggle", "colab")
ENV_VAR_ROOTS = {"BDSL_DATA_ROOT": "data_root", "BDSL_WORK_DIR": "work_dir"}
_REF = re.compile(r"\$\{([^}]+)\}")


def detect_env() -> str:
    """BDSL_ENV if set, otherwise guess from the platform's own environment variables."""
    explicit = os.environ.get("BDSL_ENV")
    if explicit:
        return explicit
    if "KAGGLE_KERNEL_RUN_TYPE" in os.environ:
        return "kaggle"
    if "COLAB_RELEASE_TAG" in os.environ or "google.colab" in sys.modules:
        return "colab"
    return "local"


def deep_merge(base: dict, extra: dict) -> dict:
    """Merge `extra` into `base` in place (nested dicts merge, everything else is replaced)."""
    for key, value in extra.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            deep_merge(base[key], value)
        else:
            base[key] = copy.deepcopy(value)
    return base


def _read_yaml(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a mapping at the top level")
    return data


def _lookup(cfg: dict, dotted: str) -> Any:
    node: Any = cfg
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            raise KeyError(dotted)
        node = node[part]
    return node


def _interpolate(cfg: dict, builtins: dict[str, str], max_passes: int = 10) -> dict:
    def resolve(value: Any) -> Any:
        if isinstance(value, dict):
            return {k: resolve(v) for k, v in value.items()}
        if isinstance(value, list):
            return [resolve(v) for v in value]
        if isinstance(value, str):
            def sub(m: re.Match) -> str:
                name = m.group(1).strip()
                if name in builtins:
                    return builtins[name]
                try:
                    found = _lookup(cfg, name)
                except KeyError:
                    raise KeyError(f"Unknown config reference ${{{name}}}") from None
                return str(found)
            return _REF.sub(sub, value)
        return value

    for _ in range(max_passes):
        new = resolve(cfg)
        if new == cfg:
            break
        cfg = new
    leftover = _REF.search(json.dumps(cfg, ensure_ascii=False))
    if leftover:
        raise ValueError(f"Unresolved or circular config reference: {leftover.group(0)}")
    return cfg


def _hashable_view(node: Any) -> Any:
    if isinstance(node, dict):
        return {
            k: _hashable_view(v)
            for k, v in node.items()
            if k not in ("_meta", "paths") and not k.endswith(("_root", "_dir"))
        }
    if isinstance(node, list):
        return [_hashable_view(v) for v in node]
    return node


def config_hash(cfg: dict) -> str:
    """SHA-256 of the machine-independent part of a resolved config (see module docstring)."""
    canonical = json.dumps(_hashable_view(cfg), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def load_config(
    env: str | None = None,
    data: str | None = None,
    overrides: dict | None = None,
    project_root: str | os.PathLike | None = None,
) -> dict:
    """Load and resolve the layered config. Returns a plain dict with a `_meta` section."""
    root = Path(project_root).resolve() if project_root else find_project_root()
    env = env or detect_env()
    if env not in ENV_NAMES:
        raise ValueError(f"Unknown env {env!r}; expected one of {ENV_NAMES}")
    config_dir = root / "configs"
    layers = [config_dir / "base.yaml", config_dir / "env" / f"{env}.yaml"]
    if data:
        layers.append(config_dir / "data" / f"{data}.yaml")
    for layer in layers:
        if not layer.is_file():
            raise FileNotFoundError(f"Missing config layer: {layer}")

    cfg: dict = {}
    for layer in layers:
        deep_merge(cfg, _read_yaml(layer))
    if overrides:
        deep_merge(cfg, overrides)
    used_env_vars = []
    for var, key in ENV_VAR_ROOTS.items():
        if os.environ.get(var):
            cfg.setdefault("paths", {})[key] = os.environ[var]
            used_env_vars.append(var)

    cfg = _interpolate(cfg, {"project_root": root.as_posix()})
    cfg["_meta"] = {
        "env": env,
        "data": data,
        "project_root": root.as_posix(),
        "layers": [layer.relative_to(root).as_posix() for layer in layers],
        "env_var_overrides": used_env_vars,
    }
    cfg["_meta"]["config_hash"] = config_hash(cfg)
    return cfg
