#!/usr/bin/env bash
# invest-committee 一鍵安裝腳本 (macOS / Linux)
# 做四件事:裝 skill、加 twstock 台股資料源、建投資設定目錄、印下一步。
# 安全設計:每個會改動系統的步驟都先問你;絕不覆蓋你既有的設定檔。
set -euo pipefail

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="${HOME}/.claude/skills"
SKILL_DEST="${SKILLS_DIR}/invest-committee"
DATA_DIR="${HOME}/.invest-committee"

say()  { printf '\n\033[1;36m==> %s\033[0m\n' "$*"; }
ok()   { printf '    \033[1;32m✓\033[0m %s\n' "$*"; }
warn() { printf '    \033[1;33m!\033[0m %s\n' "$*"; }
ask()  { local a; read -r -p "    $1 [y/N] " a; [[ "$a" =~ ^[Yy]$ ]]; }

say "invest-committee 安裝開始"
echo "    來源: $SRC_DIR"
echo "    skill 目的地: $SKILL_DEST"

# --- 步驟 1:安裝 skill 本體 ---
say "步驟 1/4 — 安裝 skill 到 $SKILL_DEST"
if [[ ! -f "${SRC_DIR}/SKILL.md" ]]; then
  echo "    找不到 SKILL.md,請在解壓後的 invest-committee/ 目錄裡執行本腳本。" >&2; exit 1
fi
mkdir -p "$SKILLS_DIR"
if [[ -d "$SKILL_DEST" ]]; then
  warn "已存在舊版 $SKILL_DEST"
  if ask "覆蓋更新?(會先備份成 invest-committee.bak.時間戳)"; then
    mv "$SKILL_DEST" "${SKILL_DEST}.bak.$(date +%Y%m%d-%H%M%S)"
  else
    warn "跳過 skill 安裝"; SKIP_SKILL=1
  fi
fi
if [[ "${SKIP_SKILL:-0}" != "1" ]]; then
  mkdir -p "$SKILL_DEST"
  # 只複製 skill 執行需要的檔,排除安裝物、說明檔、git 與備份
  ( cd "$SRC_DIR" && tar --exclude='.git' --exclude='.git/*' --exclude='.gitignore' \
      --exclude='install.sh' --exclude='INSTALL*.md' --exclude='README*.md' --exclude='*.bak.*' \
      -cf - . ) | ( cd "$SKILL_DEST" && tar -xf - )
  ok "skill 已安裝"
fi

# --- 步驟 2:台股資料源 twstock MCP ---
say "步驟 2/4 — 台股資料源 twstock MCP (Docker)"
if ! command -v docker >/dev/null 2>&1; then
  warn "未偵測到 Docker——台股功能需要它。請先裝 Docker Desktop 後再手動執行:"
  echo "      claude mcp add --scope user twstock -- docker run -i --rm --pull=always -e MCP_STDIO=1 ghcr.io/twjackysu/twsemcpserver:latest"
elif ! command -v claude >/dev/null 2>&1; then
  warn "未偵測到 claude CLI——請在互動式 Claude Code 用 /mcp 加,或安裝 CLI 後執行上述指令。"
else
  if claude mcp list 2>/dev/null | grep -q '^twstock\b'; then
    ok "twstock 已存在,略過"
  elif ask "現在執行 claude mcp add 掛上 twstock 台股資料源?"; then
    claude mcp add --scope user twstock -- docker run -i --rm --pull=always -e MCP_STDIO=1 ghcr.io/twjackysu/twsemcpserver:latest \
      && ok "twstock 已加入(重開 Claude Code 後用 /mcp 確認)" \
      || warn "加入失敗,請手動執行 INSTALL.md 步驟 2 的指令"
  else
    warn "跳過;之後可自行執行 INSTALL.md 步驟 2 的指令"
  fi
fi

# --- 步驟 3:投資設定目錄 ---
say "步驟 3/4 — 建立投資設定目錄 $DATA_DIR"
mkdir -p "${DATA_DIR}/reports"
for f in profile watchlist; do
  if [[ -f "${DATA_DIR}/${f}.md" ]]; then
    warn "${f}.md 已存在,保留你的版本(不覆蓋)"
  else
    cp "${SRC_DIR}/assets/templates/${f}.md" "${DATA_DIR}/${f}.md" && ok "建立 ${f}.md"
  fi
done

# --- 步驟 4:富途提示 + 下一步 ---
say "步驟 4/4 — 完成"
echo "    (選裝)美/港/A股即時資料:在 Claude Code 輸入 /install-futu-opend 安裝 Futu OpenD。"
echo ""
ok "安裝完成!下一步:"
echo "    1. 編輯 ${DATA_DIR}/profile.md 填你的資金/部位上限/風險承受度"
echo "    2. 重開 Claude Code"
echo "    3. 直接說「幫我分析台積電」或「看 2330 技術面」開始用"
echo ""
echo "    完整說明見 INSTALL.md。研究支援工具,非投資建議。"
