#!/usr/bin/env python3
"""
Quick validation script for skills.
Enforces strict schema compliance for SKILL.md frontmatter.
"""

import re
import sys
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, Set, List

import yaml

MAX_SKILL_NAME_LENGTH = 64

# Define schema for frontmatter validation
# Type definitions: 'str', 'list[str]', 'dict'
SCHEMA: Dict[str, Dict[str, Any]] = {
    "name": {
        "type": "str",
        "required": True,
        "pattern": r"^[a-z0-9-]+$",
        "max_length": MAX_SKILL_NAME_LENGTH
    },
    "description": {
        "type": "str",
        "required": True,
        "max_length": 1024,
        "no_angle_brackets": True
    },
    "version": {
        "type": "str",
        "required": False,
        "pattern": r"^\d+\.\d+\.\d+$"  # Simple semantic versioning
    },
    "authors": {
        "type": "list[str]",
        "required": False
    },
    "license": {
        "type": "str",
        "required": False
    },
    "allowed-tools": {
        "type": "str",  # Sometimes list, but SKILL.md usually uses space-separated string or just string description
        "required": False
    },
    "compatibility": {
        "type": "str",
        "required": False
    },
    "depends-on": {
        "type": "list[str]",
        "required": False
    },
    "related-skills": {
        "type": "list[str]",
        "required": False
    },
    "metadata": {
        "type": "dict",
        "required": False
    },
    "short-description": {
        "type": "str",
        "required": False,
        "max_length": 120
    }
}

def validate_value(key: str, value: Any, rules: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Validates a single value against its schema rules."""

    # Type check
    expected_type = rules.get("type")
    if expected_type == "str" and not isinstance(value, str):
        return False, f"'{key}' must be a string"
    if expected_type == "list[str]":
        if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
            return False, f"'{key}' must be a list of strings"
    if expected_type == "dict" and not isinstance(value, dict):
        return False, f"'{key}' must be a dictionary"

    if isinstance(value, str):
        value = value.strip()

        # Pattern check
        pattern = rules.get("pattern")
        if pattern and not re.match(pattern, value):
             # Specific error for name format
            if key == "name":
                return False, f"'{key}' format invalid. Must be lowercase, digits, and hyphens only."
            return False, f"'{key}' does not match pattern {pattern}"

        # Max length
        max_length = rules.get("max_length")
        if max_length and len(value) > max_length:
            return False, f"'{key}' exceeds maximum length of {max_length}"

        # Specific check for angle brackets
        if rules.get("no_angle_brackets") and ("<" in value or ">" in value):
            return False, f"'{key}' cannot contain angle brackets (< or >)"

        # Name specific checks
        if key == "name":
             if value.startswith("-") or value.endswith("-") or "--" in value:
                return False, f"'{key}' cannot start/end with hyphen or contain consecutive hyphens"

    return True, None

def validate_skill(skill_path: str) -> Tuple[bool, str]:
    """Validates a skill directory against the schema."""
    skill_path = Path(skill_path)

    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, "SKILL.md not found"

    content = skill_md.read_text()
    if not content.startswith("---"):
        return False, "No YAML frontmatter found (must start with ---)"

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter format"

    frontmatter_text = match.group(1)

    try:
        frontmatter = yaml.safe_load(frontmatter_text)
        if not isinstance(frontmatter, dict):
            return False, "Frontmatter must be a YAML dictionary"
    except yaml.YAMLError as e:
        return False, f"Invalid YAML in frontmatter: {e}"

    # Check for unexpected keys
    allowed_keys = set(SCHEMA.keys())
    actual_keys = set(frontmatter.keys())
    unexpected_keys = actual_keys - allowed_keys

    if unexpected_keys:
        return False, f"Unexpected key(s): {', '.join(sorted(unexpected_keys))}. Allowed: {', '.join(sorted(allowed_keys))}"

    # Check required keys and validate values
    for key, rules in SCHEMA.items():
        # Check required
        if rules.get("required") and key not in frontmatter:
            return False, f"Missing required field: '{key}'"

        # Validate value if present
        if key in frontmatter:
            valid, error = validate_value(key, frontmatter[key], rules)
            if not valid:
                return False, error

    return True, "Skill is valid!"


def main():
    if len(sys.argv) != 2:
        print("Usage: python quick_validate.py <skill_directory>")
        sys.exit(1)

    valid, message = validate_skill(sys.argv[1])
    print(message)
    sys.exit(0 if valid else 1)

if __name__ == "__main__":
    main()
