import difflib
import io
import re
import tempfile

import pandas as pd
from csv_diff import load_csv, compare as csv_diff_compare


class DiffChecker:

    # ── Text diff (DOCX / PDF) ────────────────────────────────────────────────

    @staticmethod
    def get_diff(content1: str, content2: str) -> str:
        """Return unified differ output for two text blobs."""
        lines1 = content1.strip().splitlines()
        lines2 = content2.strip().splitlines()
        d = difflib.Differ()
        result = d.compare(lines1, lines2)
        return "\n".join(result)

    @staticmethod
    def show_diff(diff_str: str) -> tuple[list[str], list[str]]:
        """Split a differ string into (new_lines, deleted_lines)."""
        deleted = re.findall(r"^\-.*", diff_str, re.MULTILINE)
        new = re.findall(r"^\+.*", diff_str, re.MULTILINE)
        return new, deleted

    # ── CSV diff ──────────────────────────────────────────────────────────────

    @staticmethod
    def compare_csv_symmetric(df1: pd.DataFrame, df2: pd.DataFrame) -> list[dict]:
        """Compare two identically-structured DataFrames; return changed rows as records."""
        compared = df1.compare(df2, result_names=("old", "new"))
        return compared.reset_index().to_dict(orient="records")

    @staticmethod
    def compare_csv_asymmetric(
        bytes1: bytes,
        bytes2: bytes,
        key_column: str,
    ) -> dict:
        """Compare two CSV files that may differ in shape, keyed on key_column."""
        data1 = load_csv(io.StringIO(bytes1.decode()), key=key_column)
        data2 = load_csv(io.StringIO(bytes2.decode()), key=key_column)
        result = csv_diff_compare(data1, data2)
        return {
            "added": result.get("added", []),
            "removed": result.get("removed", []),
            "changed": result.get("changed", []),
            "columns_added": result.get("columns_added", []),
            "columns_removed": result.get("columns_removed", []),
            "columns_renamed": result.get("columns_renamed", []),
        }

    # ── Excel diff ────────────────────────────────────────────────────────────

    @staticmethod
    def compare_excel(
        bytes1: bytes,
        bytes2: bytes,
        output_path: str,
        merge_on_column: str,
    ) -> str:
        """
        Compare two Excel files and write a diff workbook to output_path.
        Returns output_path so the caller can serve it as a FileResponse.
        """
        df1 = pd.read_excel(io.BytesIO(bytes1)).fillna("MISSING")
        df2 = pd.read_excel(io.BytesIO(bytes2)).fillna("MISSING")

        merged = pd.merge(
            df1, df2,
            on=merge_on_column,
            how="outer",
            suffixes=("_old", "_new"),
        )

        diff_mask = pd.Series([False] * len(merged), index=merged.index)
        for col in df1.columns:
            if col != merge_on_column and f"{col}_new" in merged.columns:
                diff_mask |= merged[f"{col}_old"] != merged[f"{col}_new"]

        changed = merged[diff_mask].copy()

        new_cols = []
        for col in changed.columns:
            if col == merge_on_column:
                new_cols.append((merge_on_column, ""))
            elif col.endswith("_old"):
                new_cols.append((col[:-4], "Old Value"))
            elif col.endswith("_new"):
                new_cols.append((col[:-4], "New Value"))
            else:
                new_cols.append((col, ""))

        changed.columns = pd.MultiIndex.from_tuples(new_cols)
        changed.to_excel(output_path, index=True, engine="openpyxl")

        return output_path