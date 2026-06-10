---
name: video-visual
description: 生成所有视觉资产 + 视频片段。调用后端 CLI 生成角色参考图/场景/取景框/视频。
allowed-tools: Read Write Bash
---

生成视觉素材。流程基于 Seedance 2.0 官方文档最佳实践。

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
阶段1：角色参考图（大头照 + 全身照）+ 场景全景图
阶段2：按需取景框 + 变装 + 道具参考图
阶段3：逐 shot 生成视频
阶段4：查询素材索引 + 写失败记录
```

---

## 阶段1：角色参考图 + 场景全景图

**时机**：video-write 完成、视频提示词 JSON 就绪后。

### 1a. 扫描缺失资产

读 `<PROJECT>/台本/视频提示词.json`，提取全部角色名（去重）、场景名（去重）、道具名（去重）。

读 `<PROJECT>/.drama/assets.json`（后端 CLI 写在这里），对比已有资产；如文件不存在则全量生成。

### 1b. 角色参考图（逐个角色，一次一个）

> **官方警告**：不要使用角色多视图/三视图作为 Seedance 参考素材。多视图包含同一人物不同角度，模型易将其识别为多个不同主体，加剧 ID 漂移和"双胞胎问题"。

**正确做法**：每个角色生成两张独立图片——

**图1 — 大头照**（用于 Seedance 人脸锁定）：
```
CG游戏角色原画风格，半写实渲染，清晰轮廓线。
纯白背景，无表情最佳，仅保留面部，减少肩颈背景干扰。
角色面部特写（大头照）：{发型发色}，{脸型特征}，{标志配饰（面部可见部分）}。
非真人照片，保持CG游戏角色原画质感。
```

**图2 — 全身照**（用于 Seedance 着装+体型锁定）：
```
CG游戏角色原画风格，半写实渲染，清晰轮廓线。
纯白背景，正面全身站立，见到鞋。
角色外观：{发型发色}，{脸型特征}，{标志配饰}，{体型身高}，{着装基底}。
非真人照片，保持CG游戏角色原画质感。
```

调用（逐个角色、两张图分别执行）：

```bash
# 大头照
CLI four-views --project <PROJECT> --name "<角色名>_大头照" --prompt "..."
# 全身照
CLI four-views --project <PROJECT> --name "<角色名>_全身照" --prompt "..."
```

> CLI 自动记入 `.drama/assets.json`。大头照和全身照分别作为独立 reference 在阶段 3 视频生成时传入 Seedance。

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

### 2b. 缺失变装参考图

如果某 shot 的 `outfits` 字段有非"基础"着装（如"休闲装"、"正装"），生成该着装的全身照（同样不用多视图，只用正面全身）：

```bash
CLI variant --project <PROJECT> --name <角色名> --outfit <着装名> --prompt "..."
```

CLI 自动以基础全身照为 reference_image，保持角色面容体型一致。

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

### 3a. 素材配置策略（官方推荐 4-5 个素材）

每个 shot 调用 Seedance 时，参考素材按角色分组：
- **角色锚定**：大头照 1 张 + 全身照 1 张（锁定角色外观）
- **场景定调**：取景框 1 张 或 场景全景图 1 张（锁定环境与风格）
- 总计 3-4 张图，不用满素材上限

### 3b. 提示词位置

`video-generate` CLI 的 `--episode` 参数用于定位视频提示词 JSON。短视频项目约定 episode = `"0001"`：

```bash
mkdir -p <PROJECT>/提示词
cp <PROJECT>/台本/视频提示词.json <PROJECT>/提示词/第0001集-视频提示词.json
```

### 3c. 调用生成

对每个 shot 调用（`--duration` 从 JSON 的 `video_params.duration_sec` 读取，**不要写死**）：

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

- **不用多视图作为 Seedance 参考** — 大头照 + 全身照分开上传，避免 ID 漂移
- 严格按"缺失才生成"原则 — 已有资产不重发 API
- 角色参考图 = 角色+白底，没有场景背景
- 取景框 = 空镜，没有人
- 一个镜头只一种运镜方式
- 单 shot 失败不影响其他 shot
- 不在项目目录创建 .py 脚本
- prompt 超长用临时文件传入：`--prompt @/tmp/prompt.txt`
- CLI 用 `<PROJECT>` 绝对路径
