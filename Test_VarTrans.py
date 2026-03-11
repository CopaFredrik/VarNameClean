import os
import sys
import csv
import tempfile
import subprocess
import textwrap
import unittest


# Default script name; can be overridden via command-line argument
SCRIPT_NAME = "normalize_vars.py"


class TestNormalizeVarsScript(unittest.TestCase):
    def run_script(self, args):
        """
        Helper to run the script with the given list of arguments.
        Raises an assertion error if the script exits with non-zero code.
        """
        cmd = [sys.executable, SCRIPT_NAME] + args
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result.returncode != 0:
            self.fail(
                f"Script {SCRIPT_NAME} failed with code {result.returncode}\n"
                f"STDOUT:\n{result.stdout}\n"
                f"STDERR:\n{result.stderr}"
            )
        return result

    def test_with_header_comma_delimited(self):
        """
        Header row present, comma-delimited, normalize 2nd column (1-based).
        """
        input_data = textwrap.dedent(
            """\
            Name,Variable,Description
            Row1,1stVar,Something
            Row2,Motor#1.Status,Something else
            Row3,OK_name,Already valid
            """
        )

        expected_rows = [
            ["Name", "Variable", "Description"],            # header unchanged
            ["Row1", "_1stVar", "Something"],               # leading digit -> _1stVar
            ["Row2", "Motor_1_Status", "Something else"],   # # and . -> _
            ["Row3", "OK_name", "Already valid"],           # unchanged
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            in_path = os.path.join(tmpdir, "input.csv")
            out_path = os.path.join(tmpdir, "output.csv")

            with open(in_path, "w", encoding="utf-8", newline="") as f:
                f.write(input_data)

            # column_index = 2 (1-based), delimiter default ",", header = yes (default)
            self.run_script([in_path, out_path, "2"])

            with open(out_path, "r", encoding="utf-8", newline="") as f:
                reader = csv.reader(f, delimiter=",")
                rows = list(reader)

            self.assertEqual(rows, expected_rows)

    def test_without_header_semicolon_delimited(self):
        """
        No header row, semicolon-delimited, normalize 1st column (1-based).
        """
        input_data = textwrap.dedent(
            """\
            1stName;Value
            Motor#1.Status;123
            OK_name;456
            """
        )

        expected_rows = [
            ["_1stName", "Value"],          # 1stName -> _1stName
            ["Motor_1_Status", "123"],      # # and . -> _
            ["OK_name", "456"],             # unchanged
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            in_path = os.path.join(tmpdir, "input.csv")
            out_path = os.path.join(tmpdir, "output.csv")

            with open(in_path, "w", encoding="utf-8", newline="") as f:
                f.write(input_data)

            # column_index = 1 (1-based), delimiter=";", has_header="no"
            self.run_script([in_path, out_path, "1", ";", "no"])

            with open(out_path, "r", encoding="utf-8", newline="") as f:
                reader = csv.reader(f, delimiter=";")
                rows = list(reader)

            self.assertEqual(rows, expected_rows)

    def test_empty_file(self):
        """
        Empty file should not crash and output should be empty.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            in_path = os.path.join(tmpdir, "input.csv")
            out_path = os.path.join(tmpdir, "output.csv")

            # Create empty file
            open(in_path, "w", encoding="utf-8").close()

            self.run_script([in_path, out_path, "1"])

            with open(out_path, "r", encoding="utf-8", newline="") as f:
                content = f.read()

            self.assertEqual(content, "")

    def test_single_row_no_header(self):
        """
        Single data row, no header, check normalization.
        """
        input_data = "1stVar,Something\n"
        expected_rows = [
            ["_1stVar", "Something"],
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            in_path = os.path.join(tmpdir, "input.csv")
            out_path = os.path.join(tmpdir, "output.csv")

            with open(in_path, "w", encoding="utf-8", newline="") as f:
                f.write(input_data)

            # column_index = 1, delimiter=",", has_header="no"
            self.run_script([in_path, out_path, "1", ",", "no"])

            with open(out_path, "r", encoding="utf-8", newline="") as f:
                reader = csv.reader(f, delimiter=",")
                rows = list(reader)

            self.assertEqual(rows, expected_rows)
    def test_column_index_out_of_range(self):
        """
        Column index larger than number of columns:
        script should not crash; rows should be unchanged.
        """
        input_data = textwrap.dedent(
            """\
            Name,Variable
            Row1,Value1
            Row2,Value2
            """
        )

        expected_rows = [
            ["Name", "Variable"],
            ["Row1", "Value1"],
            ["Row2", "Value2"],
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            in_path = os.path.join(tmpdir, "input.csv")
            out_path = os.path.join(tmpdir, "output.csv")

            with open(in_path, "w", encoding="utf-8", newline="") as f:
                f.write(input_data)

            # column_index = 3 (1-based): out of range (only 2 columns)
            self.run_script([in_path, out_path, "3"])

            with open(out_path, "r", encoding="utf-8", newline="") as f:
                reader = csv.reader(f, delimiter=",")
                rows = list(reader)

            self.assertEqual(rows, expected_rows)

    def test_truncation_to_64_chars(self):
        """
        Check that variable names are truncated to 64 characters.
        """
        long_name = "A" * 100  # 100 characters
        input_data = f"Header,{long_name}\nRow1,{long_name}\n"

        with tempfile.TemporaryDirectory() as tmpdir:
            in_path = os.path.join(tmpdir, "input.csv")
            out_path = os.path.join(tmpdir, "output.csv")

            with open(in_path, "w", encoding="utf-8", newline="") as f:
                f.write(input_data)

            # column_index = 2, has_header = yes
            self.run_script([in_path, out_path, "2"])

            with open(out_path, "r", encoding="utf-8", newline="") as f:
                reader = csv.reader(f, delimiter=",")
                rows = list(reader)

            # Header remains full length (not normalized)
            self.assertEqual(rows[0][1], long_name)
            # Data row truncated
            self.assertEqual(len(rows[1][1]), 64)
            self.assertEqual(rows[1][1], "A" * 64)


if __name__ == "__main__":
    # Ensure we run tests from the directory containing the script
    this_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(this_dir)

    # Allow optional script name as first positional argument to the test file
    # Usage:
    #   python test_normalize_vars.py                -> tests "normalize_vars.py"
    #   python test_normalize_vars.py myscript.py    -> tests "myscript.py"
    global SCRIPT_NAME
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        SCRIPT_NAME = sys.argv[1]
        # Remove it from argv so unittest doesn't treat it as a test pattern
        sys.argv.pop(1)

    # Make sure the script exists before running tests
    if not os.path.exists(SCRIPT_NAME):
        print(f"Error: {SCRIPT_NAME} not found in {this_dir}")
        sys.exit(1)

    unittest.main()