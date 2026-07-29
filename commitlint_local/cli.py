import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

ALLOWED_TYPES = {
    "feat",
    "fix",
    "docs",
    "style",
    "refactor",
    "perf",
    "test",
    "build",
    "ci",
    "chore",
    "revert",
}

DEFAULT_CONFIG_PATHS = [".commitlintrc", ".commitlintrc.json", "commitlint.config.json"]


class ValidationError(Exception):
    status_code = 1


def parse_commit_message(message: str) -> Dict[str, str]:
    before_colon, sep, after = message.partition(":")
    if sep == "":
        raise ValidationError("commit message must include ':' after the first segment")

    before = before_colon.strip()
    parts = before.split("(")
    if len(parts) == 1:
        type_label = parts[0].strip().lower()
        scope = ""
    else:
        type_label = parts[0].strip().lower()
        scope = parts[1].rstrip(")").strip()

    description = after.strip()
    return {"type": type_label, "scope": scope, "description": description}


def load_config(repo_root: Path, explicit_config: Optional[str]) -> Tuple[Dict[str, object], Optional[Path]]:
    candidates = [explicit_config] if explicit_config else DEFAULT_CONFIG_PATHS
    for candidate in candidates:
        path = repo_root.joinpath(candidate) if not Path(candidate).is_absolute() else Path(candidate)
        if not path.exists():
            continue
        if path.suffix in {".json", ".jsonc"}:
            with path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        else:
            parsed: Dict[str, object] = {"rules": {}}
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.partition("#")[0].strip()
                if not line:
                    continue
                key, sep, value = line.partition("=")
                parsed[key.strip()] = _decode_env_value(value.strip())
            payload = parsed
        return payload, path
    return {}, None


def _decode_env_value(value: str) -> object:
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    try:
        return int(value)
    except ValueError:
        return value


def validate_commit_message(
    message: str,
    repo_root: Optional[Path] = None,
    config_path: Optional[str] = None,
    allow_empty: bool = False,
) -> Tuple[bool, Optional[str]]:
    if message.strip() == "":
        if allow_empty:
            return True, None
        return False, "commit message must not be empty"
    parsed = parse_commit_message(message)
    footer = ""
    if "\n\n" in message:
        parsed["description"], footer = parsed["description"].split("\n\n", 1)

    type_label = parsed["type"]
    scope = parsed["scope"]
    description = parsed["description"]

    if type_label not in ALLOWED_TYPES:
        return False, f"commit type '{type_label}' is not in {sorted(ALLOWED_TYPES)}"

    if description == "":
        return False, "description is empty"

    min_description_length = 5
    rules: Dict[str, object] = {}
    root = repo_root or Path.cwd()
    config, _ = load_config(root, config_path)
    rules = config.get("rules", {}) if isinstance(config, dict) else {}

    min_description_length = int(rules.get("min-description-length", min_description_length))
    if len(description) < min_description_length:
        return False, f"description is too short: expected at least {min_description_length} characters"

    if scope and not scope.islower():
        return False, f"scope '{scope}' must be all lowercase"

    return True, None


def run_validation(
    message: str,
    repo_root: Optional[Path] = None,
    config_path: Optional[str] = None,
    config_required: bool = False,
    allow_empty: bool = False,
) -> int:
    try:
        is_valid, meta = validate_commit_message(message, repo_root, config_path, allow_empty=allow_empty)
        if not is_valid:
            print(f"FAIL: {meta}")
            return 1
        payload = {"ok": True}
        if isinstance(meta, str):
            payload["footer"] = meta
        print(json.dumps(payload))
        return 0
    except ValidationError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1


def install_hook(repo_root: Path, hook_path: str = ".git/hooks/commit-msg") -> None:
    target = repo_root / hook_path
    target.parent.mkdir(parents=True, exist_ok=True)
    real_hook = f"""\
#!/bin/sh
commit_message_file="$1"
commit_src="$2"
commit_hash="$3"
error_message=$(python -m commitlint_local.cli validate --message "$(cat "$commit_message_file")" --repo-root "{repo_root.resolve()}")
rc=$?
if [ $rc -ne 0 ]; then
    echo "$error_message"
fi
exit $rc
"""
    target.write_text(real_hook, encoding="utf-8")
    os.chmod(target, 0o755)


def resolve_repo_root(path: Optional[Path]) -> Path:
    candidate = path or Path.cwd()
    current = candidate.resolve()
    while True:
        if (current / ".git").exists():
            return current
        if current.parent == current:
            return candidate.resolve()
        current = current.parent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="commitlint")
    subparsers = parser.add_subparsers(dest="command")

    validate = subparsers.add_parser("validate")
    validate.add_argument("message", nargs="?")
    validate.add_argument("--repo-root", type=Path)
    validate.add_argument("--config")
    validate.add_argument("--allow-empty", action="store_true")

    install = subparsers.add_parser("install-hook")
    install.add_argument("--repo-root", type=Path)

    subparsers.add_parser("list-types")
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    parser = build_parser()
    arguments = parser.parse_args(argv)
    if not arguments.command:
        parser.print_help()
        return 1

    if arguments.command == "list-types":
        for item in sorted(ALLOWED_TYPES):
            print(item)
        return 0

    if arguments.command == "install-hook":
        repo_root = resolve_repo_root(arguments.repo_root)
        install_hook(repo_root)
        path = repo_root / ".git/hooks/commit-msg"
        print(f"installed pre-commit hook: {path}")
        return 0

    message = arguments.message or os.environ.get("COMMITLINT_MESSAGE", "")
    if not message:
        print("FAIL: no commit message provided; pass an argument or COMMITLINT_MESSAGE", file=sys.stderr)
        return 1

    repo_root = resolve_repo_root(arguments.repo_root)
    return run_validation(message, repo_root, arguments.config, allow_empty=arguments.allow_empty)


if __name__ == "__main__":
    raise SystemExit(main())
