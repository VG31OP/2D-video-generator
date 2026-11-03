"""
Deep Security Audit of Entire Git History
Scans all commits, trees, and patch diffs for credentials, tokens, session IDs, and cookies.
"""

import os
import sys
import re
import subprocess
from pathlib import Path

if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

def run_cmd(cmd):
    res = subprocess.run(cmd, capture_output=True, text=True, errors="replace", check=True)
    return res.stdout

def main():
    print("=" * 70)
    print("      🔍 COMPREHENSIVE GIT HISTORY SECURITY & CREDENTIAL AUDIT      ")
    print("=" * 70)

    # 1. Fetch all commits
    commits_raw = run_cmd(["git", "log", "--pretty=format:%h %ad %s", "--date=short"]).splitlines()
    print(f"\n[+] Total commits in repository: {len(commits_raw)}")
    for c in commits_raw:
        print(f"    • {c}")

    # 2. Check every commit for tracked filenames
    print("\n[+] Step 1: Checking tracked filenames across every commit...")
    all_clean_files = True
    for line in commits_raw:
        commit_hash = line.split()[0]
        files = run_cmd(["git", "ls-tree", "-r", "--name-only", commit_hash]).splitlines()
        suspect = [f for f in files if any(k in f.lower() for k in [
            "session", "cookie", "storage/instagram", ".env.local", "token", "secret", "private_key", ".sqlite", ".db"
        ]) and not f.endswith(".example")]

        if suspect:
            print(f"    [!] Commit {commit_hash} tracks suspicious files: {suspect}")
            all_clean_files = False

    if all_clean_files:
        print("    [✓] ALL COMMITS CLEAN: No session, cookie, secret, or database files ever tracked!")

    # 3. Scan the full diff text of the entire repository
    print("\n[+] Step 2: Scanning full patch diffs of all commits for secret patterns...")
    full_diff = run_cmd(["git", "log", "-p"])

    patterns = {
        "Instagram Session ID": r'sessionid["\'\s:=]+[a-zA-Z0-9%_-]{10,}',
        "Instagram CSRF Token": r'csrftoken["\'\s:=]+[a-zA-Z0-9%_-]{10,}',
        "Instagram User ID Cookie": r'ds_user_id["\'\s:=]+[0-9]{4,}',
        "Bearer Auth Token": r'Bearer\s+[a-zA-Z0-9_\-\.]{18,}',
        "Google/Gemini API Key": r'AIzaSy[a-zA-Z0-9_\-]{30,}',
        "OpenAI API Key": r'sk-[a-zA-Z0-9]{20,}',
        "Private Key Header": r'-----BEGIN (RSA|EC|OPENSSH|PRIVATE) KEY-----',
        "Hardcoded Password Assignment": r'(password|passwd|pwd)\s*=\s*["\'][^"\']{5,}["\']'
    }

    findings = {}
    for name, pat in patterns.items():
        matches = re.findall(pat, full_diff, flags=re.IGNORECASE)
        # Filter code variable definitions or tests
        filtered = [
            m if isinstance(m, str) else m[0]
            for m in matches
            if not any(safe in str(m).lower() for safe in [
                "args.password", "password: str", "password=none", "password = ''", "password = \"\"",
                "password_hash", "default_password"
            ])
        ]
        findings[name] = filtered

    all_clean_patterns = True
    for name, matches in findings.items():
        if matches:
            print(f"    [!] Potential {name} detected ({len(matches)} occurrences):")
            for m in matches[:3]:
                print(f"        -> {m}")
            all_clean_patterns = False
        else:
            print(f"    [✓] {name}: Clean (0 occurrences)")

    print("\n" + "=" * 70)
    if all_clean_files and all_clean_patterns:
        print("    🎉 AUDIT RESULT: 100% CLEAN — ZERO CREDENTIALS EVER COMMITTED! 🎉")
        print("    No Instagram passwords, cookies, session files, or secrets have")
        print("    ever been pushed or committed to this repository.")
    else:
        print("    ⚠️ AUDIT RESULT: REVIEW FINDINGS ABOVE.")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
