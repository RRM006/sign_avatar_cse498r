"""Model A, A-GRU (design doc 04 §F-10): Bangla tokens → gloss tokens.

BiGRU encoder, Bahdanau (additive) attention, GRU decoder, greedy and beam decoding. Small enough to
train on the desktop CPU. Targets may start with tag tokens such as `<neg>` (config `tag_prefix`).
"""

from __future__ import annotations

import hashlib
import json

import torch
from torch import nn
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence

PAD, BOS, EOS, UNK = 0, 1, 2, 3
SPECIALS = ["<pad>", "<s>", "</s>", "<unk>"]
TAGS = ("neg", "q-wh", "q-yn")


def tag_token(tag: str) -> str:
    return f"<{tag}>"


def split_tags(tokens: list[str]) -> tuple[set[str], list[str]]:
    """Separate tag tokens (anywhere in the output) from gloss tokens."""
    tag_toks = {tag_token(t): t for t in TAGS}
    return {tag_toks[t] for t in tokens if t in tag_toks}, [t for t in tokens if t not in tag_toks]


class Vocab:
    def __init__(self, tokens: list[str]):
        self.itos = SPECIALS + sorted(set(tokens) - set(SPECIALS))
        self.stoi = {t: i for i, t in enumerate(self.itos)}

    def __len__(self) -> int:
        return len(self.itos)

    def encode(self, tokens: list[str]) -> list[int]:
        return [self.stoi.get(t, UNK) for t in tokens]

    def decode(self, ids: list[int]) -> list[str]:
        out = []
        for i in ids:
            if i == EOS:
                break
            if i not in (PAD, BOS):
                out.append(self.itos[i])
        return out


def vocab_hash(src: Vocab, tgt: Vocab) -> str:
    text = json.dumps({"src": src.itos, "tgt": tgt.itos}, ensure_ascii=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class Seq2Seq(nn.Module):
    def __init__(self, n_src: int, n_tgt: int, emb: int, enc_hidden: int, dec_hidden: int, attn: int,
                 dropout: float):
        super().__init__()
        self.src_emb = nn.Embedding(n_src, emb, padding_idx=PAD)
        self.tgt_emb = nn.Embedding(n_tgt, emb, padding_idx=PAD)
        self.encoder = nn.GRU(emb, enc_hidden, batch_first=True, bidirectional=True)
        self.bridge = nn.Linear(2 * enc_hidden, dec_hidden)
        self.att_enc = nn.Linear(2 * enc_hidden, attn, bias=False)
        self.att_dec = nn.Linear(dec_hidden, attn)
        self.att_v = nn.Linear(attn, 1, bias=False)
        self.decoder = nn.GRUCell(emb + 2 * enc_hidden, dec_hidden)
        self.out = nn.Linear(dec_hidden + 2 * enc_hidden + emb, n_tgt)
        self.drop = nn.Dropout(dropout)

    def encode(self, src: torch.Tensor, src_len: torch.Tensor):
        e = self.drop(self.src_emb(src))
        packed = pack_padded_sequence(e, src_len.cpu(), batch_first=True, enforce_sorted=False)
        out, h = self.encoder(packed)
        out, _ = pad_packed_sequence(out, batch_first=True, total_length=src.size(1))
        h0 = torch.tanh(self.bridge(torch.cat([h[0], h[1]], dim=-1)))
        return out, self.att_enc(out), src != PAD, h0

    def step(self, y_prev, h, enc_out, enc_proj, mask):
        """One decoder step: attention over the source with the previous state, then the GRU cell."""
        e = self.drop(self.tgt_emb(y_prev))
        scores = self.att_v(torch.tanh(enc_proj + self.att_dec(h).unsqueeze(1))).squeeze(-1)
        weights = torch.softmax(scores.masked_fill(~mask, -1e9), dim=-1)
        ctx = torch.bmm(weights.unsqueeze(1), enc_out).squeeze(1)
        h = self.decoder(torch.cat([e, ctx], dim=-1), h)
        return self.out(self.drop(torch.cat([h, ctx, e], dim=-1))), h

    def forward(self, src, src_len, tgt_in):
        """Teacher forcing: logits for every target position."""
        enc_out, enc_proj, mask, h = self.encode(src, src_len)
        logits = []
        for t in range(tgt_in.size(1)):
            lg, h = self.step(tgt_in[:, t], h, enc_out, enc_proj, mask)
            logits.append(lg)
        return torch.stack(logits, dim=1)


def count_params(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters())


@torch.no_grad()
def greedy_decode(model: Seq2Seq, src, src_len, max_len: int) -> list[list[int]]:
    model.eval()
    enc_out, enc_proj, mask, h = model.encode(src, src_len)
    y = torch.full((src.size(0),), BOS, dtype=torch.long)
    steps = []
    for _ in range(max_len):
        lg, h = model.step(y, h, enc_out, enc_proj, mask)
        y = lg.argmax(-1)
        steps.append(y)
    return torch.stack(steps, dim=1).tolist()


@torch.no_grad()
def beam_decode(model: Seq2Seq, src_ids: list[int], beam: int, max_len: int) -> list[int]:
    """Beam search for one sentence; finished hypotheses are ranked by mean log-probability."""
    model.eval()
    src = torch.tensor([src_ids])
    enc_out, enc_proj, mask, h = model.encode(src, torch.tensor([len(src_ids)]))
    live = [(0.0, [BOS], h)]
    done = []
    for _ in range(max_len):
        cands = []
        for lp, seq, hs in live:
            lg, h2 = model.step(torch.tensor([seq[-1]]), hs, enc_out, enc_proj, mask)
            top = torch.log_softmax(lg, -1)[0].topk(beam)
            for v, i in zip(top.values.tolist(), top.indices.tolist()):
                cands.append((lp + v, seq + [i], h2))
        cands.sort(key=lambda c: c[0], reverse=True)
        live = []
        for c in cands[:beam]:
            (done if c[1][-1] == EOS else live).append(c)
        if not live or len(done) >= beam:
            break
    done += live
    best = max(done, key=lambda c: c[0] / (len(c[1]) - 1))
    return best[1][1:]
