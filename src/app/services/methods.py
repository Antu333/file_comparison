from src.app.services.check_diff import DiffChecker
from src.app.services.check_similarity import SimilarityChecker
from src.app.services.summerizer import Summarizer


class CompareService:

    # ── DOCX / PDF text comparison ────────────────────────────────────────────

    @staticmethod
    def text_report(content1: str, content2: str) -> dict:
        """
        Compare two text blobs (from DOCX or PDF).
        Returns similarity score + line-level diff.
        """
        diff_str = DiffChecker.get_diff(content1, content2)
        new_lines, deleted_lines = DiffChecker.show_diff(diff_str)
        score = SimilarityChecker.check_similarity(content1, content2)
        return {
            "similarity_score": score,
            "new_lines": new_lines,
            "deleted_lines": deleted_lines,
        }

    # ── CSV comparison ────────────────────────────────────────────────────────

    @staticmethod
    def csv_symmetric_report(df1, df2) -> list[dict]:
        return DiffChecker.compare_csv_symmetric(df1, df2)

    @staticmethod
    def csv_asymmetric_report(bytes1: bytes, bytes2: bytes, key_column: str) -> dict:
        return DiffChecker.compare_csv_asymmetric(bytes1, bytes2, key_column)

    # ── Excel comparison ──────────────────────────────────────────────────────

    @staticmethod
    def excel_report(bytes1: bytes, bytes2: bytes, output_path: str, merge_on_column: str) -> str:
        """Returns the path to the generated diff Excel file."""
        return DiffChecker.compare_excel(bytes1, bytes2, output_path, merge_on_column)

    # ── AI Summaries ──────────────────────────────────────────────────────────

    @staticmethod
    def summary_for_text(content1: str, content2: str) -> str:
        """Generate a Gemini summary comparing two DOCX/PDF text blobs."""
        score = SimilarityChecker.check_similarity(content1, content2)
        diff_str = DiffChecker.get_diff(content1, content2)
        new_lines, deleted_lines = DiffChecker.show_diff(diff_str)

        context = (
            f"Similarity percentage: {score:.2%}\n\n"
            f"Newly added lines (+):\n" + "\n".join(new_lines) + "\n\n"
            f"Deleted lines (-):\n" + "\n".join(deleted_lines)
        )

        prompt = f"""You are a summarizer. Generate a crisp and concise summary from the following context:

{context}

Important notes:
1. The summary must be professional and understandable to any user.
2. Keep the summary within 1000 words.
3. Include all points from the context properly.
4. Maintain a proper structure.

Return the response in clean Markdown.

Rules:
- Use ## headings.
- Use bullet points.
- Use numbered lists where appropriate.
- Use tables for comparisons.
- Bold important values.
- Do not return HTML.
- Keep sections concise.
"""
        return Summarizer.gemini(prompt)

    @staticmethod
    def summary_for_csv_excel(content1: str, content2: str) -> str:
        """Generate a Gemini comparison table for two CSV/Excel content strings."""
        prompt = f"""You are a professional AI assistant. Compare the following CSV/Excel file contents and generate a professional comparison report as a CSV table.

Table format:
1. Columns: sl_no | column_name | old_value | new_value
2. Only include rows where values differ.
3. Output ONLY the CSV table — no markdown, no backticks, no explanations.
4. Keep the report under 500 words.
5. If no differences exist, output only the header row.

Return the response in clean Markdown.

Rules:
- Use ## headings.
- Use bullet points.
- Use numbered lists where appropriate.
- Use tables for comparisons.
- Bold important values.
- Do not return HTML.
- Keep sections concise.

File 1 contents:
{content1}

File 2 contents:
{content2}
"""
        return Summarizer.gemini(prompt)

    @staticmethod
    def csv_string_to_records(content1: str, content2: str) -> tuple[str, list[dict]]:
        """
        Ask Gemini to diff two CSV/Excel contents and return
        (raw_csv_text, parsed_records).
        """
        from app.services.read_file import FileReader

        prompt = f"""You will compare the contents of two CSV/Excel files.
You must NOT invent or assume any data. Only use actual values from the files.

STRICT OUTPUT RULES:
1. Output ONLY a CSV table. No explanations, no markdown, no comments.
2. Columns: sl_no, column_name, old_value, new_value
3. Only include rows where values differ.
4. Values must be taken EXACTLY from the input — no modification, no guessing.
5. Do NOT describe missing data. Leave a cell empty if needed.
6. Keep output under 500 words.
7. Do NOT wrap the CSV in backticks or markdown.
8. If no differences exist, output only the header row.

Return the response in clean Markdown.

Rules:
- Use ## headings.
- Use bullet points.
- Use numbered lists where appropriate.
- Use tables for comparisons.
- Bold important values.
- Do not return HTML.
- Keep sections concise.

File 1 contents:
{content1}

File 2 contents:
{content2}
"""
        raw_csv = Summarizer.gemini(prompt)
        records = FileReader.read_csv_string(raw_csv)
        return raw_csv, records