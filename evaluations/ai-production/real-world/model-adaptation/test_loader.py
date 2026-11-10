"""Generic malicious-header controls, not fabricated model/runtime evidence."""
import json
from pathlib import Path
import struct
import tempfile
import unittest
from safe_model import inspect_directory, inspect_weights, strict_json


def weights(path, *, metadata=None, tensor=None):
    header = {'weight': tensor or {'dtype': 'F16', 'shape': [1], 'data_offsets': [0, 2]},
              '__metadata__': metadata}
    raw = json.dumps(header).encode()
    path.write_bytes(struct.pack('<Q', len(raw)) + raw + b'\0\0')


class LoaderBoundaries(unittest.TestCase):
    def test_native_optional_null_metadata_and_unsafe_metadata(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'model.safetensors'
            weights(path)
            self.assertEqual(1, inspect_weights(path)['parameters'])
            weights(path, metadata={'unsafe': {'code': 'not data strings'}})
            with self.assertRaises(ValueError):
                inspect_weights(path)

    def test_wrong_sha_and_executable_format_and_symlink(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'model.safetensors'
            weights(path)
            with self.assertRaisesRegex(ValueError, 'SHA256'):
                inspect_weights(path, expected_sha256='0' * 64)
            linked = Path(temporary) / 'linked.safetensors'
            linked.symlink_to(path)
            with self.assertRaises(ValueError):
                inspect_weights(linked)
            binary = Path(temporary) / 'model.bin'
            weights(binary)
            with self.assertRaises(ValueError):
                inspect_weights(binary)

    def test_oversized_shape_and_invalid_span(self):
        for tensor in ({'dtype': 'F16', 'shape': [131072, 131072], 'data_offsets': [0, 2]},
                       {'dtype': 'F16', 'shape': [1], 'data_offsets': [0, 4]},
                       {'dtype': 'F16', 'shape': [True], 'data_offsets': [0, 2]}):
            with tempfile.TemporaryDirectory() as temporary:
                path = Path(temporary) / 'model.safetensors'
                weights(path, tensor=tensor)
                with self.assertRaises(ValueError):
                    inspect_weights(path)

    def test_strict_json_overflow_nested_nonfinite_and_duplicates(self):
        for raw in (b'{"x":1e999}', b'{"x":{"y":NaN}}', b'{"x":1,"x":2}'):
            with self.assertRaises(ValueError):
                strict_json(raw)

    def test_allocation_config_extra_shard_remote_code_and_index_escape(self):
        config = {'model_type': 'llama', 'architectures': ['LlamaForCausalLM'], 'num_hidden_layers': 1,
                  'hidden_size': 8, 'vocab_size': 16, 'intermediate_size': 16, 'num_attention_heads': 1,
                  'num_key_value_heads': 1, 'max_position_embeddings': 128}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            weights(root / 'model.safetensors')
            for name in ('tokenizer.json', 'tokenizer_config.json'):
                (root / name).write_text('{}')
            def write(value):
                (root / 'config.json').write_text(json.dumps(value))
            write(config)
            self.assertEqual('llama', inspect_directory(root)['architecture'])
            for changed in ({'intermediate_size': 1000000000}, {'vocab_size': 1000000000},
                            {'num_attention_heads': 3}, {'auto_map': {'AutoModel': 'unreviewed.module'}}):
                write({**config, **changed})
                with self.assertRaises(ValueError):
                    inspect_directory(root)
            write(config)
            (root / 'extra.safetensors').write_bytes(b'not loaded')
            with self.assertRaises(ValueError):
                inspect_directory(root)
            (root / 'extra.safetensors').unlink()
            (root / 'model.safetensors.index.json').write_text('{"weight_map":{"w":"../escape.safetensors"}}')
            with self.assertRaises(ValueError):
                inspect_directory(root)


if __name__ == '__main__':
    unittest.main()
