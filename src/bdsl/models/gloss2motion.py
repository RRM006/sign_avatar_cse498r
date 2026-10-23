"""Model B (design doc 04 §F-10): gloss (or Bangla word) tokens → motion frames, non-autoregressive.

Token embeddings → 3-layer Transformer encoder (d = 192, 4 heads) → a length head (log frame count).
Decoder: one query per output frame, built from a sinusoidal code of normalised time (0…1), 3 layers
that attend to each other and to the encoder → linear to the 208 feature values. All frames are
predicted at once (no frame-by-frame feedback, so no "frozen pose" drift). Training uses the true
length; inference uses the predicted length. Every tensor is created on the input's device, so the
model runs on CPU or CUDA (2026-10-23, owner-approved GPU support).
"""

from __future__ import annotations

import math

import torch
from torch import nn

from ..features.normalize import N_FEAT, PARTS

PAD = 0


def time_code(n_frames: torch.Tensor, t_max: int, dim: int, max_cycles: float = 128.0) -> torch.Tensor:
    """(B, t_max, dim) sinusoidal code of τ = t/(T−1) for each sequence's own length T, with
    frequencies from 1 to `max_cycles` cycles per clip (enough to tell neighbouring frames apart)."""
    dev = n_frames.device
    t = torch.arange(t_max, dtype=torch.float32, device=dev)[None, :]
    tau = t / (n_frames[:, None].float() - 1).clamp(min=1)
    cycles = torch.exp(torch.linspace(0.0, math.log(max_cycles), dim // 2, device=dev))
    ang = 2 * math.pi * tau[..., None] * cycles
    return torch.cat([torch.sin(ang), torch.cos(ang)], dim=-1)


class Gloss2Motion(nn.Module):
    def __init__(self, n_vocab: int, d: int, heads: int, enc_layers: int, dec_layers: int, ff: int,
                 dropout: float, max_tokens: int = 32):
        super().__init__()
        self.d = d
        self.tok = nn.Embedding(n_vocab, d, padding_idx=PAD)
        self.pos = nn.Embedding(max_tokens, d)
        enc = nn.TransformerEncoderLayer(d, heads, ff, dropout, batch_first=True)
        self.encoder = nn.TransformerEncoder(enc, enc_layers, enable_nested_tensor=False)
        self.length_head = nn.Sequential(nn.Linear(d, d), nn.ReLU(), nn.Linear(d, 1))
        self.query = nn.Linear(d, d)
        dec = nn.TransformerDecoderLayer(d, heads, ff, dropout, batch_first=True)
        self.decoder = nn.TransformerDecoder(dec, dec_layers)
        self.out = nn.Linear(d, N_FEAT)

    def encode(self, tokens: torch.Tensor):
        pad = tokens == PAD
        pos = torch.arange(tokens.size(1), device=tokens.device)[None]
        mem = self.encoder(self.tok(tokens) + self.pos(pos), src_key_padding_mask=pad)
        keep = (~pad).unsqueeze(-1).float()
        pooled = (mem * keep).sum(1) / keep.sum(1).clamp(min=1)
        return mem, pad, self.length_head(pooled).squeeze(-1)

    def decode(self, mem, pad, n_frames: torch.Tensor) -> torch.Tensor:
        t_max = int(n_frames.max())
        q = self.query(time_code(n_frames, t_max, self.d))
        frame_pad = torch.arange(t_max, device=n_frames.device)[None] >= n_frames[:, None]
        h = self.decoder(q, mem, tgt_key_padding_mask=frame_pad, memory_key_padding_mask=pad)
        return self.out(h)

    def forward(self, tokens, n_frames):
        """Training: frames for the given (true) lengths, plus the predicted log length."""
        mem, pad, log_len = self.encode(tokens)
        return self.decode(mem, pad, n_frames), log_len

    @torch.no_grad()
    def generate(self, tokens, max_frames: int) -> list[torch.Tensor]:
        """Inference: predicted length, then frames."""
        self.eval()
        mem, pad, log_len = self.encode(tokens)
        n = torch.exp(log_len).round().long().clamp(2, max_frames)
        out = self.decode(mem, pad, n)
        return [out[b, :n[b]] for b in range(len(n))]


def value_weights(hand_weight: float) -> torch.Tensor:
    w = torch.ones(N_FEAT)
    w[PARTS["lhand"]] = hand_weight
    w[PARTS["rhand"]] = hand_weight
    return w


def masked_loss(pred, target, value_mask, n_frames, log_len, weights, lambda_vel: float, lambda_len: float):
    """Masked L1 on positions + λ_v · masked L1 on frame-to-frame velocity + λ_len · |log length error|.
    `value_mask` (B, T, 208) is True only for present values inside each sequence; missing values and
    padding never contribute (their gradient is exactly zero)."""
    m = value_mask.float() * weights
    pos = (torch.abs(pred - target) * m).sum() / m.sum().clamp(min=1)
    mv = (value_mask[:, 1:] & value_mask[:, :-1]).float() * weights
    vel_err = torch.abs((pred[:, 1:] - pred[:, :-1]) - (target[:, 1:] - target[:, :-1]))
    vel = (vel_err * mv).sum() / mv.sum().clamp(min=1)
    length = torch.abs(log_len - torch.log(n_frames.float())).mean()
    total = pos + lambda_vel * vel + lambda_len * length
    return total, {"pos": pos.item(), "vel": vel.item(), "len": length.item()}
