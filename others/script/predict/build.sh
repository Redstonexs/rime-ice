#!/usr/bin/env bash
#
# 生成简体预测数据并（在可用时）构建 predict.db。
#
#   bash others/script/predict/build.sh [gen_predict_data.py 的参数...]
#
# 产物输出到 dist/：predict.txt（数据）、predict.db（二进制，需 build_predict）。
#
# build_predict 的获取方式见同目录 README.md。可通过环境变量指定：
#   BUILD_PREDICT=/path/to/build_predict   build_predict 可执行文件
#   PYTHON=python                          指定 python 解释器（默认自动探测）
#   OUT_DIR=/path/to/out                   输出目录（默认 <repo>/dist）

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
OUT_DIR="${OUT_DIR:-${REPO_ROOT}/dist}"
mkdir -p "${OUT_DIR}"

# 选择 python（Windows git-bash 上通常是 python）
PY="${PYTHON:-}"
if [ -z "${PY}" ]; then
  for c in python3 python; do
    if command -v "$c" >/dev/null 2>&1; then PY="$c"; break; fi
  done
fi
[ -n "${PY}" ] || { echo "[predict] 找不到 python，请安装 Python 3"; exit 1; }

echo "[predict] 生成预测数据 -> ${OUT_DIR}/predict.txt"
"${PY}" "${SCRIPT_DIR}/gen_predict_data.py" "$@" -o "${OUT_DIR}/predict.txt"

# 定位 build_predict
BP="${BUILD_PREDICT:-}"
if [ -z "${BP}" ] && command -v build_predict >/dev/null 2>&1; then
  BP="$(command -v build_predict)"
fi

if [ -z "${BP}" ]; then
  echo "[predict] 已生成 ${OUT_DIR}/predict.txt"
  echo "[predict] 未找到 build_predict，跳过 predict.db 构建。"
  echo "          编译方法见 ${SCRIPT_DIR#${REPO_ROOT}/}/README.md，"
  echo "          或设 BUILD_PREDICT=/path/to/build_predict 后重试。"
  exit 0
fi

echo "[predict] 使用 build_predict: ${BP}"
echo "[predict] 构建 -> ${OUT_DIR}/predict.db"
"${BP}" "${OUT_DIR}/predict.db" < "${OUT_DIR}/predict.txt"
ls -l "${OUT_DIR}/predict.db"
echo "[predict] 完成。"
