"""Exercise scalar ABI boundaries without claiming native Windows execution."""
import ctypes
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'native_windows_standard_user.py'
SPEC = importlib.util.spec_from_file_location('standard_user_scalar_probe', SOURCE)
probe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe)


class TokenScalarBoundaryTests(unittest.TestCase):
    def query(self, kind, payload, returned, success=True):
        win = object.__new__(probe.Windows)
        observed = []
        def get_information(token, actual_kind, output, capacity, length):
            observed.append(actual_kind)
            self.assertEqual(actual_kind, kind)
            self.assertEqual(capacity, 4)
            self.assertEqual(ctypes.addressof(output._obj) % ctypes.alignment(ctypes.c_uint32), 0)
            self.assertEqual(ctypes.string_at(output, 4), b'\0' * 4)
            ctypes.memmove(output, payload, len(payload))
            ctypes.cast(length, ctypes.POINTER(probe.W.DWORD)).contents.value = returned
            return success
        win.a = SimpleNamespace(GetTokenInformation=get_information)
        def checked(result, operation):
            if not result:
                raise OSError('Synthetic rejected SDK call: ' + operation)
        win.ok = checked
        return win, observed

    def test_one_byte_false_does_not_consume_undefined_nonzero_tail(self):
        win, calls = self.query(21, b'\x00\xa5\xa5\xa5', 1)
        self.assertFalse(win.token_boolean(None, 21))
        self.assertEqual(calls, [21])

    def test_one_byte_nonzero_restriction_is_true(self):
        win, _ = self.query(21, b'\x80\x00\x00\x00', 1)
        self.assertTrue(win.token_boolean(None, 21))

    def test_documented_four_byte_restriction_value_is_supported(self):
        win, _ = self.query(21, b'\x00\x01\x00\x00', 4)
        self.assertTrue(win.token_boolean(None, 21))

    def test_elevation_requires_its_complete_four_byte_structure(self):
        win, _ = self.query(20, b'\x01', 1)
        with self.assertRaisesRegex(ValueError, 'scalar size'):
            win.token_boolean(None, 20)
        win, _ = self.query(20, b'\x00' * 4, 4)
        self.assertFalse(win.token_boolean(None, 20))

    def test_unexpected_lengths_fail_closed(self):
        for length in (0, 2, 3, 5):
            with self.subTest(length=length):
                win, _ = self.query(21, b'\x01', length)
                with self.assertRaisesRegex(ValueError, 'scalar size'):
                    win.token_boolean(None, 21)

    def test_failed_sdk_query_cannot_supply_a_value(self):
        win, _ = self.query(21, b'\x01', 1, success=False)
        with self.assertRaises(OSError):
            win.token_boolean(None, 21)

    def test_unknown_scalar_class_is_not_queried(self):
        win, calls = self.query(99, b'\x01', 1)
        with self.assertRaisesRegex(ValueError, 'scalar class'):
            win.token_boolean(None, 99)
        self.assertEqual(calls, [])


if __name__ == '__main__':
    unittest.main()
