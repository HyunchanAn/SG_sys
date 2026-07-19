# PowerShell script for running tests on Windows
$ErrorActionPreference = "Continue"

$BASE_DIR = "\\macbookpro-hc\GitHub"
$env:PYTHONPATH = "$BASE_DIR\SG_proj_001;$BASE_DIR\SG_proj_002;$BASE_DIR\SG_proj_003;$BASE_DIR\SG_proj_004;$BASE_DIR\SG_proj_005;$BASE_DIR\SG_proj_006;$BASE_DIR\SG_proj_007;$BASE_DIR\SG_proj_008;$BASE_DIR\SG_proj_009;$BASE_DIR\SG_proj_010;$BASE_DIR\SG_proj_011;$BASE_DIR\SG_proj_012;$BASE_DIR\SG_proj_013;$BASE_DIR\SG_proj_014;$BASE_DIR\SG_proj_015;$BASE_DIR\SG_sys;$env:PYTHONPATH"

$REPOS = @(
    "SG_sys", "SG_DB",
    "SG_proj_001", "SG_proj_002", "SG_proj_003", "SG_proj_004",
    "SG_proj_005", "SG_proj_006", "SG_proj_007", "SG_proj_009",
    "SG_proj_010", "SG_proj_011", "SG_proj_012", "SG_proj_013",
    "SG_proj_014", "SG_proj_015",
    "SG_integration_step1", "SG_integration_step2", "SG_integration_step3"
)

New-Item -ItemType Directory -Force -Path "$BASE_DIR\SG_sys\reports" | Out-Null
$REPORT_FILE = "$BASE_DIR\SG_sys\reports\test_report_windows.md"

"# Repository E2E & Consistency Test Report (Windows)" | Out-File -FilePath $REPORT_FILE
"Date: $(Get-Date)" | Out-File -FilePath $REPORT_FILE -Append
"" | Out-File -FilePath $REPORT_FILE -Append

$MISSING_REPOS = @()
foreach ($REPO in $REPOS) {
    if (-not (Test-Path "$BASE_DIR\$REPO")) {
        $MISSING_REPOS += $REPO
    }
}

if ($MISSING_REPOS.Count -ne 0) {
    "## 🚨 CRITICAL ERROR: Workspace Integrity Check Failed" | Out-File -FilePath $REPORT_FILE -Append
    "The following required modules are missing from the workspace:" | Out-File -FilePath $REPORT_FILE -Append
    foreach ($M in $MISSING_REPOS) {
        "- $M" | Out-File -FilePath $REPORT_FILE -Append
    }
    "" | Out-File -FilePath $REPORT_FILE -Append
    "**Status: FATAL ERROR (Missing Repositories) :x:**" | Out-File -FilePath $REPORT_FILE -Append
    Write-Host "Aborting tests due to structural integrity failure."
    exit 1
}

Write-Host "Spinning up Root Orchestration (MSA PoC) for SG_proj_001 and SG_proj_004 on Windows..."
Set-Location -Path "$BASE_DIR\SG_sys"
docker-compose -f docker-compose-windows.yml up -d --build

Write-Host "Waiting 15 seconds for DB to initialize..."
Start-Sleep -Seconds 15
Write-Host "Restoring DB dump to sg_proj_004_db..."
Get-Content -Path "$BASE_DIR\SG_DB\init_scripts\init.sql" -Raw | docker exec -i sg_proj_004_db psql -U sg_user -d sg_proj_004

foreach ($REPO in $REPOS) {
    "## $REPO" | Out-File -FilePath $REPORT_FILE -Append
    Write-Host "Running tests in $REPO..."
    
    Set-Location -Path "$BASE_DIR\$REPO"
    
    $env:OMP_NUM_THREADS = "1"
    $env:MKL_NUM_THREADS = "1"
    
    $EXEC_CMD = "python -m pytest"
    $IS_DOCKER = $false
    if ($REPO -eq "SG_proj_001") {
        $EXEC_CMD = "docker exec sg_proj_001_api pytest"
        $IS_DOCKER = $true
    } elseif ($REPO -eq "SG_proj_004") {
        $EXEC_CMD = "docker exec sg_proj_004_api pytest"
        $IS_DOCKER = $true
    }
    
    if (Test-Path "tests") {
        if ($IS_DOCKER) {
            Invoke-Expression "$EXEC_CMD tests/" | Out-File -FilePath "test_out.log"
        } else {
            python -m pytest tests/ 2>&1 | Out-File -FilePath "test_out.log"
        }
        
        $EXIT_CODE = $LASTEXITCODE
        
        '```text' | Out-File -FilePath $REPORT_FILE -Append
        Get-Content "test_out.log" | Out-File -FilePath $REPORT_FILE -Append
        '```' | Out-File -FilePath $REPORT_FILE -Append
        
        if ($EXIT_CODE -eq 0 -or $EXIT_CODE -eq 5) {
            "**Status: PASSED :white_check_mark:**" | Out-File -FilePath $REPORT_FILE -Append
        } else {
            "**Status: FAILED :x:**" | Out-File -FilePath $REPORT_FILE -Append
        }
    } else {
        $TEST_FILES = Get-ChildItem -Path . -Recurse -Depth 1 -Filter "test_*.py"
        if ($TEST_FILES) {
            $FILE_NAMES = $TEST_FILES.Name -join ' '
            if ($IS_DOCKER) {
                Invoke-Expression "$EXEC_CMD $FILE_NAMES" | Out-File -FilePath "test_out.log"
            } else {
                Invoke-Expression "python -m pytest $FILE_NAMES" 2>&1 | Out-File -FilePath "test_out.log"
            }
            $EXIT_CODE = $LASTEXITCODE
            
            '```text' | Out-File -FilePath $REPORT_FILE -Append
            Get-Content "test_out.log" | Out-File -FilePath $REPORT_FILE -Append
            '```' | Out-File -FilePath $REPORT_FILE -Append
            
            if ($EXIT_CODE -eq 0 -or $EXIT_CODE -eq 5) {
                "**Status: PASSED :white_check_mark:**" | Out-File -FilePath $REPORT_FILE -Append
            } else {
                "**Status: FAILED :x:**" | Out-File -FilePath $REPORT_FILE -Append
            }
        } else {
            "No tests found." | Out-File -FilePath $REPORT_FILE -Append
        }
    }
    "" | Out-File -FilePath $REPORT_FILE -Append
}

Write-Host "Tests completed."
