#!/usr/bin/env python3
"""
Generate Pydantic models from nested schema directories.

This script:
1. Scans the schemas/ directory for .yaml and .json schema files
2. Generates Pydantic models maintaining the directory structure
3. Creates proper __init__.py files for Python packages
4. Handles cross-references between schemas
5. Adds a nested Fields class to each model for field name constants

Usage:
    python generate_events.py
    python generate_events.py --schemas-dir custom_schemas/ --output-dir python/models/
"""

import argparse
import ast
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Set, Tuple


class SchemasGenerator:
    def __init__(self, schemas_dir: str, output_dir: str, verbose: bool = False):
        self.schemas_dir = Path(schemas_dir)
        self.output_dir = Path(output_dir)
        self.verbose = verbose

        if not self.schemas_dir.exists():
            raise ValueError(f"Schemas directory does not exist: {self.schemas_dir}")

    def log(self, message: str):
        """Print message if verbose mode is enabled"""
        if self.verbose:
            print(f"[INFO] {message}")

    def find_schema_files(self) -> List[Path]:
        """
        Find all schema files (.yaml, .yml, .json) in the schemas directory.
        Returns list of paths relative to schemas_dir.
        """
        schema_files = []
        extensions = {'.yaml', '.yml', '.json'}

        for ext in extensions:
            schema_files.extend(self.schemas_dir.rglob(f'*{ext}'))

        # Sort for deterministic order
        schema_files.sort()

        self.log(f"Found {len(schema_files)} schema files")
        return schema_files

    def get_relative_path(self, schema_file: Path) -> Path:
        """Get path relative to schemas directory"""
        return schema_file.relative_to(self.schemas_dir)

    def get_output_path(self, schema_file: Path) -> Path:
        """
        Get the output Python file path for a schema file.

        Example:
            schemas/events/trading/trade.yaml -> python/events/trading/trade.py
            schemas/common/base.json -> python/common/base.py
        """
        rel_path = self.get_relative_path(schema_file)

        # Replace extension with .py
        output_path = self.output_dir / rel_path.with_suffix('.py')

        return output_path

    def get_package_dirs(self, schema_files: List[Path]) -> Set[Path]:
        """
        Get all unique package directories that need __init__.py files.
        """
        package_dirs = {self.output_dir}  # Root package

        for schema_file in schema_files:
            output_path = self.get_output_path(schema_file)

            # Add all parent directories
            current = output_path.parent
            while current != self.output_dir and current != current.parent:
                package_dirs.add(current)
                current = current.parent

        return package_dirs

    def extract_class_fields(self, class_node: ast.ClassDef) -> List[str]:
        """Extract field names from a class definition"""
        fields = []
        for item in class_node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                field_name = item.target.id
                # Skip private fields and model_config
                if not field_name.startswith('_') and field_name != 'model_config':
                    fields.append(field_name)
        return fields

    def generate_fields_class(self, fields: List[str], indent: str = "    ") -> str:
        """Generate the Fields nested class code"""
        if not fields:
            return ""

        lines = [f"{indent}class Fields:"]
        for field in fields:
            lines.append(f"{indent}    {field.upper()} = '{field}'")
        lines.append("")  # Empty line after class

        return "\n".join(lines)

    def find_class_insert_position(self, lines: List[str], class_start_line: int) -> int:
        """
        Find where to insert the Fields class within a class definition.
        Insert after model_config if present, otherwise after class docstring or class declaration.
        """
        # Start searching from the line after class declaration
        i = class_start_line
        in_docstring = False
        docstring_quotes = None
        docstring_ended = False

        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            # Handle docstrings
            if not docstring_ended:
                # Check if we're entering a docstring
                if not in_docstring and (stripped.startswith('"""') or stripped.startswith("'''")):
                    in_docstring = True
                    docstring_quotes = '"""' if stripped.startswith('"""') else "'''"

                    # Check if docstring ends on same line (e.g., """Single line""")
                    if stripped.count(docstring_quotes) >= 2 and len(stripped) > len(docstring_quotes):
                        in_docstring = False
                        docstring_ended = True

                    i += 1
                    continue

                # Check if we're exiting a multi-line docstring
                elif in_docstring:
                    if docstring_quotes in line:
                        in_docstring = False
                        docstring_ended = True
                    i += 1
                    continue

            # After docstring has ended, skip empty lines and comments
            if docstring_ended and (not stripped or stripped.startswith('#')):
                i += 1
                continue

            # Check for model_config (after docstring)
            if docstring_ended and 'model_config' in stripped and '=' in stripped:
                # Skip until we find the end of model_config assignment
                if 'ConfigDict' in stripped:
                    # Multi-line ConfigDict
                    paren_count = stripped.count('(') - stripped.count(')')
                    i += 1
                    while i < len(lines) and paren_count > 0:
                        paren_count += lines[i].count('(') - lines[i].count(')')
                        i += 1
                    return i
                else:
                    # Single line model_config
                    return i + 1

            # If we've passed the docstring and found any actual content (field or method), insert before it
            if docstring_ended and stripped and not stripped.startswith('#'):
                return i

            # If no docstring was found and we hit content, insert here
            if not in_docstring and not docstring_ended and stripped and not stripped.startswith('#'):
                return i

            i += 1

        return i

    def add_fields_class_to_model(self, output_file: Path):
        """Add a Fields nested class to each BaseModel class in the generated file"""

        if not output_file.exists():
            return

        content = output_file.read_text()

        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            self.log(f"Could not parse {output_file}: {e}")
            return

        lines = content.split('\n')
        insertions = []  # List of (line_number, fields_class_code)

        # Find all class definitions
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if this is likely a Pydantic model (has annotations)
                fields = self.extract_class_fields(node)

                if fields:
                    # Get the indentation of the class
                    class_line_idx = node.lineno - 1  # ast uses 1-based indexing
                    class_line = lines[class_line_idx]
                    indent = len(class_line) - len(class_line.lstrip())
                    base_indent = ' ' * indent

                    # Generate Fields class
                    fields_class = self.generate_fields_class(fields, base_indent + "    ")

                    # Find insertion point
                    insert_line = self.find_class_insert_position(lines, class_line_idx + 1)

                    insertions.append((insert_line, fields_class))

        # Insert Fields classes (work backwards to maintain line numbers)
        for line_num, fields_class in reversed(insertions):
            lines.insert(line_num, fields_class)

        # Write back to file
        output_file.write_text('\n'.join(lines))
        self.log(f"Added Fields classes to: {output_file.relative_to(self.output_dir.parent)}")

    def generate_model(self, schema_file: Path, output_file: Path) -> bool:
        """
        Generate a single Pydantic model from a schema file.
        Returns True if successful, False otherwise.
        """
        # Create output directory
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Determine input file type
        file_ext = schema_file.suffix.lower()
        if file_ext in ['.yaml', '.yml']:
            input_type = 'jsonschema'  # datamodel-codegen handles YAML automatically
        elif file_ext == '.json':
            input_type = 'jsonschema'
        else:
            self.log(f"Skipping unsupported file type: {schema_file}")
            return False

        # Build command
        cmd = [
            'datamodel-codegen',
            '--input', str(schema_file),
            '--output', str(output_file),
            '--input-file-type', input_type,
            '--output-model-type', 'pydantic_v2.BaseModel',
            '--field-constraints',
            '--use-standard-collections',
            '--use-schema-description',
            '--use-field-description',
            '--target-python-version', '3.9',
            '--collapse-root-models',
            '--use-default',
            '--use-default-kwarg',
        ]

        self.log(f"Generating: {self.get_relative_path(schema_file)} -> {output_file.relative_to(self.output_dir)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            if self.verbose and result.stdout:
                print(result.stdout)

            # Add Fields class to the generated model
            self.add_fields_class_to_model(output_file)

            return True

        except subprocess.CalledProcessError as e:
            print(f"âŒ Error generating {schema_file}:", file=sys.stderr)
            print(e.stderr, file=sys.stderr)
            return False
        except FileNotFoundError:
            print("âŒ Error: datamodel-codegen not found. Install it with:", file=sys.stderr)
            print("    pip install datamodel-code-generator[http]", file=sys.stderr)
            sys.exit(1)

    def create_init_file(self, package_dir: Path, schema_files: List[Path]):
        """
        Create __init__.py file for a package directory.
        Imports all models from Python files in that directory.
        """
        init_file = package_dir / '__init__.py'

        # Find all Python files in this directory (not subdirectories)
        py_files = [
            f for f in package_dir.glob('*.py')
            if f.name != '__init__.py'
        ]

        if not py_files and package_dir != self.output_dir:
            # No models in this directory, just make it a package
            init_file.write_text('"""Generated event models package"""\n')
            return

        # Generate imports
        imports = []
        for py_file in sorted(py_files):
            module_name = py_file.stem
            imports.append(f"from .{module_name} import *")

        # Write __init__.py
        content = '"""Generated event models package"""\n\n'
        content += '\n'.join(imports)
        content += '\n'

        init_file.write_text(content)
        self.log(f"Created: {init_file.relative_to(self.output_dir.parent)}")

    def generate_all(self) -> bool:
        """
        Main generation logic.
        Returns True if all generations succeeded, False otherwise.
        """
        print(f"ðŸ” Scanning schemas in: {self.schemas_dir}")

        # Find all schema files
        schema_files = self.find_schema_files()

        if not schema_files:
            print(f"âš ï¸  No schema files found in {self.schemas_dir}")
            return True

        print(f"ðŸ“ Generating models in: {self.output_dir}")
        print()

        # Generate each model
        success_count = 0
        fail_count = 0

        for schema_file in schema_files:
            output_file = self.get_output_path(schema_file)

            if self.generate_model(schema_file, output_file):
                success_count += 1
            else:
                fail_count += 1

        print()
        print(f"âœ… Generated {success_count} models with Fields classes")

        if fail_count > 0:
            print(f"âŒ Failed to generate {fail_count} models")

        # Create __init__.py files
        print()
        print("ðŸ“¦ Creating package structure...")

        package_dirs = self.get_package_dirs(schema_files)
        for package_dir in sorted(package_dirs):
            self.create_init_file(package_dir, schema_files)

        print()
        print("âœ¨ Done!")

        return fail_count == 0

    def print_structure(self):
        """Print the directory structure that will be generated"""
        schema_files = self.find_schema_files()

        print("Schema -> Python mapping:")
        print()

        for schema_file in schema_files:
            rel_schema = self.get_relative_path(schema_file)
            output_file = self.get_output_path(schema_file)
            rel_output = output_file.relative_to(self.output_dir.parent)

            print(f"  {rel_schema}")
            print(f"    -> {rel_output}")

        print()
        print(f"Total: {len(schema_files)} schemas")


def main():
    parser = argparse.ArgumentParser(
        description='Generate Pydantic models from nested schema directories',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python generate_events.py

  # Custom directories
  python generate_events.py --schemas-dir my_schemas/ --output-dir generated/

  # Preview structure without generating
  python generate_events.py --dry-run

  # Verbose output
  python generate_events.py -v
        """
    )

    parser.add_argument(
        '--schemas-dir',
        default='schemas',
        help='Directory containing schema files (default: schemas)'
    )

    parser.add_argument(
        '--output-dir',
        default='python/events',
        help='Output directory for generated Python models (default: python/events)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be generated without actually generating'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    try:
        generator = SchemasGenerator(
            schemas_dir=args.schemas_dir,
            output_dir=args.output_dir,
            verbose=args.verbose
        )

        if args.dry_run:
            generator.print_structure()
            return 0

        success = generator.generate_all()
        return 0 if success else 1

    except Exception as e:
        print(f"âŒ Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
