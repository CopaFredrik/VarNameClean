# normalize_vars.py Documentation

This project provides a command-line utility to **normalize variable names** in a specific column of a CSV (or delimited) file, along with a **test suite** to verify its behavior. The main script is implemented in `normalize_vars.py` (represented here by `VarTransV3.py`), and the tests are in `Test_VarTrans.py` [1][2].

---

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Command-line Arguments](#command-line-arguments)
  - [Examples](#examples)
- [Normalization Rules](#normalization-rules)
- [API Reference](#api-reference)
  - [`normalize_variable_name`](#normalize_variable_name)
  - [`process_file`](#process_file)
  - [`main`](#main)
- [Test Suite](#test-suite)
  - [Running the Tests](#running-the-tests)
  - [Test Behavior](#test-behavior)
- [Notes and Limitations](#notes-and-limitations)
- [License](#license)

---

## Overview

The **normalize_vars** tool reads a delimited text file (typically CSV), **normalizes variable names** in a specified column, and writes the updated data to an output file.

Normalization is designed for environments where variable names must follow a restricted character set and length limit (e.g., PLC tags, code generators).

Core behavior is implemented in:

- `normalize_variable_name(name: str) -> str`  
- `process_file(input_path, output_path, col_index_0based, delimiter=",", has_header=True)`  
- A CLI entry point `main()` that parses command-line arguments [2].

---

## Installation

1. Ensure you have **Python 3** installed.
2. Place the script (e.g., `normalize_vars.py`, based on `VarTransV3.py`) and the test file `Test_VarTrans.py` in the same directory [1][2].

No external dependencies are required beyond the Python standard library (`sys`, `re`, `csv`, `os`, `tempfile`, `subprocess`, `unittest`, `textwrap`) [1][2].

---

## Usage

### Command-line Arguments

The script is intended to be run from the command line as follows [2]:

```bash
python normalize_vars.py <input_file> <output_file> <column_index> [delimiter] [has_header]
```

- `<input_file>`  
  Path to the input CSV (or delimited) file.

- `<output_file>`  
  Path where the processed file will be written.

- `<column_index>`  
  **1-based** index of the column whose values should be normalized  
  (e.g., `1` = first column, `2` = second column, etc.) [2].

- `[delimiter]` (optional)  
  Field delimiter. Default is `","` (comma) [2].

- `[has_header]` (optional)  
  Either `"yes"` or `"no"`. Default: `"yes"`.  
  When `"yes"`, the first row is treated as a header and is **not** normalized [2].

If the number of arguments is incorrect (less than 4 or more than 6), the script prints a usage message and exits with code `1` [2]:

```text
Usage: python normalize_vars.py <input_file> <output_file> <column_index> [delimiter] [has_header]
  <column_index> is 1-based (1 = first column).
  [delimiter]   is optional, default is ','.
  [has_header]  is optional, 'yes' or 'no' (default: 'yes').
```

### Examples

#### 1. Normalize the second column of a comma-separated file with a header

```bash
python normalize_vars.py input.csv output.csv 2
```

- Uses default delimiter: `,`
- Assumes there **is** a header row (`has_header = "yes"`)

Given data like [1]:

```csv
Name,Variable,Description
Row1,1stVar,Something
Row2,Motor#1.Status,Something else
Row3,OK_name,Already valid
```

The **Variable** column will be normalized to:

- `1stVar` → `_1stVar` (leading digit gets prefixed with `_`)  
- `Motor#1.Status` → `Motor_1_Status` (`#` and `.` replaced with `_`)  
- `OK_name` → `OK_name` (no change) [1][2]

#### 2. Normalize the third column of a semicolon-separated file without a header

```bash
python normalize_vars.py data.txt data_out.txt 3 ";" no
```

- Delimiter: `";"`
- No header row; all rows are processed.

---

## Normalization Rules

The function `normalize_variable_name` enforces the following rules [2]:

1. **Allowed characters**  
   The final name may only contain:
   - `A–Z`
   - `a–z`
   - `0–9`
   - `_` (underscore)

2. **Leading digit**  
   If the original name starts with a digit (`0–9`), an underscore is **prepended**:

   ```text
   "1stVar" → "_1stVar"
   ```

3. **Unsupported characters**  
   Any character **not** in `[A-Za-z0-9_]` is replaced with an underscore:

   ```text
   "Motor#1.Status" → "Motor_1_Status"
   ```

4. **Maximum length**  
   Names are **truncated to 64 characters**:

   ```text
   "a_very_long_name_... (over 64 chars) ..." → "first 64 characters only"
   ```

5. **Empty input**  
   If the input name is empty or falsy, it becomes a single underscore:

   ```text
   "" → "_"
   ```

---

## API Reference

### `normalize_variable_name`

```python
def normalize_variable_name(name: str) -> str:
    """
    Normalize a variable name so it uses only:
    - letters A–Z, a–z
    - digits 0–9
    - underscore _

    Rules:
    1. If the name starts with a digit, prepend an underscore.
    2. Replace all characters outside [A-Za-z0-9_] with an underscore.
    3. Truncate to 64 characters total.
    """
```

**Parameters**

- `name`: The original variable name string.

**Returns**

- A normalized string satisfying the character and length restrictions [2].

---

### `process_file`

```python
def process_file(
    input_path: str,
    output_path: str,
    col_index_0based: int,
    delimiter: str = ",",
    has_header: bool = True,
):
    """
    Read input_path, normalize column col_index_0based (0-based),
    write to output_path.
    """
```

**Parameters**

- `input_path`: Path to the input file.
- `output_path`: Path to the output file.
- `col_index_0based`: **0-based** index of the column to normalize (note: the CLI uses 1-based and converts to 0-based internally) [2].
- `delimiter`: Field delimiter; default `","`.
- `has_header`: If `True`, the first row is treated as a header and is written unchanged [2].

**Behavior**

- Reads each row from `input_path` using `csv` with the given `delimiter`.
- If `has_header` is `True`, the first row is copied verbatim.
- For all subsequent rows (or all rows if `has_header` is `False`):
  - Applies `normalize_variable_name` to the value of the specified column.
  - Writes the updated rows to `output_path` [2].

---

### `main`

```python
def main():
    # Usage:
    #   python normalize_vars.py <input_file> <output_file> <column_index> [delimiter] [has_header]
    #
    #   <column_index> : 1-based (1 = first column)
    #   [delimiter]    : optional, default ","
    #   [has_header]   : optional, "yes" (default) or "no"
```

**Responsibilities** [2]:

1. Parse `sys.argv` for CLI arguments.
2. Validate argument count.
3. Infer `delimiter` (default `","`) and `has_header` (`"yes"` → `True`, `"no"` → `False`).
4. Convert the 1-based `<column_index>` to 0-based for use by `process_file`.
5. Invoke `process_file(input_file, output_file, col_index_0based, delimiter, has_header)`.

The script is executable as a module:

```python
if __name__ == "__main__":
    main()
```

---

## Test Suite

The test file `TestNormalizeVarsScript` (within `Test_VarTrans.py`) provides automated tests for the CLI behavior of the script [1].

### Running the Tests

From the directory containing both the test file and script:

```bash
python Test_VarTrans.py
```

By default this tests `normalize_vars.py` [1]. You can override the script name:

```bash
python Test_VarTrans.py myscript.py
```

The test file supports an **optional script name as the first positional argument** [1]:

- `python Test_VarTrans.py` → tests `normalize_vars.py`
- `python Test_VarTrans.py myscript.py` → tests `myscript.py`

It also ensures the script exists before running tests; otherwise it prints an error and exits [1].

Internally, tests call a helper method to run the script as a subprocess [1]:

```python
cmd = [sys.executable, SCRIPT_NAME] + args
result = subprocess.run(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
)
```

If the script exits with a non-zero return code, the test fails and prints stdout/stderr [1].

### Test Behavior

An example test case `test_with_header_comma_delimited` validates:

- CSV input with a header row.
- Comma as delimiter.
- Normalization applied to the **second column** (1-based) [1].

It checks:

- Header row is **unchanged**.
- `1stVar` becomes `_1stVar`.
- `Motor#1.Status` becomes `Motor_1_Status`.
- Already valid names remain unchanged [1][2].

Temporary directories and files are used so tests do not affect real files [1].

---

## Notes and Limitations

- Column index from the CLI is **1-based**; the internal API uses **0-based** indices [2].
- Only the specified column is normalized; other columns are left intact.
- The script assumes a well-formed delimited file; there is no extensive error handling for malformed CSV beyond what Python’s `csv` module provides.

---
