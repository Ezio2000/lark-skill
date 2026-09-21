"""Optional pandas integration: run with uv's dataframe extra."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "references/sheets/scripts"))
try:
    import pandas as pd
    from lark_sheets_df import df_to_sheet, sheet_to_df
except ModuleNotFoundError as exc:
    if exc.name != "pandas":
        raise
    pd = None


@unittest.skipIf(pd is None, "Enable the dataframe extra to test pandas integration")
class DataframeIntegrationTests(unittest.TestCase):
    def test_roundtrip_preserves_text_identifiers_and_numeric_values(self):
        source = pd.DataFrame({"code": ["001", "002"], "amount": [1.5, 2.5], "active": [True, False]})
        restored = sheet_to_df(df_to_sheet(source, "data"))
        pd.testing.assert_frame_equal(source, restored)

    def test_numeric_column_labels_become_protocol_strings(self):
        packed = df_to_sheet(pd.DataFrame({0: [12], 1: [34]}), "data")
        self.assertEqual(packed["columns"], ["0", "1"])
        self.assertEqual(set(packed["dtypes"]), {"0", "1"})

    def test_label_normalization_does_not_silently_merge_columns(self):
        with self.assertRaises(ValueError):
            df_to_sheet(pd.DataFrame([[1, 2]], columns=[1, "1"]), "data")


if __name__ == "__main__":
    unittest.main()
