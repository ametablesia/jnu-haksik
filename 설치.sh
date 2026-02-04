#!/usr/bin/env bash

set -e
echo "▶ 학식 CLI 설치 시작"

# ------------------------------
# 경로 설정
# ------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_BIN="$SCRIPT_DIR/dist/haksik"
DEST_DIR="$HOME/.local/bin"
DEST_BIN="$DEST_DIR/haksik"
ALIAS_FILE="$HOME/.bash_aliases_haksik"
BASHRC_FILE="$HOME/.bashrc"

# ------------------------------
# 실행파일 확인
# ------------------------------
if [ ! -x "$SRC_BIN" ]; then
    echo "[ERROR] dist/haksik 실행파일을 찾을 수 없습니다."
    exit 1
fi

# ------------------------------
# ~/.local/bin 생성
# ------------------------------
mkdir -p "$DEST_DIR"

# ------------------------------
# 실행파일 복사
# ------------------------------
echo "▶ 실행파일 복사: $DEST_BIN"
cp "$SRC_BIN" "$DEST_BIN"
chmod +x "$DEST_BIN"

# ------------------------------
# alias 파일 생성
# ------------------------------
echo "▶ alias 파일 생성: $ALIAS_FILE"

cat > "$ALIAS_FILE" <<'EOF'
# =====================================
# 학식 CLI alias
# =====================================

HAKSIK_BIN="$HOME/.local/bin/haksik"

if [ -x "$HAKSIK_BIN" ]; then
    alias 학식="$HAKSIK_BIN"
fi

# 자주 쓰는 단축 (선택)
alias 점심="학식 오늘 중식"
alias 저녁="학식 오늘 석식"
EOF

# ------------------------------
# .bashrc에 source 등록
# ------------------------------
if ! grep -q "bash_aliases_haksik" "$BASHRC_FILE"; then
    echo "▶ .bashrc에 alias 로드 추가"
    cat >> "$BASHRC_FILE" <<'EOF'

# 학식 alias 로드
if [ -f "$HOME/.bash_aliases_haksik" ]; then
    source "$HOME/.bash_aliases_haksik"
fi
EOF
else
    echo "▶ .bashrc에 이미 alias 로드가 존재함 (스킵)"
fi

# ------------------------------
# PATH 확인
# ------------------------------
if ! echo "$PATH" | grep -q "$HOME/.local/bin"; then
    echo "▶ PATH에 ~/.local/bin 추가"
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$BASHRC_FILE"
fi

# ------------------------------
# 완료
# ------------------------------
echo
echo "✅ 설치 완료!"
echo "   새 터미널을 열거나 다음 명령 실행:"
echo "   source ~/.bashrc"
echo
echo "   사용 예:"
echo "     학식"
echo "     학식 내일 석식"
echo "     학식 사이트"
