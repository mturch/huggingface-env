#!/usr/bin/env python3
"""
Generate PDF diagrams from Mermaid (.mmd) files using mermaid-cli.

This script:
1. Finds all .mmd files in the specified directory
2. Generates PDF versions using mermaid-cli (mmdc)
3. Optionally generates PNG versions for web use

Requirements:
- Node.js and npm installed
- @mermaid-js/mermaid-cli installed globally: npm install -g @mermaid-js/mermaid-cli
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


def check_mermaid_cli() -> bool:
    """Check if mermaid-cli is installed."""
    try:
        result = subprocess.run(
            ["mmdc", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def find_mermaid_files(directory: Path) -> List[Path]:
    """Find all .mmd files in the directory."""
    return list(directory.rglob("*.mmd"))


def generate_diagram(
    input_file: Path,
    output_dir: Path,
    format: str = "pdf",
    background: str = "transparent",
) -> bool:
    """
    Generate a diagram from a Mermaid file.

    Args:
        input_file: Path to the .mmd file
        output_dir: Directory to save the output
        format: Output format (pdf, png, svg)
        background: Background color (transparent, white, etc.)

    Returns:
        True if successful, False otherwise
    """
    output_file = output_dir / f"{input_file.stem}.{format}"
    output_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        "mmdc",
        "-i", str(input_file),
        "-o", str(output_file),
        "-b", background,
    ]

    print(f"Generating {format.upper()} from {input_file.name}...", end=" ")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"✓ Saved to {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed")
        print(f"Error: {e.stderr}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate diagrams from Mermaid files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-i", "--input-dir",
        type=Path,
        default=Path("docs/mermaid"),
        help="Directory containing .mmd files (default: docs/mermaid)",
    )
    parser.add_argument(
        "-o", "--output-dir",
        type=Path,
        default=Path("docs/diagrams"),
        help="Directory to save generated diagrams (default: docs/diagrams)",
    )
    parser.add_argument(
        "-f", "--formats",
        nargs="+",
        default=["pdf"],
        choices=["pdf", "png", "svg"],
        help="Output formats (default: pdf)",
    )
    parser.add_argument(
        "-b", "--background",
        default="transparent",
        help="Background color (default: transparent)",
    )
    parser.add_argument(
        "--file",
        type=Path,
        help="Process a single file instead of directory",
    )

    args = parser.parse_args()

    # Check if mermaid-cli is installed
    if not check_mermaid_cli():
        print("Error: mermaid-cli (mmdc) not found!")
        print("Install it with: npm install -g @mermaid-js/mermaid-cli")
        sys.exit(1)

    # Find files to process
    if args.file:
        if not args.file.exists():
            print(f"Error: File not found: {args.file}")
            sys.exit(1)
        mermaid_files = [args.file]
    else:
        if not args.input_dir.exists():
            print(f"Error: Directory not found: {args.input_dir}")
            print(f"Creating directory: {args.input_dir}")
            args.input_dir.mkdir(parents=True, exist_ok=True)

        mermaid_files = find_mermaid_files(args.input_dir)

    if not mermaid_files:
        print(f"No .mmd files found in {args.input_dir}")
        sys.exit(0)

    print(f"Found {len(mermaid_files)} Mermaid file(s)")
    print()

    # Generate diagrams
    success_count = 0
    total_count = len(mermaid_files) * len(args.formats)

    for mermaid_file in mermaid_files:
        for fmt in args.formats:
            if generate_diagram(mermaid_file, args.output_dir, fmt, args.background):
                success_count += 1

    print()
    print(f"Generated {success_count}/{total_count} diagram(s)")

    if success_count < total_count:
        sys.exit(1)


if __name__ == "__main__":
    main()
