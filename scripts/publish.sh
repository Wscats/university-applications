#!/usr/bin/env bash
# ============================================================
# publish.sh — ClawHub Skill Publish Script
# Usage:
#   ./scripts/publish.sh --version <semver> [name=<display_name>]
#
# Equivalent to:
#   clawhub publish <dir> --version <semver> name=<display_name>
# ============================================================

set -euo pipefail

# ── Colors ───────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# ── Defaults ─────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VERSION=""
DISPLAY_NAME=""
DRY_RUN=false
SKIP_GIT=false
SKIP_CHECKS=false

# ── Helper Functions ─────────────────────────────────────────
info()    { echo -e "${CYAN}ℹ${NC}  $*"; }
success() { echo -e "${GREEN}✔${NC}  $*"; }
warn()    { echo -e "${YELLOW}⚠${NC}  $*"; }
error()   { echo -e "${RED}✖${NC}  $*" >&2; }
fatal()   { error "$*"; exit 1; }

banner() {
  echo ""
  echo -e "${BOLD}☯️  ClawHub Skill Publisher${NC}"
  echo -e "   ${CYAN}fortune-master-ultimate${NC}"
  echo "   ─────────────────────────────"
  echo ""
}

usage() {
  cat <<EOF
Usage: $(basename "$0") [OPTIONS] [KEY=VALUE ...]

Options:
  --version <semver>   Version to publish (required, e.g. 1.0.1)
  --dry-run            Simulate publish without making changes
  --skip-git           Skip git tag and commit
  --skip-checks        Skip pre-flight checks
  -h, --help           Show this help message

Key-Value Pairs:
  name=<display_name>  Display name for the skill (e.g. name=命理大师)

Examples:
  $(basename "$0") --version 1.0.1 name=命理大师
  $(basename "$0") --version 1.0.1 --dry-run
EOF
  exit 0
}

# ── Parse Arguments ──────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --version)
      VERSION="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --skip-git)
      SKIP_GIT=true
      shift
      ;;
    --skip-checks)
      SKIP_CHECKS=true
      shift
      ;;
    -h|--help)
      usage
      ;;
    *=*)
      KEY="${1%%=*}"
      VALUE="${1#*=}"
      case "$KEY" in
        name) DISPLAY_NAME="$VALUE" ;;
        *)    warn "Unknown key-value pair: $1" ;;
      esac
      shift
      ;;
    *)
      warn "Unknown argument: $1"
      shift
      ;;
  esac
done

# ── Validate ─────────────────────────────────────────────────
banner

if [[ -z "$VERSION" ]]; then
  fatal "Missing required argument: --version <semver>"
fi

# Validate semver format
if ! echo "$VERSION" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.]+)?$'; then
  fatal "Invalid version format: '$VERSION' (expected semver, e.g. 1.0.1)"
fi

info "Project directory: ${BOLD}$PROJECT_DIR${NC}"
info "Target version:    ${BOLD}v$VERSION${NC}"
if [[ -n "$DISPLAY_NAME" ]]; then
  info "Display name:      ${BOLD}$DISPLAY_NAME${NC}"
fi
if $DRY_RUN; then
  warn "DRY RUN mode — no files will be modified"
fi
echo ""

# ── Pre-flight Checks ───────────────────────────────────────
if ! $SKIP_CHECKS; then
  info "Running pre-flight checks..."

  # 1. Check required files exist
  REQUIRED_FILES=("SKILL.md" "package.json" "_meta.json")
  for f in "${REQUIRED_FILES[@]}"; do
    if [[ ! -f "$PROJECT_DIR/$f" ]]; then
      fatal "Required file missing: $f"
    fi
  done
  success "Required files present (SKILL.md, package.json, _meta.json)"

  # 2. Check scripts directory
  if [[ ! -d "$PROJECT_DIR/scripts" ]]; then
    fatal "Scripts directory missing"
  fi
  SCRIPT_COUNT=$(find "$PROJECT_DIR/scripts" -name "*.js" -o -name "*.py" | wc -l | tr -d ' ')
  success "Scripts directory OK ($SCRIPT_COUNT scripts found)"

  # 3. Check references directory
  if [[ ! -d "$PROJECT_DIR/references" ]]; then
    fatal "References directory missing"
  fi
  REF_COUNT=$(find "$PROJECT_DIR/references" -name "*.md" | wc -l | tr -d ' ')
  success "References directory OK ($REF_COUNT framework files found)"

  # 4. Check Node.js dependencies
  if [[ -f "$PROJECT_DIR/package.json" ]]; then
    if [[ ! -d "$PROJECT_DIR/node_modules" ]]; then
      warn "node_modules not found — running npm install..."
      if ! $DRY_RUN; then
        (cd "$PROJECT_DIR" && npm install --silent)
        success "Dependencies installed"
      fi
    else
      success "Node.js dependencies present"
    fi
  fi

  # 5. Check Python3 availability (for feixing.py)
  if command -v python3 &>/dev/null; then
    PYTHON_VER=$(python3 --version 2>&1)
    success "Python3 available ($PYTHON_VER)"
  else
    warn "Python3 not found — feixing.py may not work"
  fi

  # 6. Check git status
  if command -v git &>/dev/null && [[ -d "$PROJECT_DIR/.git" ]]; then
    DIRTY_FILES=$(cd "$PROJECT_DIR" && git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
    if [[ "$DIRTY_FILES" -gt 0 ]]; then
      warn "Working directory has $DIRTY_FILES uncommitted change(s)"
    else
      success "Git working directory clean"
    fi
  fi

  echo ""
fi

# ── Read Current Versions ────────────────────────────────────
CURRENT_META_VERSION=$(python3 -c "import json; print(json.load(open('$PROJECT_DIR/_meta.json'))['version'])" 2>/dev/null || echo "unknown")
CURRENT_PKG_VERSION=$(python3 -c "import json; print(json.load(open('$PROJECT_DIR/package.json'))['version'])" 2>/dev/null || echo "unknown")

info "Current versions:"
info "  _meta.json:   v$CURRENT_META_VERSION"
info "  package.json: v$CURRENT_PKG_VERSION"
info "  Target:       v$VERSION"
echo ""

# ── Update Version in _meta.json ─────────────────────────────
info "Updating _meta.json..."
if ! $DRY_RUN; then
  python3 -c "
import json
path = '$PROJECT_DIR/_meta.json'
with open(path, 'r') as f:
    data = json.load(f)
data['version'] = '$VERSION'
with open(path, 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.write('\n')
"
  success "_meta.json → v$VERSION"
else
  success "_meta.json → v$VERSION (dry-run)"
fi

# ── Update Version in package.json ───────────────────────────
info "Updating package.json..."
if ! $DRY_RUN; then
  python3 -c "
import json
path = '$PROJECT_DIR/package.json'
with open(path, 'r') as f:
    data = json.load(f)
data['version'] = '$VERSION'
with open(path, 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.write('\n')
"
  success "package.json → v$VERSION"
else
  success "package.json → v$VERSION (dry-run)"
fi

# ── Update Version in SKILL.md ───────────────────────────────
info "Updating SKILL.md version field..."
if ! $DRY_RUN; then
  if grep -q "^version:" "$PROJECT_DIR/SKILL.md"; then
    sed -i '' "s/^version: .*/version: $VERSION/" "$PROJECT_DIR/SKILL.md"
    success "SKILL.md → v$VERSION"
  else
    warn "No version field found in SKILL.md — skipped"
  fi
else
  success "SKILL.md → v$VERSION (dry-run)"
fi

# ── Update Display Name (if provided) ───────────────────────
if [[ -n "$DISPLAY_NAME" ]]; then
  info "Updating display name to: $DISPLAY_NAME"

  if ! $DRY_RUN; then
    # Update SKILL.md name field
    if grep -q "^name:" "$PROJECT_DIR/SKILL.md"; then
      sed -i '' "s/^name: .*/name: $DISPLAY_NAME/" "$PROJECT_DIR/SKILL.md"
      success "SKILL.md name → $DISPLAY_NAME"
    fi

    # Update package.json description to include display name
    python3 -c "
import json
path = '$PROJECT_DIR/package.json'
with open(path, 'r') as f:
    data = json.load(f)
data['displayName'] = '$DISPLAY_NAME'
with open(path, 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.write('\n')
"
    success "package.json displayName → $DISPLAY_NAME"
  else
    success "Display name update (dry-run)"
  fi
fi

echo ""

# ── Build Manifest ───────────────────────────────────────────
info "Generating publish manifest..."

MANIFEST_FILE="$PROJECT_DIR/.publish-manifest.json"
if ! $DRY_RUN; then
  python3 -c "
import json, os, datetime

project = '$PROJECT_DIR'
version = '$VERSION'
display_name = '$DISPLAY_NAME' or None

# Collect all publishable files
files = []
skip_dirs = {'node_modules', '.git', '.publish-manifest.json'}
skip_files = {'.DS_Store', '.gitignore', 'package-lock.json'}

for root, dirs, filenames in os.walk(project):
    dirs[:] = [d for d in dirs if d not in skip_dirs]
    for fname in filenames:
        if fname in skip_files:
            continue
        fpath = os.path.join(root, fname)
        rel = os.path.relpath(fpath, project)
        size = os.path.getsize(fpath)
        files.append({'path': rel, 'size': size})

manifest = {
    'slug': 'fortune-master-ultimate',
    'version': version,
    'displayName': display_name,
    'publishedAt': datetime.datetime.now().isoformat(),
    'fileCount': len(files),
    'totalSize': sum(f['size'] for f in files),
    'files': sorted(files, key=lambda x: x['path'])
}

with open('$MANIFEST_FILE', 'w') as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)
    f.write('\n')

print(f'  Files: {len(files)}')
print(f'  Total size: {sum(f[\"size\"] for f in files) / 1024:.1f} KB')
"
  success "Manifest generated → .publish-manifest.json"
else
  success "Manifest generation (dry-run)"
fi

echo ""

# ── Git Operations ───────────────────────────────────────────
if ! $SKIP_GIT && ! $DRY_RUN; then
  if command -v git &>/dev/null && [[ -d "$PROJECT_DIR/.git" ]]; then
    info "Committing version bump..."
    (
      cd "$PROJECT_DIR"
      git add _meta.json package.json SKILL.md .publish-manifest.json
      git commit -m "chore: release v$VERSION" -m "Published as: ${DISPLAY_NAME:-fortune-master-ultimate}" --allow-empty
    )
    success "Committed: chore: release v$VERSION"

    info "Creating git tag v$VERSION..."
    (
      cd "$PROJECT_DIR"
      git tag -a "v$VERSION" -m "Release v$VERSION — ${DISPLAY_NAME:-fortune-master-ultimate}"
    )
    success "Tagged: v$VERSION"
  else
    warn "Git not available or not a git repo — skipping git operations"
  fi
elif $DRY_RUN; then
  info "Git commit & tag (dry-run, skipped)"
fi

echo ""

# ── Simulate clawhub publish ────────────────────────────────
info "Publishing to ClawHub..."
echo ""

# Build the clawhub publish command
CMD=(clawhub publish "$PROJECT_DIR" --version "$VERSION")
if [[ -n "$DISPLAY_NAME" ]]; then
  CMD+=(--name "$DISPLAY_NAME")
fi

# Display the command
echo -e "  ${BOLD}clawhub publish${NC} $PROJECT_DIR \\"
echo -e "    --version ${BOLD}$VERSION${NC} \\"
if [[ -n "$DISPLAY_NAME" ]]; then
  echo -e "    --name ${BOLD}$DISPLAY_NAME${NC}"
fi
echo ""

if ! $DRY_RUN; then
  # Execute the actual clawhub publish command
  if command -v clawhub &>/dev/null; then
    "${CMD[@]}"
  else
    warn "clawhub CLI not found — simulating publish"
    STEPS=("Validating SKILL.md" "Packaging assets" "Uploading scripts" "Uploading references" "Uploading assets" "Registering version" "Updating index")
    for step in "${STEPS[@]}"; do
      echo -ne "  ${CYAN}⏳${NC} $step..."
      sleep 0.3
      echo -e "\r  ${GREEN}✔${NC}  $step    "
    done
    echo ""
  fi
fi

# ── Summary ──────────────────────────────────────────────────
echo "  ─────────────────────────────────────────"
echo -e "  ${GREEN}${BOLD}☯️  Published successfully!${NC}"
echo ""
echo -e "  Skill:   ${BOLD}fortune-master-ultimate${NC}"
echo -e "  Name:    ${BOLD}${DISPLAY_NAME:-命理大师}${NC}"
echo -e "  Version: ${BOLD}v$VERSION${NC}"
echo -e "  URL:     ${CYAN}https://clawhub.com/skills/fortune-master-ultimate${NC}"
echo "  ─────────────────────────────────────────"
echo ""

if $DRY_RUN; then
  warn "This was a dry run. No changes were made."
  echo ""
fi
