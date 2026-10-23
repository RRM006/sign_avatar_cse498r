"""Device choice for training (owner-approved GPU support, 2026-10-23).

`resolve_device("cuda")` gives CUDA when PyTorch can see a GPU and falls back to the CPU otherwise;
the fallback is recorded, never silent. `device_info()` is written into every run.json / env.json.
"""

from __future__ import annotations

import torch


def resolve_device(requested: str | None) -> tuple[torch.device, str]:
    """(device, note). requested: "cuda", "cpu", "auto" or None (= auto)."""
    req = (requested or "auto").lower()
    if req not in ("cuda", "cpu", "auto"):
        raise ValueError(f"device must be cuda, cpu or auto, got {requested!r}")
    if req == "cpu":
        return torch.device("cpu"), "cpu requested"
    if torch.cuda.is_available():
        return torch.device("cuda:0"), f"{req} requested; CUDA available"
    return torch.device("cpu"), f"{req} requested but CUDA is not available: running on CPU"


def device_info(device: torch.device | None = None) -> dict:
    """GPU name, CUDA/cuDNN versions and the device actually used."""
    info = {"torch": torch.__version__, "cuda_available": torch.cuda.is_available(),
            "torch_cuda_version": torch.version.cuda, "device": str(device) if device is not None else None,
            "gpu_count": torch.cuda.device_count() if torch.cuda.is_available() else 0, "gpu_names": [],
            "cudnn_version": None}
    if torch.cuda.is_available():
        info["gpu_names"] = [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())]
        try:
            info["cudnn_version"] = torch.backends.cudnn.version()
        except Exception:  # noqa: BLE001 — informational only
            info["cudnn_version"] = None
    return info


def rng_state(device: torch.device) -> dict:
    """RNG states needed for an exact resume (the CUDA state matters for dropout on the GPU)."""
    out = {"rng_torch": torch.get_rng_state()}
    if device.type == "cuda":
        out["rng_cuda"] = torch.cuda.get_rng_state(device)
    return out


def set_rng_state(ck: dict, device: torch.device) -> None:
    torch.set_rng_state(ck["rng_torch"])
    if device.type == "cuda" and "rng_cuda" in ck:
        torch.cuda.set_rng_state(ck["rng_cuda"], device)
