import os
import subprocess
import glob

base_dir = "/Users/hyunchanan/Documents/GitHub"
for d in os.listdir(base_dir):
    full_path = os.path.join(base_dir, d)
    if d.startswith("SG_") and os.path.isdir(os.path.join(full_path, ".git")):
        print(f"--- Processing {d} ---")
        
        # git add .
        subprocess.run(["git", "add", "."], cwd=full_path)
        
        # Unstage date-prefixed md files
        md_files = glob.glob(os.path.join(full_path, "[0-9][0-9][0-9][0-9][0-9][0-9]_[0-9][0-9][0-9][0-9]*.md"))
        for md_file in md_files:
            basename = os.path.basename(md_file)
            print(f"Unstaging {basename}")
            subprocess.run(["git", "restore", "--staged", basename], cwd=full_path)
            subprocess.run(["git", "reset", "HEAD", basename], cwd=full_path, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            
        # Check diff
        diff_res = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=full_path)
        if diff_res.returncode != 0:
            print("Committing and pushing...")
            subprocess.run(["git", "commit", "-m", "Auto-commit after Adhesion Conditional Model Upgrade & UI integration"], cwd=full_path)
            subprocess.run(["git", "push"], cwd=full_path)
        else:
            print("No changes to commit.")
