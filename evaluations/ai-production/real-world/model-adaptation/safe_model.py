"""Bounded safetensors/llama preflight for the optional native MLX evaluation.

This inspects bytes and configuration; it does not execute/load a model or
authenticate rights. Native model loading is a separate explicitly chosen step.
"""
from pathlib import Path
import hashlib
import json
import math
import struct

MAX_WEIGHTS = 320 * 1024 * 1024
MAX_HEADER = 2 * 1024 * 1024
DTYPES = {"F16": 2, "BF16": 2, "F32": 4, "U32": 4, "I32": 4}

def strict_json(raw):
    def pairs(items):
        out = {}
        for k, v in items:
            if k in out:
                raise ValueError("duplicate JSON key")
            out[k] = v
        return out
    value = json.loads(raw, object_pairs_hook=pairs,
                       parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite JSON")))
    def finite(v):
        if isinstance(v, float) and not math.isfinite(v):
            raise ValueError("nonfinite JSON")
        if isinstance(v, dict):
            for child in v.values(): finite(child)
        elif isinstance(v, list):
            for child in v: finite(child)
    finite(value)
    return value

def file_pin(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError("regular unlinked model file required")
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return {"name": path.name, "bytes": path.stat().st_size, "sha256": h.hexdigest()}

def inspect_weights(path, *, expected_sha256=None):
    path = Path(path)
    if path.suffix != ".safetensors" or path.is_symlink() or not path.is_file():
        raise ValueError("only a regular safetensors file is admitted")
    size = path.stat().st_size
    if not 8 < size <= MAX_WEIGHTS:
        raise ValueError("weights file size outside bounded route")
    with path.open("rb") as f:
        n = struct.unpack("<Q", f.read(8))[0]
        if not 2 <= n <= MAX_HEADER or n + 8 >= size:
            raise ValueError("invalid or excessive safetensors header")
        header = strict_json(f.read(n))
    if not isinstance(header, dict) or len(header) > 5000:
        raise ValueError("invalid tensor map")
    spans, parameters = [], 0
    for name, tensor in header.items():
        if name == "__metadata__":
            # Native MLX saves an optional metadata:null header. It contains no
            # executable content; non-null metadata must still be string pairs.
            if tensor is None:
                continue
            if not isinstance(tensor, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in tensor.items()):
                raise ValueError("metadata must contain strings only")
            continue
        if not isinstance(name, str) or not name or "/" in name or "\\" in name or ".." in name:
            raise ValueError("invalid tensor name")
        if not isinstance(tensor, dict) or set(tensor) != {"dtype", "shape", "data_offsets"}:
            raise ValueError("invalid tensor declaration")
        shape, offsets, dtype = tensor["shape"], tensor["data_offsets"], tensor["dtype"]
        if dtype not in DTYPES or not isinstance(shape, list) or not 1 <= len(shape) <= 4:
            raise ValueError("unsupported dtype or rank")
        if not all(type(x) is int and 1 <= x <= 131072 for x in shape):
            raise ValueError("invalid tensor dimension")
        count = math.prod(shape); parameters += count
        if count > 32_000_000 or parameters > 160_000_000:
            raise ValueError("excessive tensor allocation")
        if not isinstance(offsets, list) or len(offsets) != 2 or not all(type(x) is int for x in offsets):
            raise ValueError("invalid tensor offsets")
        a, b = offsets
        if not 0 <= a < b <= size - 8 - n or b - a != count * DTYPES[dtype]:
            raise ValueError("tensor payload bounds mismatch")
        spans.append((a, b))
    spans.sort()
    if not spans or spans[0][0] != 0 or spans[-1][1] != size - 8 - n:
        raise ValueError("incomplete tensor payload")
    if any(a[1] != b[0] for a, b in zip(spans, spans[1:])):
        raise ValueError("overlapping or missing tensor spans")
    pin = file_pin(path)
    if expected_sha256 is not None and pin["sha256"] != expected_sha256:
        raise ValueError("weights SHA256 mismatch")
    return {**pin, "tensor_count": len(spans), "parameters": parameters, "header_bytes": n}

def inspect_directory(root, *, expected_sha256=None):
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise ValueError("regular model directory required")
    allowed = {"config.json", "tokenizer_config.json", "tokenizer.json", "special_tokens_map.json",
               "vocab.json", "merges.txt", "generation_config.json", "model.safetensors",
               "model.safetensors.index.json", "chat_template.jinja", "README.md"}
    if any(p.name not in allowed or p.is_symlink() or not p.is_file() for p in root.iterdir()):
        raise ValueError("unreviewed or linked extra model member")
    configs = []
    for name in ("config.json", "tokenizer_config.json"):
        path = root / name
        if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_HEADER:
            raise ValueError("missing or unsafe model configuration")
        config = strict_json(path.read_bytes())
        if config.get("auto_map"):
            raise ValueError("remote custom code is outside this native route")
        configs.append(config)
    config = configs[0]
    if config.get("model_type") != "llama" or config.get("architectures") != ["LlamaForCausalLM"]:
        raise ValueError("only the reviewed llama architecture is admitted")
    layers, hidden = config.get("num_hidden_layers"), config.get("hidden_size")
    if not (type(layers) is int and type(hidden) is int and 1 <= layers <= 32 and 1 <= hidden <= 1024):
        raise ValueError("architecture resource envelope exceeded")
    bounds = {"vocab_size": (1, 65536), "intermediate_size": (1, 4096),
              "num_attention_heads": (1, 16), "num_key_value_heads": (1, 16),
              "max_position_embeddings": (1, 65536)}
    for key, (minimum, maximum) in bounds.items():
        value = config.get(key)
        if type(value) is not int or not minimum <= value <= maximum:
            raise ValueError("architecture allocation bound exceeded: " + key)
    heads, kvheads = config["num_attention_heads"], config["num_key_value_heads"]
    if hidden % heads or heads % kvheads or kvheads > heads or config.get("rope_scaling"):
        raise ValueError("unreviewed attention/position configuration")
    for name in ("tokenizer.json", "vocab.json", "merges.txt", "special_tokens_map.json", "generation_config.json", "chat_template.jinja"):
        path = root / name
        if path.exists() and path.stat().st_size > 8 * 1024 * 1024:
            raise ValueError("tokenizer/configuration member too large")
    index = root / "model.safetensors.index.json"
    if index.exists():
        value = strict_json(index.read_bytes())
        if set(value.get("weight_map", {}).values()) != {"model.safetensors"}:
            raise ValueError("weight index references unreviewed shard/path")
    if any(x.suffix in {".bin", ".pkl", ".pickle", ".pt", ".pth", ".py"} for x in root.iterdir()):
        raise ValueError("executable serialization/custom code is not admitted")
    return {"architecture": "llama", "remote_custom_code": False,
            "weights": inspect_weights(root / "model.safetensors", expected_sha256=expected_sha256),
            "config": file_pin(root / "config.json"), "tokenizer_config": file_pin(root / "tokenizer_config.json"),
            "tokenizer": file_pin(root / "tokenizer.json")}
