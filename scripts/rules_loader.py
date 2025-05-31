import os
import glob
import logging
import yaml
import json
from typing import List, Dict
import re

RULES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../.cursor/rules'))
LOG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '../logs/rules_loader.log'))

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def parse_rule_file(filepath: str) -> Dict:
    """Parse a rule file for metadata and return as dict."""
    rule = {
        'name': os.path.splitext(os.path.basename(filepath))[0],
        'path': filepath,
        'alwaysApply': False,
        'type': None,
        'description': '',
        'globs': [],
        'raw': ''
    }
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            rule['raw'] = content
        # Try YAML frontmatter or key: value pairs at top
        lines = content.splitlines()
        meta = {}
        for i, line in enumerate(lines):
            if line.strip() == '---':
                break
            if ':' in line:
                k, v = line.split(':', 1)
                meta[k.strip()] = v.strip()
        # Fallback: look for - '**/glob' lines
        globs = [l.strip('- ').strip() for l in lines if l.strip().startswith('- ')]
        rule['globs'] = globs
        # Assign meta
        for k in ['alwaysApply', 'type', 'description']:
            if k in meta:
                rule[k] = meta[k]
        if 'alwaysApply' in rule:
            rule['alwaysApply'] = str(rule['alwaysApply']).lower() == 'true'
        # Try to extract description from markdown
        for i, line in enumerate(lines):
            if line.lower().startswith('# '):
                rule['description'] = lines[i+1].strip() if i+1 < len(lines) else ''
                break
        # --- Extract code_snippet from Python code block ---
        code_match = re.search(r'```python\s*([\s\S]+?)```', content, re.MULTILINE)
        if code_match:
            rule['code_snippet'] = code_match.group(1).strip()
    except Exception as e:
        logger.error(f"Failed to parse rule file {filepath}: {e}")
    return rule

def load_rules(rules_dir: str = RULES_DIR) -> List[Dict]:
    """Scan rules_dir for .mdc and .md files and parse them."""
    rules = []
    for ext in ('*.mdc', '*.md'):
        for filepath in glob.glob(os.path.join(rules_dir, ext)):
            rule = parse_rule_file(filepath)
            if rule['name']:
                rules.append(rule)
    # Recursively scan subdirs
    for root, dirs, files in os.walk(rules_dir):
        for ext in ('*.mdc', '*.md'):
            for filepath in glob.glob(os.path.join(root, ext)):
                rule = parse_rule_file(filepath)
                if rule['name']:
                    rules.append(rule)
    logger.info(f"Loaded {len(rules)} rules from {rules_dir}")
    return rules

if __name__ == "__main__":
    rules = load_rules()
    print(json.dumps(rules, indent=2, ensure_ascii=False)) 