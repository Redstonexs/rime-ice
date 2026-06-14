#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成简体中文输入预测数据（librime-predict 的 build_predict 输入）。

语料来源：本仓库 cn_dicts/ 下的简体词库（词条 + 词频）。

预测原理见 rime/librime-predict：当输入区为空且开启「预测」开关时，
predictor 以「上一个已上屏词条的文本」为 key 在 predict.db 中精确查找，
把候选作为「下一段」预测出来（可按 max_iterations 链式预测）。

因此本脚本把每个多字词条按「前缀 -> 后缀」拆分，仅保留前缀本身也是词库
中存在的词（即用户真的可能单独上屏的单位），例如：

    中华人民共和国 ->  中华 -> 人民共和国
                       中华人民 -> 共和国

输出为 3 列、制表符分隔：  key <TAB> text <TAB> weight
该格式即 build_predict 的标准输入（build_predict 以空白分隔读取三列）。

用法：
    python gen_predict_data.py [选项] [词库文件...]   > predict.txt
不指定词库文件时，默认使用 ../../../cn_dicts/{base,ext,tencent,8105}.dict.yaml
"""

import argparse
import os
import sys
from collections import defaultdict

# CJK 判定：基本区 + 扩展A + 兼容表意 + 〇
def _is_cjk(ch: str) -> bool:
    o = ord(ch)
    return (
        0x4E00 <= o <= 0x9FFF
        or 0x3400 <= o <= 0x4DBF
        or 0xF900 <= o <= 0xFAFF
        or o == 0x3007  # 〇
        or 0x20000 <= o <= 0x2FA1F  # 扩展 B-F（含部分生僻字）
    )


def is_word(s: str) -> bool:
    """纯 CJK、无空白、非空才算词条（自动排除 YAML 头、注释、英文等）。"""
    if not s:
        return False
    return all(_is_cjk(ch) for ch in s)


def parse_dict(path: str):
    """逐行产出 (word, weight)。

    依赖 is_word 过滤头部/注释：rime 词典头部的键（name/version/sort...）均为
    ASCII，注释以 # 开头，故只需取每行第一列、判定是否为纯 CJK 词即可。
    词频取最后一列（若为整数），否则默认 100。
    """
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line or line.lstrip().startswith("#"):
                continue
            cols = line.split("\t")
            word = cols[0].strip()
            if not is_word(word):
                continue
            weight = 100
            if len(cols) >= 2:
                last = cols[-1].strip()
                if last.isdigit():
                    weight = int(last)
            yield word, weight


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    repo = os.path.abspath(os.path.join(here, "..", "..", ".."))
    default_dicts = [
        os.path.join(repo, "cn_dicts", name)
        for name in ("base.dict.yaml", "ext.dict.yaml", "tencent.dict.yaml", "8105.dict.yaml")
    ]

    ap = argparse.ArgumentParser(description="生成简体预测数据 (predict.txt)")
    ap.add_argument("inputs", nargs="*", help="词库文件，缺省使用 cn_dicts 主词库")
    ap.add_argument("--max-candidates", type=int, default=20,
                    help="每个 key 最多保留的候选数（按权重降序），默认 20")
    ap.add_argument("--max-key-len", type=int, default=6,
                    help="前缀（key）最大字数，默认 6")
    ap.add_argument("--min-weight", type=int, default=0,
                    help="过滤掉权重低于该值的源词条，默认 0（不过滤）")
    ap.add_argument("--no-vocab-filter", action="store_true",
                    help="不要求前缀本身是词库中的词（生成更多但更杂的数据）")
    ap.add_argument("--start-count", type=int, default=100,
                    help="为空上下文 '$' 生成的起始词数量（按权重降序），默认 100；0 关闭")
    ap.add_argument("--start-max-len", type=int, default=3,
                    help="'$' 起始词的最大字数，默认 3")
    ap.add_argument("-o", "--output", default="-", help="输出文件，默认 stdout")
    args = ap.parse_args()

    inputs = args.inputs or default_dicts
    missing = [p for p in inputs if not os.path.isfile(p)]
    if missing:
        sys.stderr.write("找不到词库文件:\n  " + "\n  ".join(missing) + "\n")
        return 1

    # 1) 汇总 word -> 最大权重，并构建词表 vocab
    word_weight: dict[str, int] = {}
    for path in inputs:
        n = 0
        for word, weight in parse_dict(path):
            if weight < args.min_weight:
                continue
            if word_weight.get(word, -1) < weight:
                word_weight[word] = weight
            n += 1
        sys.stderr.write(f"[gen] 读取 {os.path.basename(path)}: {n} 行\n")
    vocab = set(word_weight)
    sys.stderr.write(f"[gen] 词表规模: {len(vocab)} 词\n")

    # 2) 前缀 -> 后缀 记录（去重保留最大权重）
    data: dict[str, dict[str, int]] = defaultdict(dict)

    def add(key: str, text: str, w: int) -> None:
        d = data[key]
        if d.get(text, -1) < w:
            d[text] = w

    for word, weight in word_weight.items():
        L = len(word)
        if L < 2:
            continue
        upper = min(L - 1, args.max_key_len)
        for i in range(1, upper + 1):
            prefix = word[:i]
            if (not args.no_vocab_filter) and prefix not in vocab:
                continue
            add(prefix, word[i:], weight)

    # 3) '$' 起始预测：取权重最高的若干短词
    if args.start_count > 0:
        starts = sorted(
            (w for w in word_weight if 1 <= len(w) <= args.start_max_len),
            key=lambda w: (-word_weight[w], w),
        )[: args.start_count]
        for w in starts:
            add("$", w, word_weight[w])

    # 4) 输出：key 排序；候选按权重降序、其次后缀短优先、再 unicode
    out = sys.stdout if args.output == "-" else open(args.output, "w", encoding="utf-8", newline="\n")
    key_count = 0
    rec_count = 0
    try:
        for key in sorted(data):
            cands = sorted(data[key].items(), key=lambda kv: (-kv[1], len(kv[0]), kv[0]))
            if args.max_candidates > 0:
                cands = cands[: args.max_candidates]
            for text, w in cands:
                out.write(f"{key}\t{text}\t{w}\n")
                rec_count += 1
            key_count += 1
    finally:
        if out is not sys.stdout:
            out.close()

    sys.stderr.write(f"[gen] 生成 keys: {key_count}，records: {rec_count}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
