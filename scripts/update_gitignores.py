import os
from pathlib import Path

def main():
    base_dir = Path("/Users/hyunchanan/Documents/GitHub")
    # All directories starting with SG_
    sg_dirs = [d for d in base_dir.iterdir() if d.is_dir() and d.name.startswith("SG_")]
    
    entries_to_add = ["raw_data/", "*.db", ".env"]
    
    updated_count = 0
    for d in sg_dirs:
        gitignore_path = d / ".gitignore"
        
        # If .gitignore doesn't exist, create it
        if not gitignore_path.exists():
            content = ""
        else:
            with open(gitignore_path, "r", encoding="utf-8") as f:
                content = f.read()
                
        lines = content.splitlines()
        
        needs_update = False
        to_append = []
        
        for entry in entries_to_add:
            # simple check if entry is in lines
            if entry not in lines:
                to_append.append(entry)
                needs_update = True
                
        if needs_update:
            with open(gitignore_path, "a", encoding="utf-8") as f:
                if content and not content.endswith("\n"):
                    f.write("\n")
                if to_append:
                    f.write("\n# Security Rules Auto-Appended\n")
                    for entry in to_append:
                        f.write(f"{entry}\n")
            print(f"Updated {d.name}/.gitignore with {to_append}")
            updated_count += 1
            
    print(f"Finished updating {updated_count} repositories.")

if __name__ == "__main__":
    main()
