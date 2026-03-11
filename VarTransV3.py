#!/usr/bin/env python3
import sys
import re
import csv


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

    if not name:
        return "_"

    # If first character is a digit, add underscore in front
    if name[0].isdigit():
        name = "_" + name

    # Replace all non [A-Za-z0-9_] characters with underscore
    name = re.sub(r'[^A-Za-z0-9_]', '_', name)

    # Enforce max length 64
    name = name[:64]

    return name


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

    - Treats the file as delimited (CSV-like) text.
    - If has_header is True:
        * First row is written unchanged as header.
        * Only the selected column in subsequent rows is modified.
    - If has_header is False:
        * All rows are treated as data and may be modified.
    """
    with open(input_path, "r", newline="", encoding="utf-8") as infile, \
         open(output_path, "w", newline="", encoding="utf-8") as outfile:

        reader = csv.reader(infile, delimiter=delimiter)
        writer = csv.writer(outfile, delimiter=delimiter)

        if has_header:
            try:
                header = next(reader)
            except StopIteration:
                # Empty file
                return
            writer.writerow(header)

        for row in reader:
            if col_index_0based < len(row):
                row[col_index_0based] = normalize_variable_name(row[col_index_0based])
            writer.writerow(row)


def main():
    # Usage:
    #   python normalize_vars.py <input_file> <output_file> <column_index> [delimiter] [has_header]
    #
    #   <column_index> : 1-based (1 = first column)
    #   [delimiter]    : optional, default ","
    #   [has_header]   : optional, "yes" (default) or "no"
    if len(sys.argv) < 4 or len(sys.argv) > 6:
        print("Usage: python normalize_vars.py <input_file> <output_file> <column_index> [delimiter] [has_header]")
        print("  <column_index> is 1-based (1 = first column).")
        print("  [delimiter]   is optional, default is ','.")
        print("  [has_header]  is optional, 'yes' or 'no' (default: 'yes').")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Column index (1-based from CLI)
    try:
        column_index_1based = int(sys.argv[3])
        if column_index_1based <= 0:
            raise ValueError
    except ValueError:
        print("Error: <column_index> must be a positive integer (1-based).")
        sys.exit(1)

    col_index_0based = column_index_1based - 1

    # Optional delimiter
    delimiter = sys.argv[4] if len(sys.argv) >= 5 else ","

    # Optional has_header
    if len(sys.argv) == 6:
        has_header_arg = sys.argv[5].strip().lower()
        if has_header_arg in ("yes", "y", "true", "1"):
            has_header = True
        elif has_header_arg in ("no", "n", "false", "0"):
            has_header = False
        else:
            print("Error: [has_header] must be 'yes' or 'no'.")
            sys.exit(1)
    else:
        has_header = True  # default

    process_file(input_file, output_file, col_index_0based, delimiter=delimiter, has_header=has_header)


if __name__ == "__main__":
    main()