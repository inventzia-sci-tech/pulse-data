# #!/usr/bin/env python3
# """
# Generate Pydantic models from nested schema directories.
#
# This script:
# 1. Scans the schemas/ directory for .yaml and .json schema files
# 2. Generates Pydantic models maintaining the directory structure
# 3. Creates proper __init__.py files for Python packages
# 4. Handles cross-references between schemas
#
# Usage:
#     python generate_events.py
#     python generate_events.py --schemas-dir custom_schemas/ --output-dir python/models/
# """
#
# import argparse
# import os
# import subprocess
# import sys
# from pathlib import Path
# from typing import List, Set
#
#
# class SchemasGenerator:
#     def __init__(self, schemas_dir: str, output_dir: str, verbose: bool = False):
#         self.schemas_dir = Path(schemas_dir)
#         self.output_dir = Path(output_dir)
#         self.verbose = verbose
#
#         if not self.schemas_dir.exists():
#             raise ValueError(f"Schemas directory does not exist: {self.schemas_dir}")
#
#     def log(self, message: str):
#         """Print message if verbose mode is enabled"""
#         if self.verbose:
#             print(f"[INFO] {message}")
#
#     def find_schema_files(self) -> List[Path]:
#         """
#         Find all schema files (.yaml, .yml, .json) in the schemas directory.
#         Returns list of paths relative to schemas_dir.
#         """
#         schema_files = []
#         extensions = {'.yaml', '.yml', '.json'}
#
#         for ext in extensions:
#             schema_files.extend(self.schemas_dir.rglob(f'*{ext}'))
#
#         # Sort for deterministic order
#         schema_files.sort()
#
#         self.log(f"Found {len(schema_files)} schema files")
#         return schema_files
#
#     def get_relative_path(self, schema_file: Path) -> Path:
#         """Get path relative to schemas directory"""
#         return schema_file.relative_to(self.schemas_dir)
#
#     def get_output_path(self, schema_file: Path) -> Path:
#         """
#         Get the output Python file path for a schema file.
#
#         Example:
#             schemas/events/trading/trade.yaml -> python/events/trading/trade.py
#             schemas/common/base.json -> python/common/base.py
#         """
#         rel_path = self.get_relative_path(schema_file)
#
#         # Replace extension with .py
#         output_path = self.output_dir / rel_path.with_suffix('.py')
#
#         return output_path
#
#     def get_package_dirs(self, schema_files: List[Path]) -> Set[Path]:
#         """
#         Get all unique package directories that need __init__.py files.
#         """
#         package_dirs = {self.output_dir}  # Root package
#
#         for schema_file in schema_files:
#             output_path = self.get_output_path(schema_file)
#
#             # Add all parent directories
#             current = output_path.parent
#             while current != self.output_dir and current != current.parent:
#                 package_dirs.add(current)
#                 current = current.parent
#
#         return package_dirs
#
#     def generate_model(self, schema_file: Path, output_file: Path) -> bool:
#         """
#         Generate a single Pydantic model from a schema file.
#         Returns True if successful, False otherwise.
#         """
#         # Create output directory
#         output_file.parent.mkdir(parents=True, exist_ok=True)
#
#         # Determine input file type
#         file_ext = schema_file.suffix.lower()
#         if file_ext in ['.yaml', '.yml']:
#             input_type = 'jsonschema'  # datamodel-codegen handles YAML automatically
#         elif file_ext == '.json':
#             input_type = 'jsonschema'
#         else:
#             self.log(f"Skipping unsupported file type: {schema_file}")
#             return False
#
#         # Build command
#         cmd = [
#             'datamodel-codegen',
#             '--input', str(schema_file),
#             '--output', str(output_file),
#             '--input-file-type', input_type,
#             '--output-model-type', 'pydantic_v2.BaseModel',
#             '--field-constraints',
#             '--use-standard-collections',
#             '--use-schema-description',
#             '--use-field-description',
#             '--target-python-version', '3.9',
#             '--collapse-root-models',
#             '--use-default',
#             '--use-default-kwarg',
#         ]
#
#         self.log(f"Generating: {self.get_relative_path(schema_file)} -> {output_file.relative_to(self.output_dir)}")
#
#         try:
#             result = subprocess.run(
#                 cmd,
#                 capture_output=True,
#                 text=True,
#                 check=True
#             )
#
#             if self.verbose and result.stdout:
#                 print(result.stdout)
#
#             return True
#
#         except subprocess.CalledProcessError as e:
#             print(f"❌ Error generating {schema_file}:", file=sys.stderr)
#             print(e.stderr, file=sys.stderr)
#             return False
#         except FileNotFoundError:
#             print("❌ Error: datamodel-codegen not found. Install it with:", file=sys.stderr)
#             print("    pip install datamodel-code-generator[http]", file=sys.stderr)
#             sys.exit(1)
#
#     def create_init_file(self, package_dir: Path, schema_files: List[Path]):
#         """
#         Create __init__.py file for a package directory.
#         Imports all models from Python files in that directory.
#         """
#         init_file = package_dir / '__init__.py'
#
#         # Find all Python files in this directory (not subdirectories)
#         py_files = [
#             f for f in package_dir.glob('*.py')
#             if f.name != '__init__.py'
#         ]
#
#         if not py_files and package_dir != self.output_dir:
#             # No models in this directory, just make it a package
#             init_file.write_text('"""Generated event models package"""\n')
#             return
#
#         # Generate imports
#         imports = []
#         for py_file in sorted(py_files):
#             module_name = py_file.stem
#             imports.append(f"from .{module_name} import *")
#
#         # Write __init__.py
#         content = '"""Generated event models package"""\n\n'
#         content += '\n'.join(imports)
#         content += '\n'
#
#         init_file.write_text(content)
#         self.log(f"Created: {init_file.relative_to(self.output_dir.parent)}")
#
#     def generate_all(self) -> bool:
#         """
#         Main generation logic.
#         Returns True if all generations succeeded, False otherwise.
#         """
#         print(f"🔍 Scanning schemas in: {self.schemas_dir}")
#
#         # Find all schema files
#         schema_files = self.find_schema_files()
#
#         if not schema_files:
#             print(f"⚠️  No schema files found in {self.schemas_dir}")
#             return True
#
#         print(f"📝 Generating models in: {self.output_dir}")
#         print()
#
#         # Generate each model
#         success_count = 0
#         fail_count = 0
#
#         for schema_file in schema_files:
#             output_file = self.get_output_path(schema_file)
#
#             if self.generate_model(schema_file, output_file):
#                 success_count += 1
#             else:
#                 fail_count += 1
#
#         print()
#         print(f"✅ Generated {success_count} models")
#
#         if fail_count > 0:
#             print(f"❌ Failed to generate {fail_count} models")
#
#         # Create __init__.py files
#         print()
#         print("📦 Creating package structure...")
#
#         package_dirs = self.get_package_dirs(schema_files)
#         for package_dir in sorted(package_dirs):
#             self.create_init_file(package_dir, schema_files)
#
#         print()
#         print("✨ Done!")
#
#         return fail_count == 0
#
#     def print_structure(self):
#         """Print the directory structure that will be generated"""
#         schema_files = self.find_schema_files()
#
#         print("Schema -> Python mapping:")
#         print()
#
#         for schema_file in schema_files:
#             rel_schema = self.get_relative_path(schema_file)
#             output_file = self.get_output_path(schema_file)
#             rel_output = output_file.relative_to(self.output_dir.parent)
#
#             print(f"  {rel_schema}")
#             print(f"    -> {rel_output}")
#
#         print()
#         print(f"Total: {len(schema_files)} schemas")
#
#
# def main():
#     parser = argparse.ArgumentParser(
#         description='Generate Pydantic models from nested schema directories',
#         formatter_class=argparse.RawDescriptionHelpFormatter,
#         epilog="""
# Examples:
#   # Basic usage
#   python generate_events.py
#
#   # Custom directories
#   python generate_events.py --schemas-dir my_schemas/ --output-dir generated/
#
#   # Preview structure without generating
#   python generate_events.py --dry-run
#
#   # Verbose output
#   python generate_events.py -v
#         """
#     )
#
#     parser.add_argument(
#         '--schemas-dir',
#         default='schemas',
#         help='Directory containing schema files (default: schemas)'
#     )
#
#     parser.add_argument(
#         '--output-dir',
#         default='python/events',
#         help='Output directory for generated Python models (default: python/events)'
#     )
#
#     parser.add_argument(
#         '--dry-run',
#         action='store_true',
#         help='Show what would be generated without actually generating'
#     )
#
#     parser.add_argument(
#         '-v', '--verbose',
#         action='store_true',
#         help='Verbose output'
#     )
#
#     args = parser.parse_args()
#
#     try:
#         generator = SchemasGenerator(
#             schemas_dir=args.schemas_dir,
#             output_dir=args.output_dir,
#             verbose=args.verbose
#         )
#
#         if args.dry_run:
#             generator.print_structure()
#             return 0
#
#         success = generator.generate_all()
#         return 0 if success else 1
#
#     except Exception as e:
#         print(f"❌ Error: {e}", file=sys.stderr)
#         if args.verbose:
#             import traceback
#             traceback.print_exc()
#         return 1
#
#
# if __name__ == '__main__':
#     sys.exit(main())
