# 输入预测 / predict.db 构建

雾凇拼音的简体中文**输入预测**（基于 [librime-predict](https://github.com/rime/librime-predict)）。
本目录的脚本从 `cn_dicts/` 生成预测数据，再用 librime-predict 的 `build_predict`
工具编译为二进制 `predict.db`。

部署使用教程见 [`others/docs/Prediction.md`](../../docs/Prediction.md)。

## 原理

启用「预测」后，当输入区为空时，predictor 以**上一个已上屏词条的文本**为键，
在 `predict.db` 中精确查找，把后续文字作为候选预测出来（可按 `max_iterations` 链式预测）。

`predict.db` 是 librime 私有的二进制格式（Darts 双数组 trie + StringTable，**不是 SQLite**），
文件头为 `Rime::Predict/1.0`。键 = 上一个上屏词，值 = 预测的后续文字，并带权重。

本项目用 `cn_dicts/` 里的简体词条作为语料：把每个多字词按「前缀 → 后缀」拆分，
且只保留**前缀本身也是词库中的词**（即用户真的可能单独上屏的单位）。例如
`中华人民共和国` 生成 `中华 → 人民共和国`、`中华人民 → 共和国`。词频沿用词库权重，
因此 `北京 → 市/大学/时间…`、`苹果 → 电脑/公司/…` 等预测会按常用度排序。

## 文件

- `gen_predict_data.py`：从 `cn_dicts/` 生成 3 列预测数据 `key<TAB>text<TAB>weight`
  （即 `build_predict` 的标准输入）。纯 Python，无第三方依赖。
- `build.sh`：生成数据，并在能找到 `build_predict` 时构建 `predict.db`，输出到 `dist/`。

## 快速使用

已有 `build_predict` 时：

```bash
BUILD_PREDICT=/path/to/build_predict bash others/script/predict/build.sh
# 产物：dist/predict.txt、dist/predict.db
```

只想生成/调参数据：

```bash
python others/script/predict/gen_predict_data.py --help
python others/script/predict/gen_predict_data.py -o dist/predict.txt
```

常用参数：`--max-candidates`（每键候选上限，默认 20）、`--max-key-len`（前缀最大字数，默认 6）、
`--min-weight`（过滤低频源词条）、`--no-vocab-filter`（不要求前缀是词，数据更多更杂）、
`--start-count`（空输入 `$` 的起始词数量）。

## 如何获得 build_predict

`build_predict` 必须随 librime 一起编译（它使用 librime 的内部符号）。发行版自带的
librime 运行库**通常不含头文件、也不导出这些符号**，无法直接链接。

### Linux（与 CI 一致，最稳）

```bash
git clone --depth 1 https://github.com/rime/librime
git clone --depth 1 https://github.com/rime/librime-predict librime/plugins/predict
cd librime
sudo apt-get install -y cmake ninja-build g++ \
  libboost-dev libboost-regex-dev libgoogle-glog-dev libgflags-dev \
  libleveldb-dev libmarisa-dev libyaml-cpp-dev libopencc-dev
cmake -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DBUILD_TEST=OFF
cmake --build build --target build_predict
# 插件是独立子项目，产物在 build/plugins/predict/bin/build_predict
```

### Windows / MSYS2（UCRT64，最小编译，无需编译整个 librime）

在 **MSYS2 UCRT64** shell 中：

```bash
pacman -S --needed mingw-w64-ucrt-x86_64-gcc \
  mingw-w64-ucrt-x86_64-boost mingw-w64-ucrt-x86_64-glog \
  mingw-w64-ucrt-x86_64-marisa mingw-w64-ucrt-x86_64-leveldb \
  mingw-w64-ucrt-x86_64-yaml-cpp mingw-w64-ucrt-x86_64-opencc

git clone --depth 1 https://github.com/rime/librime
git clone --depth 1 https://github.com/rime/librime-predict

# 最小 build_config.h（关闭日志，避免链接 glog）
printf '#ifndef RIME_BUILD_CONFIG_H_\n#define RIME_BUILD_CONFIG_H_\n#define RIME_DATA_DIR "rime-data"\n#define RIME_PLUGINS_DIR "rime-plugins"\n#endif\n' \
  > librime/src/rime/build_config.h

g++ -std=c++17 -O2 \
  -I librime/src -I librime/include -I librime-predict/src -I /ucrt64/include \
  librime-predict/tools/build_predict.cc librime-predict/src/predict_db.cc \
  librime/src/rime/dict/mapped_file.cc librime/src/rime/dict/string_table.cc \
  -L /ucrt64/lib -lmarisa -o build_predict.exe
```

> 只编译了 `build_predict` 真正用到的两个 librime 源文件（`mapped_file.cc`、`string_table.cc`），
> 关闭日志后唯一的链接依赖是 marisa。运行时需要 `ucrt64\bin` 在 `PATH`
> （`libmarisa`、`libstdc++`、`libgcc` 等 DLL）。

## CI

[`.github/workflows/predict.yml`](../../../.github/workflows/predict.yml) 在 Linux 上按上面
「Linux」流程编译 `build_predict`，生成 `predict.db`，上传为构建产物；官方仓库还会发布到
`predict` tag 的 Release。可在 Actions 页面手动触发（workflow_dispatch）。

## 备选：librime-predict-leveldb（按上屏历史学习）

[librime-predict-leveldb](https://github.com/fxliang/librime-predict-leveldb) 是 fxliang 基于
`rime/librime-predict` 的改版，用 LevelDB 用户库 `predict.userdb` 取代静态 `predict.db`，
能持续记录你**连续上屏的词**并自我加权（部署、配置见
[`others/docs/Prediction.md`](../../docs/Prediction.md) 第七节）。

本目录生成的 `predict.txt`（3 列 `key<TAB>text<TAB>weight`）可直接作为它的**预热语料**，
用插件随附的数据工具导入用户库：

```bash
python gen_predict_data.py -o predict.txt   # 或直接用 dist/predict.txt
# C++ 工具（随插件编译产物）：
predict_data_tool --from txt --to leveldb --input predict.txt --output predict.userdb
# 或 Python 工具（需 pip install plyvel）：
python3 scripts/predict_data_tool.py --from txt --to leveldb --input predict.txt --output predict.userdb
```
