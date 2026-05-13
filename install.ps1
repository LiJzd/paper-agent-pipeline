# Paper Agent Pipeline - Windows 安装脚本
# 用法: .\install.ps1

$ErrorActionPreference = "Stop"

$CLAUDE_DIR = "$env:USERPROFILE\.claude"
$REPO_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "=== Paper Agent Pipeline 安装 ===" -ForegroundColor Cyan
Write-Host ""

# 检查 ~/.claude 目录
if (-not (Test-Path $CLAUDE_DIR)) {
    Write-Host "创建 $CLAUDE_DIR ..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $CLAUDE_DIR -Force | Out-Null
}

# 1. 复制智能体定义和脚本
Write-Host "[1/4] 复制智能体定义到 $CLAUDE_DIR\agents\ ..." -ForegroundColor Green
if (-not (Test-Path "$CLAUDE_DIR\agents")) {
    New-Item -ItemType Directory -Path "$CLAUDE_DIR\agents" -Force | Out-Null
}
Copy-Item "$REPO_DIR\agents\paper_*.md" "$CLAUDE_DIR\agents\" -Force
$agentCount = (Get-ChildItem "$REPO_DIR\agents\paper_*.md").Count
Write-Host "  已复制 $agentCount 个智能体文件" -ForegroundColor Gray

# 复制脚本文件
if (Test-Path "$REPO_DIR\agents\assets") {
    if (-not (Test-Path "$CLAUDE_DIR\agents\assets\components")) {
        New-Item -ItemType Directory -Path "$CLAUDE_DIR\agents\assets\components" -Force | Out-Null
    }
    Copy-Item "$REPO_DIR\agents\assets\components\*.py" "$CLAUDE_DIR\agents\assets\components\" -Force
    Write-Host "  已复制脚本文件到 agents\assets\components\" -ForegroundColor Gray
}

# 2. 复制内置 Skill
Write-Host "[2/4] 复制 literature-search Skill 到 $CLAUDE_DIR\skills\ ..." -ForegroundColor Green
if (-not (Test-Path "$CLAUDE_DIR\skills\literature-search\scripts")) {
    New-Item -ItemType Directory -Path "$CLAUDE_DIR\skills\literature-search\scripts" -Force | Out-Null
}
Copy-Item "$REPO_DIR\skills\literature-search\SKILL.md" "$CLAUDE_DIR\skills\literature-search\" -Force
Copy-Item "$REPO_DIR\skills\literature-search\scripts\s2_search.py" "$CLAUDE_DIR\skills\literature-search\scripts\" -Force
Write-Host "  已复制 literature-search Skill" -ForegroundColor Gray

# 3. 复制命令桥接文件
Write-Host "[3/4] 复制 Nature Skill 命令桥接到 $CLAUDE_DIR\commands\ ..." -ForegroundColor Green
if (-not (Test-Path "$CLAUDE_DIR\commands")) {
    New-Item -ItemType Directory -Path "$CLAUDE_DIR\commands" -Force | Out-Null
}
Copy-Item "$REPO_DIR\commands\nature-*.md" "$CLAUDE_DIR\commands\" -Force
Write-Host "  已复制 6 个命令桥接文件" -ForegroundColor Gray

# 4. 处理 CLAUDE.md
Write-Host "[4/4] 处理 CLAUDE.md 配置 ..." -ForegroundColor Green
$CLAUDE_MD = "$CLAUDE_DIR\CLAUDE.md"
$PAPER_SECTION = Get-Content "$REPO_DIR\CLAUDE.md" -Raw -Encoding UTF8

if (Test-Path $CLAUDE_MD) {
    $existing = Get-Content $CLAUDE_MD -Raw -Encoding UTF8
    if ($existing -match "论文工作流") {
        Write-Host "  CLAUDE.md 已包含论文工作流配置，跳过" -ForegroundColor Yellow
    } else {
        Write-Host "  追加论文工作流配置到 CLAUDE.md ..." -ForegroundColor Yellow
        Add-Content -Path $CLAUDE_MD -Value "`n---`n`n$PAPER_SECTION" -Encoding UTF8
    }
} else {
    Write-Host "  创建新的 CLAUDE.md ..." -ForegroundColor Yellow
    Set-Content -Path $CLAUDE_MD -Value $PAPER_SECTION -Encoding UTF8
}

Write-Host ""
Write-Host "=== 安装完成！===" -ForegroundColor Cyan
Write-Host ""
Write-Host "还需要安装外部依赖：" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. nature-skills (MIT 许可证):" -ForegroundColor White
Write-Host "     git clone https://github.com/Yuan1z0825/nature-skills ~/.claude/skills/nature-skills" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. word-document-processor (Anthropic 专有):" -ForegroundColor White
Write-Host "     通过 Claude Code Skill 市场安装" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. Python 依赖:" -ForegroundColor White
Write-Host "     pip install requests python-docx" -ForegroundColor Gray
Write-Host ""
Write-Host "使用方式：在 Claude Code 中输入" -ForegroundColor White
Write-Host '     帮我写一篇论文，主题是：[你的主题]' -ForegroundColor Gray
Write-Host ""
