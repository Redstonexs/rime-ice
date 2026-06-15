# 输入预测部署教程（Windows / Android）

雾凇拼音的简体中文**输入预测**：当输入区为空时，根据你**上一个上屏的词**，预测可能的
后续文字，直接选用而无需再输入。基于 [librime-predict](https://github.com/rime/librime-predict)。

> 官方随 librime-predict 提供的 `predict.db` 是**繁体**的。本仓库提供的是从雾凇词库生成的
> **简体** `predict.db`，预测项按词频排序，例如：
> `北京 → 市 / 大学 / 时间`，`苹果 → 电脑 / 公司`，`谢谢 → 合作 / 大家`。

> 进阶：想让预测**按你自己的上屏历史学习、越用越准**，可改用 fxliang 的
> [librime-predict-leveldb](https://github.com/fxliang/librime-predict-leveldb)，
> 把「上一个词 → 下一个词」的搭配记进个人词库，见下文 **第七节**。

效果示意：上屏「中华」后，候选区出现「人民共和国 / 民族 / 民国 …」可直接选用。

---

## 一、前置条件：前端要内置 predict 插件

输入预测需要前端所用的 **librime 编译时带了 `librime-predict` 插件**（librime ≥ 1.11）。
否则部署时会出现 `predictor` / `predict_translator` 组件找不到的错误日志，预测也不会生效。

| 平台 | 前端 | 说明 |
| --- | --- | --- |
| Windows | 小狼毫 **Weasel** | 建议 **0.16.0 及以上**（已内置 64 位、较新的 librime） |
| Android | **fcitx5-android**（Rime 插件） | 较新版本已内置 predict 插件，推荐 |
| Android | **同文 Trime** | 较新版本已内置 predict 插件 |

**如何确认是否支持**：完成下面的部署后，若重新部署成功、`F4`/方案菜单里出现「预测」开关，
且上屏一个词后候选区给出预测，即说明支持；若部署日志报组件相关错误或毫无预测，多半是
前端的 librime 太旧，升级前端即可。

---

## 二、需要的两个文件

1. **`predict.db`**：简体预测库。获取方式（任选其一）：
   - 从本仓库 Actions/Release 的 `predict` 资源下载；
   - 自行构建（见 [`others/script/predict/README.md`](../script/predict/README.md)），产物在 `dist/predict.db`。
2. **`rime_ice.custom.yaml`**：启用预测的补丁，模板见
   [`others/patch_examples/rime_ice.custom.yaml`](../patch_examples/rime_ice.custom.yaml)。

补丁核心内容（若你已有 `rime_ice.custom.yaml`，把 `patch:` 下的条目合并进去即可）：

```yaml
patch:
  "engine/processors/@after 0": predictor
  "engine/translators/@before 0": predict_translator
  "switches/+":
    - name: prediction
      states: [ 关闭预测, 开启预测 ]
      reset: 1            # 部署后默认开启；删掉此行则默认关闭
  predictor:
    db: predict.db
    max_candidates: 5
    max_iterations: 2
```

> **双拼用户**：补丁要打到你正在用的方案上。例如新建 `double_pinyin_flypy.custom.yaml`，
> 内容与上面 `patch:` 部分相同（其他双拼方案同理）。

---

## 三、Windows · 小狼毫 Weasel

1. 打开 Weasel 的**用户文件夹**：右键托盘小狼毫图标 →「用户文件夹」（通常是
   `%APPDATA%\Rime`，即 `C:\Users\你的用户名\AppData\Roaming\Rime`）。
2. 把 **`predict.db`** 复制进该文件夹（与 `rime_ice.schema.yaml` 等放在一起）。
3. 把 **`rime_ice.custom.yaml`** 复制进同一文件夹（已有则合并）。
4. 右键托盘图标 →「**重新部署**」。
5. 用 `Ctrl+grave`（`` ` ``）或 `F4` 打开方案菜单，确认「预测」开关已开启。

桌面端体验：上屏一个词、输入区为空时，候选区会给出预测项；用数字键或空格选用，
按 `Esc` / `退格` 可消除当前预测。

---

## 四、Android

> 通用思路：把 `predict.db` 和 `rime_ice.custom.yaml` 放进对应 App 的 **Rime 用户目录**
> （和雾凇拼音其余文件在一起），然后在 App 内**重新部署**。

### 4.1 fcitx5-android（Rime 插件）

1. 安装 **Fcitx5 for Android** 及其 **Rime 插件**，并已导入雾凇拼音。
2. 进入 App →「输入法」/「插件」中的 **Rime** → 找到「**用户数据目录**」（可在应用内
   定位或导入文件）。
3. 把 `predict.db` 和 `rime_ice.custom.yaml` 放进该目录（与雾凇其他文件同级）。
4. 回到 Rime →「**重新部署**」。
5. 在键盘上通过方案/开关菜单确认「预测」已开启。

### 4.2 同文 Trime

1. 安装 **同文 Trime**，并已部署雾凇拼音。Trime 默认用户目录为
   `/storage/emulated/0/rime`（即内部存储根目录下的 `rime` 文件夹）。
2. 用文件管理器把 `predict.db` 和 `rime_ice.custom.yaml` 复制进 `rime/` 目录。
3. 打开 Trime → 菜单 →「**重新部署**」（部署完成提示成功）。
4. 在工具栏/长按回车的菜单里确认「预测」开关已开启。

手机端体验：预测对移动输入帮助更明显——上屏一个词后，候选区直接给出后续词，
点选即可；可配合 `max_iterations` 连续预测。

---

## 五、使用与注意事项

- **触发方式**：输入区为空、且上一个上屏的是普通词（非标点/数字/西文）时才预测。
- **数字键习惯**：若你习惯直接敲数字，可能会误把预测候选上屏。可调小
  `max_candidates`，或不需要时用「预测」开关临时关闭。
- **默认开关**：把补丁里的 `reset: 1` 删掉即可改为「部署后默认关闭」，仍可在菜单手动开启。
- **繁简**：本库为简体；开启简繁切换时，预测候选不会被转换（这是 predict 的已知限制）。
- **关闭/卸载**：在菜单关闭「预测」开关即可停用；或从用户文件夹删除 `rime_ice.custom.yaml`
  里的预测相关条目并重新部署，`predict.db` 可一并删除。

---

## 六、自定义 / 重建 predict.db

预测数据来自 `cn_dicts/`，可自行调参（候选数量、前缀长度、过滤低频等）后重建。
完整说明见 [`others/script/predict/README.md`](../script/predict/README.md)：

```bash
# 1) 生成预测数据（纯 Python）
python others/script/predict/gen_predict_data.py -o dist/predict.txt
# 2) 用 build_predict 编译为 predict.db（build_predict 的获取见上面的 README）
BUILD_PREDICT=/path/to/build_predict bash others/script/predict/build.sh
```

---

## 七、进阶：按你的上屏历史学习预测（librime-predict-leveldb）

上面的 `predict.db` 是**静态词库**预测：内容固定，不随你的使用变化。如果希望预测能
**根据你自己上屏的历史**自我学习、越用越准，可改用 fxliang 的
[**librime-predict-leveldb**](https://github.com/fxliang/librime-predict-leveldb)
（基于 `rime/librime-predict` 的改版）。

它把你**连续上屏的词**记录到 LevelDB 用户库 `predict.userdb`：「上一个词 → 下一个词」
的搭配会被持续记录、加权，预测因此逐渐贴合你的个人用法。两次上屏间隔过久（默认 30 秒）
则不建立关联，避免把不相关的输入串到一起。

> ⚠️ **这是另一个插件。** 它和上面用的 `rime/librime-predict` 是两套实现，组件名相同
> （`predictor` / `predict_translator`），**不能同时启用**。要用它，前端的 librime 必须在
> **编译时带上 librime-predict-leveldb**——目前各发行版自带的通常是原版 librime-predict，
> 并没有它。需自行把它作为 librime 插件编译，或使用已内置它的前端 / Weasel 构建。

### 7.1 配置补丁

把 `rime_ice.custom.yaml` 里的 `predictor` 块换成下面这套（处理器挂载、开关与第二节相同）：

```yaml
patch:
  "engine/processors/@after 0": predictor
  "engine/translators/@before 0": predict_translator
  "switches/+":
    - name: prediction
      states: [ 关闭预测, 开启预测 ]
      reset: 1            # 部署后默认开启；删掉此行则默认关闭
  predictor:
    predictdb: predict.userdb            # LevelDB 用户库（首次部署自动创建于用户目录）
    max_candidates: 5                    # 每次最多显示的预测候选数
    max_iterations: 1                    # 连续预测次数；0 表示不限制
    max_commit_interval_seconds: 30      # 两次上屏间隔超过该秒数则不建立关联
    legacy_mode: false                   # false=学习模式(leveldb)；true=退回原版、改读下面的 db
    db: predict.db                       # 仅 legacy_mode: true 时使用
```

- **空库起步**：`predict.userdb` 不存在时会自动创建，从零开始学——刚装时没有预测，随使用
  逐渐出现。
- **用词库预热（推荐）**：先把本仓库词库生成的 `predict.txt` 灌进用户库，开局即有静态预测，
  之后再叠加你的历史（见 7.3）。
- **沿用旧库**：若只想用原来的静态 `predict.db`、不想学习，设 `legacy_mode: true` 即可，
  配置与第二节等价。

### 7.2 部署

与第三 / 四节完全一样：把（用 7.1 内容的）`rime_ice.custom.yaml` 放进 Rime 用户文件夹并
**重新部署**。`predict.userdb` 会在用户目录自动生成，**无需手动放入 `predict.db`**
（除非 `legacy_mode: true`）。开关、触发方式、注意事项均同上。双拼用户照样把补丁打到自己
正在用的方案上。

### 7.3 用词库预热用户库 / 导入导出

插件随附数据工具，可在 LevelDB 用户库与文本之间互转。文本为制表符分隔：
`prefix<TAB>word<TAB>weight`（可扩展为 `…<TAB>commits<TAB>dee<TAB>tick`）。

```bash
# 1) 用本仓库词库生成预热数据（纯 Python，无依赖）
python others/script/predict/gen_predict_data.py -o predict.txt

# 2) 文本 → LevelDB 用户库（任选其一）
#   A) C++ 工具（随插件一起编译的产物）
predict_data_tool --from txt --to leveldb --input predict.txt --output predict.userdb
#   B) Python 工具（需 pip install plyvel）
python3 scripts/predict_data_tool.py --from txt --to leveldb --input predict.txt --output predict.userdb

# 备份 / 检查：用户库 → 文本
predict_data_tool --from leveldb --to txt --input predict.userdb --output predict.txt
```

把生成的 `predict.userdb` 放进用户文件夹（配合 `legacy_mode: false`），即可
「带着词库知识开局、再随上屏历史持续学习」。
