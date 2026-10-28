"""Frozen LaBraM representations (WORKPLAN Phase 5).

What happens here
-----------------
1. `load_labram` builds the LaBraM-base network exactly as the authors' fine-tuning script does
   (`external/LaBraM/run_class_finetuning.py` with the README flags) and loads the pretrained
   weights from `checkpoints/labram-base.pth`. The model is frozen (eval mode, no gradients).
   With `random_init=True` the same architecture is returned with untrained weights: the
   negative control used later (T5.4.4).
2. `input_chans` maps our 16 canonical channel names onto LaBraM's channel vocabulary
   (`utils.standard_1020`), which supplies the per-channel positional embedding.
3. `extract` feeds preprocessed epochs (n, 16, 800) in microvolts through the model in batches
   and records, for every transformer block, the mean over patch tokens and the CLS token, plus
   the model's own final pooled feature (fc_norm of the mean). Layer choice is made later, inside
   training folds, so all 12 layers are kept.
4. `pool_participant` turns a participant's epoch embeddings into one vector (mean or median;
   D-018). Choice is also made inside training folds.

Conventions confirmed from the LaBraM code (T5.1.3, 2026-10-28)
- input tensor [batch, channels, patches, 200] at 200 Hz, i.e. 1-s patches;
- amplitude: microvolts divided by 100 (`engine_for_finetuning.py`, line 64);
- channel names upper-case; the pretraining/fine-tuning sets use the old names T3/T4/T5/T6;
- `input_chans = [0] + [standard_1020.index(name) + 1 ...]` (0 is the CLS slot);
- checkpoint dict key 'model', parameter names prefixed 'student.'; head and
  relative_position_index entries are dropped before loading;
- model flags (README): abs_pos_emb=True, rel_pos_bias=False, qkv_bias=False, layer-scale init
  0.1, mean pooling; dropout and drop-path set to 0 because the model is only run frozen.
"""
import sys
from collections import OrderedDict
from pathlib import Path

import numpy as np
import torch

# Our canonical (old 10-20) names -> LaBraM vocabulary entries. LaBraM lists both old and new
# temporal names; the fine-tuning datasets (TUAB/TUEV) use the old ones, so we do too.
LABRAM_NAMES = {"Fp1": "FP1", "Fp2": "FP2", "F7": "F7", "F3": "F3", "F4": "F4", "F8": "F8",
                "T3": "T3", "C3": "C3", "C4": "C4", "T4": "T4", "T5": "T5", "P3": "P3", "P4": "P4",
                "T6": "T6", "O1": "O1", "O2": "O2"}
SCALE = 1.0 / 100.0          # microvolts -> LaBraM input units
PATCH = 200                  # samples per patch (1 s at 200 Hz)


def _import_labram(repo_dir):
    """Make the LaBraM model definition importable (the repository is a flat set of modules).

    Only `modeling_finetune` is imported (it registers `labram_*` with timm). The repository's
    `utils.py` pulls in training-only dependencies (h5py, tensorboard), so its channel vocabulary
    is read from the source text instead (see `standard_1020`)."""
    repo_dir = str(Path(repo_dir).resolve())
    if repo_dir not in sys.path:
        sys.path.insert(0, repo_dir)
    import modeling_finetune  # noqa: F401


def standard_1020(repo_dir):
    """LaBraM's channel vocabulary, parsed from the `standard_1020 = [...]` literal in utils.py."""
    import ast
    src = (Path(repo_dir) / "utils.py").read_text(encoding="utf-8")
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "standard_1020" for t in node.targets):
            return ast.literal_eval(node.value)
    raise RuntimeError("standard_1020 not found in LaBraM utils.py")


def input_chans(ch_names, repo_dir):
    """LaBraM channel indices for our channel order: [0 (CLS)] + vocabulary index + 1 per channel
    (same construction as `utils.get_input_chans` in the LaBraM repository)."""
    vocab = standard_1020(repo_dir)
    return [0] + [vocab.index(LABRAM_NAMES[c]) + 1 for c in ch_names]


def load_labram(repo_dir, checkpoint=None, device="cpu", random_init=False):
    """Build LaBraM-base as in the authors' fine-tuning script and load the pretrained weights.

    Returns (model, report) where report lists any *unexplained* missing/unexpected keys (empty
    when loading went as the authors' script expects, T5.1.4) and how many tensors were loaded."""
    _import_labram(repo_dir)
    from timm.models import create_model

    model = create_model(
        "labram_base_patch200_200", pretrained=False, num_classes=1,
        drop_rate=0.0, drop_path_rate=0.0, attn_drop_rate=0.0, drop_block_rate=None,
        # README fine-tuning flags: --abs_pos_emb --disable_rel_pos_bias --disable_qkv_bias,
        # layer_scale_init_value 0.1 (default), use_mean_pooling (default). Dropout off: frozen use.
        use_mean_pooling=True, init_scale=0.001, use_rel_pos_bias=False,
        use_abs_pos_emb=True, init_values=0.1, qkv_bias=False,
    )
    report = {"missing": [], "unexpected": []}
    if not random_init:
        # The checkpoint stores a numpy scalar alongside the tensors (training metadata), which the
        # safe unpickler rejects by default; allow just that type rather than disabling weights_only.
        # Besides the weights, the file holds the training arguments (argparse.Namespace) and a
        # numpy scalar; both are plain data classes, so they are allow-listed by name.
        import argparse
        import numpy._core.multiarray
        import numpy.dtypes
        allowed = [(numpy._core.multiarray.scalar, "numpy.core.multiarray.scalar"),   # name used by numpy 1.x pickles
                   numpy._core.multiarray.scalar, numpy.dtype, argparse.Namespace,
                   numpy.dtypes.Float64DType, numpy.dtypes.Float32DType, numpy.dtypes.Int64DType]
        with torch.serialization.safe_globals(allowed):
            ckpt = torch.load(checkpoint, map_location="cpu", weights_only=True)
        state = ckpt["model"] if "model" in ckpt else ckpt
        new = OrderedDict()
        for k, v in state.items():
            if k.startswith("student."):          # pretraining wrapper prefix
                k = k[len("student."):]
            if "relative_position_index" in k or k.startswith("head."):
                continue
            new[k] = v
        res = model.load_state_dict(new, strict=False)
        # Expected differences between the pretraining checkpoint and the fine-tuning architecture
        # (the authors' script tolerates the same ones):
        #  - missing fc_norm.*: the LayerNorm applied to the mean-pooled tokens is created at
        #    fine-tuning time and has no pretrained weights; here it stays at its default
        #    (weight 1, bias 0), i.e. the 'pooled' feature is a plain layer-normalised mean;
        #  - unexpected: pretraining heads (lm_head, projection_head, logit_scale, mask_token)
        #    and the pretraining final norm, which the mean-pooling model replaces by Identity.
        expected_missing = {"fc_norm.weight", "fc_norm.bias"}
        expected_unexpected_prefixes = ("lm_head.", "projection_head.", "logit_scale", "mask_token", "norm.")
        report["missing"] = [k for k in res.missing_keys if not k.startswith("head.") and k not in expected_missing]
        report["unexpected"] = [k for k in res.unexpected_keys if not k.startswith(expected_unexpected_prefixes)]
        report["loaded"] = len(new) - len(res.unexpected_keys)
    model.eval()
    for p in model.parameters():
        p.requires_grad_(False)
    return model.to(device), report


def _hooks(model, store):
    """Register forward hooks that save each block's output tokens."""
    handles = []
    for i, blk in enumerate(model.blocks):
        handles.append(blk.register_forward_hook(lambda m, inp, out, i=i: store.__setitem__(i, out)))
    return handles


@torch.no_grad()
def extract(model, X, chans, device="cpu", batch_size=64):
    """Embeddings for epochs X (n, n_channels, 800) in microvolts.

    Returns dict of float32 arrays:
      layer_mean (n_layers, n, d): mean over the patch tokens (CLS excluded) after each block;
      layer_cls  (n_layers, n, d): the CLS token after each block;
      pooled     (n, d):          the model's own feature = fc_norm(mean of final patch tokens).
    """
    n_layers, d = len(model.blocks), model.embed_dim
    out_mean = np.empty((n_layers, len(X), d), np.float32)
    out_cls = np.empty((n_layers, len(X), d), np.float32)
    pooled = np.empty((len(X), d), np.float32)
    store = {}
    handles = _hooks(model, store)
    try:
        for s in range(0, len(X), batch_size):
            xb = torch.as_tensor(X[s:s + batch_size], dtype=torch.float32, device=device) * SCALE
            b, c, t = xb.shape
            xb = xb.reshape(b, c, t // PATCH, PATCH)          # [B, N, A, 200] as in the authors' engine
            store.clear()
            feat = model.forward_features(xb, input_chans=chans)   # (B, d), fc_norm applied
            pooled[s:s + b] = feat.float().cpu().numpy()
            for i in range(n_layers):
                tok = store[i]                                  # (B, 1 + N*A, d)
                out_cls[i, s:s + b] = tok[:, 0].float().cpu().numpy()
                out_mean[i, s:s + b] = tok[:, 1:].mean(1).float().cpu().numpy()
    finally:
        for h in handles:
            h.remove()
    return {"layer_mean": out_mean, "layer_cls": out_cls, "pooled": pooled}


def pool_participant(Z, method="mean"):
    """One vector per participant from their epoch embeddings Z (n_epochs, d)."""
    if method == "mean":
        return Z.mean(axis=0)
    if method == "median":
        return np.median(Z, axis=0)
    raise ValueError(method)
