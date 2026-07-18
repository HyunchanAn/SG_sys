import subprocess
import re
import sys

def check_history():
    repo_path = r"\\macbookpro-hc\GitHub\SG_proj_004"
    keywords = ["sg_password", "password=", "postgresql://"]
    
    print(f"Checking Git history in {repo_path}...")
    try:
        # 모든 브랜치와 커밋의 diff를 가져옴
        result = subprocess.run(
            ["git", "log", "-p", "--all"], 
            cwd=repo_path, 
            capture_output=True, 
            text=True, 
            encoding='utf-8', 
            errors='replace'
        )
        
        output = result.stdout
        
        matches = []
        current_commit = None
        current_author = None
        current_date = None
        
        for line in output.split('\n'):
            if line.startswith('commit '):
                current_commit = line.split()[1]
            elif line.startswith('Author:'):
                current_author = line
            elif line.startswith('Date:'):
                current_date = line
            elif line.startswith('+') and not line.startswith('+++'):
                # 추가된 라인에서만 검색 (삭제된 라인은 패스)
                for kw in keywords:
                    if kw.lower() in line.lower():
                        matches.append((current_commit, current_author, current_date, kw, line.strip()))
                        break
        
        if matches:
            print(f"발견된 비밀번호/크리덴셜 관련 노출 로그 ({len(matches)}건):")
            for commit, author, date, kw, content in matches:
                print("-" * 60)
                print(f"Commit : {commit[:8]}")
                print(f"{author}")
                print(f"{date}")
                print(f"Line   : {content}")
        else:
            print("Git 히스토리 내에서 비밀번호 노출 내역이 발견되지 않았습니다.")
            
    except Exception as e:
        print(f"Error executing git command: {e}")

if __name__ == "__main__":
    check_history()
