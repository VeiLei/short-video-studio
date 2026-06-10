---
name: video-visual
description: 生成所有视觉资产 + 视频片段。调用后端 CLI 生成四视图/全景/取景框/视频。
allowed-tools: Read Write Bash
---

生成视觉素材。四个阶段，按需触发。流程对齐 short-drama-writer 的 drama-generate。

## 前置条件

- 当前工作目录是项目根目录（含 `.video/state.json`），以下用 `<PROJECT>` 代指
- `.video/state.json` phase ∈ {write, review, visual}
- `台本/视频提示词.json` 存在且已通过 schema 校验
- 后端 `.env` 已配置即梦 API Key + ARK API Key
- 以下用 `CLI` 代指后端 CLI 入口。**按顺序查找**：

  ```
  1. cd d:/PersonalFiles/Project_Space/short-drama-writer/backend && .venv/Scripts/python -m app.cli  ← 本地开发后端（优先）
  2. unix: cd ${CLAUDE_PLUGIN_ROOT}/../short-drama-writer/backend && .venv/bin/python -m app.cli
  3. win:  cd ${CLAUDE_PLUGIN_ROOT}/../short-drama-writer/backend && .venv/Scripts/python -m app.cli
  ```

  路径 1 的 .venv 存在则直接用；不存在则依次尝试 2/3。均不存在时报错。

---

## 素材生成时序

```
阶段1：角色基础四视图 + 场景全景图
阶段2：按需取景框 + 变装四视图 + 道具参考图
阶段3：逐 shot 生成视频
阶段4：查询素材索引 + 写失败记录
```

---

## 阶段1：角色基础四视图 + 场景全景图

**时机**：video-write 完成、视频提示词 JSON 就绪后。

### 1a. 扫描缺失资产

读 `<PROJECT>/台本/视频提示词.json`，提取全部角色名（去重）、场景名（去重）、道具名（去重）。

读 `<PROJECT>/.drama/assets.json`（后端 CLI 写在这里），对比已有资产；如文件不存在则全量生成。

### 1b. 角色基础四视图（逐个角色，一次一个）

从 `<PROJECT>/设定/角色.md` 取角色的**不可变锚点块**（发型发色、脸型特征、标志配饰、体型身高、着装基底），原样拼入四视图 prompt：

```
CG游戏角色原画风格，半写实渲染，清晰轮廓线，平涂上色，游戏角色设定图质感，非真人照片。
纯白背景。
四视图组合：左侧（版面的三分之一）为角色面部特写（胸部以上），
右侧（版面的三分之二）依次为正面全身、侧面全身、背面全身，
全身照要见到鞋，三视图严格对齐、间距均匀，无重叠。
角色外观锚点：{发型发色}，{脸型特征}，{标志配饰}，{体型身高}，{着装基底}。
保持CG游戏角色原画质感，非真人。
```

> **锚点锁定**：锚点词从设定/角色.md 原样复制，不增不减。这些词后续视频生成阶段会作为 reference 的视觉锚点。

调用（逐个角色执行，一次一个）：

```bash
CLI four-views --project <PROJECT> --name <角色名> --prompt "..."
```

CLI 自动记入 `<PROJECT>/.drama/assets.json`，outfit="基础"。

### 1c. 场景全景图（逐个场景，一次一个）

从 `<PROJECT>/设定/场景.md` 取空间描述、关键地标、光线色调、氛围基调。

```
{场景类型}，{关键地标}，{空间尺寸}。
{氛围基调}，{色调/光照方向}。空镜，无人物。
竖屏9:16构图，展示场景全貌。
```

调用：

```bash
CLI scene-master --project <PROJECT> --name <场景名> --prompt "..."
```

---

## 阶段2：按需取景框 + 变装 + 道具

### 2a. 缺失取景框

对每个 shot 指定的 frame_type + scene，检查 `.drama/assets.json` 中是否已有对应 shot_frame，缺失的调用：

```bash
CLI shot-frame --project <PROJECT> --scene <场景名> --frame-id <frame_id> --frame-type <type> --prompt "..."
```

取景框 = 空镜无人。CLI 自动以场景 master 图为 reference_image。

### 2b. 缺失变装四视图

如果某 shot 的 `outfits` 字段有非"基础"着装（如"休闲装"、"正装"），检查 `.drama/assets.json` 是否已有，缺失则调用：

```bash
CLI variant --project <PROJECT> --name <角色名> --outfit <着装名> --prompt "..."
```

CLI 自动以基础四视图为 reference_image，保持角色面容体型一致。

### 2c. 缺失道具参考图

对 `视频提示词.json` 中出现的每个道具，检查 `.drama/assets.json` 的 `props` 段，缺失则调用：

```
CG游戏原画风格，半写实渲染，{道具描述}。
纯白背景，无人物，正上方或侧45°产品图视角，展示全部细节。
```

```bash
CLI prop-ref --project <PROJECT> --name <道具名> --prompt "..." --scene <关联场景>
```

---

## 阶段3：逐 shot 生成视频

**注意**：`video-generate` CLI 的 `--episode` 参数用于定位视频提示词 JSON。短视频项目只有一个视频，约定 episode = `"0001"`，且提示词文件必须放在：

```
<PROJECT>/提示词/第0001集-视频提示词.json
```

因此在阶段 3 前，**必须先将** `<PROJECT>/台本/视频提示词.json` **复制到** `<PROJECT>/提示词/第0001集-视频提示词.json`：

```bash
mkdir -p <PROJECT>/提示词
cp <PROJECT>/台本/视频提示词.json <PROJECT>/提示词/第0001集-视频提示词.json
```

然后对每个 shot 调用（`--duration` 从视频提示词 JSON 的 `video_params.duration_sec` 读取，**不要写死**）：

```bash
CLI video-generate --project <PROJECT> --episode 0001 --shot-id <shot_id> --scene <场景名> --frame-id <frame_id>
```

> **MVP 阶段**：先不传 `--mode narration`。如果用户明确要"知识科普型"旁白视频，再加 `--mode narration`。

CLI 自动从 JSON 读取 duration/ratio/refs → submit → poll → download 到 `<PROJECT>/素材/视频/`。

---

## 阶段4：查询素材索引 + 失败记录

随时查看已有素材：

```bash
CLI assets --project <PROJECT>
```

如果某个 shot 生成失败（CLI 返回非零退出码），写到 `<PROJECT>/.video/voice_index.json`：

```json
{
  "failed_shots": [
    {
      "shot_id": "S07",
      "error": "Seedance content filter",
      "timestamp": "2026-06-09T12:30:00Z"
    }
  ]
}
```

video-review 在下轮会读这个。

---

## 阶段5：更新 state

```bash
cd d:/PersonalFiles/Project_Space/short-video-studio
.venv/Scripts/python -c "
import sys
sys.path.insert(0, 'plugin/scripts')
from state_manager import StateManager
StateManager('<PROJECT>').set_phase('visual')
"
```

## 错误处理

- **API key 错误**（401/403）→ 立即终止，提示用户检查 .env
- **Seedance 内容过滤** → 单 shot 重试一次，换同义词；再失败则标记 failed
- **限流（429）** → CLI 已有 submit_lock 串行化
- **轮询超时**（>30 分钟）→ 标记 timeout，跳过
- **TOS 上传失败** → 本地保留图片，tos_url 置空

## 关键约束

- 严格按"缺失才生成"原则 — 已有的资产不重发 API
- 角色四视图 = 角色+白底，没有场景背景
- 取景框 = 空镜，没有人
- 视频生成时取景框(TOS) + 角色(TOS) → Seedance
- 单 shot 失败不影响其他 shot
- 不在项目目录创建 .py 脚本
- prompt 超长用临时文件传入：`--prompt @/tmp/prompt.txt`
- CLI 用 `<PROJECT>` 绝对路径，不用相对路径
