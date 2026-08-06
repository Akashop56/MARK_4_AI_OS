import os
import subprocess
import sys
from datetime import datetime

class GitHubBackupManager:
    """
    MARK_4 Automated GitHub Repository Backup Engine:
    1. Initializes or checks git repository in /sdcard/pa.
    2. Automatically creates a clean .gitignore (prevents sensitive .env leaks).
    3. Stages all Mark_4 architectural files and tools.
    4. Commits with a structured architecture timestamp message.
    5. Pushes safely to remote GitHub origin.
    """
    def __init__(self, repo_dir: str = "/sdcard/pa"):
        self.repo_dir = repo_dir
        self.gitignore_path = os.path.join(self.repo_dir, ".gitignore")

    def run_git_cmd(self, args: list) -> bool:
        try:
            res = subprocess.run(
                ["git"] + args,
                cwd=self.repo_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if res.returncode == 0:
                if res.stdout.strip():
                    print(f"  └─> {res.stdout.strip()}")
                return True
            else:
                print(f"  ⚠️ [Git Warning]: {res.stderr.strip()}")
                return False
        except Exception as e:
            print(f"  ❌ [Git Execution Error]: {e}")
            return False

    def ensure_gitignore(self) -> None:
        """Ensures API keys, temp files, and caches are never leaked."""
        ignore_rules = [
            "# Security & Sensitive Key Files",
            ".env",
            "*.env",
            ".omniroute/",
            "",
            "# Python & Cache Directories",
            "__pycache__/",
            "*.py[cod]",
            "*$py.class",
            ".pytest_cache/",
            "*.bak",
            "*.tmp",
            "",
            "# Temporary Sandbox & Test Output",
            "temp_exec.py",
            "*.log",
            "result.json"
        ]
        
        if not os.path.exists(self.gitignore_path):
            with open(self.gitignore_path, "w", encoding="utf-8") as f:
                f.write("\n".join(ignore_rules) + "\n")
            print("🛡️ [Security]: Created strict .gitignore to protect .env and API keys.")

    def execute_backup(self, remote_url: str = "") -> None:
        print("="*60)
        print("🚀 STARTING MARK_4 MASTER ARCHITECTURE GITHUB BACKUP")
        print("="*60)

        # 0. Security rules
        self.ensure_gitignore()

        # 1. Initialize git if not already present
        if not os.path.exists(os.path.join(self.repo_dir, ".git")):
            print("📦 [Step 1]: Initializing new Git repository...")
            self.run_git_cmd(["init"])
        else:
            print("📦 [Step 1]: Existing Git repository detected.")

        # 2. Add remote origin if provided
        if remote_url:
            print(f"🔗 [Step 2]: Configuring remote origin -> {remote_url}")
            self.run_git_cmd(["remote", "remove", "origin"])
            self.run_git_cmd(["remote", "add", "origin", remote_url])
            self.run_git_cmd(["branch", "-M", "main"])
        else:
            print("🔗 [Step 2]: Checking existing remote origins...")
            self.run_git_cmd(["remote", "-v"])

        # 3. Stage files safely
        print("📂 [Step 3]: Staging MARK_4 architecture and tool files...")
        self.run_git_cmd(["add", "Mark_4/", ".gitignore"])

        # 4. Commit changes
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_msg = f"🤖 MARK_4 Autonomous AI OS Backup - {timestamp} (6-Layer Architecture Complete)"
        print(f"💾 [Step 4]: Committing changes -> '{commit_msg}'...")
        commit_success = self.run_git_cmd(["commit", "-m", commit_msg])

        if not commit_success:
            print("  ℹ️ No new changes to commit (working directory clean).")

        # 5. Push to Github
        print("☁️ [Step 5]: Pushing to GitHub repository...")
        push_success = self.run_git_cmd(["push", "-u", "origin", "main"])

        print("="*60)
        if push_success:
            print("✅ GITHUB BACKUP SUCCESSFUL! Your autonomous AI architecture is safe.")
        else:
            print("⚠️ NOTE: If push failed, make sure your GitHub Personal Access Token (PAT)")
            print("   or SSH key is configured in Termux, and remote origin is set!")
            print("   To set remote URL manually: git remote add origin <YOUR_REPO_URL>")
        print("="*60)

if __name__ == "__main__":
    url_arg = sys.argv[1] if len(sys.argv) > 1 else ""
    manager = GitHubBackupManager()
    manager.execute_backup(remote_url=url_arg)
