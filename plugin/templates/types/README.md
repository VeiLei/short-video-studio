# 类型模板

视频类型模板，供 `/video-init` skill 在 init 阶段套用。

| 文件 | 类型 | 核心钩子 | 适合场景 |
|---|---|---|---|
| `knowledge.md` | 知识科普 | 悬念 / 反常识 / 数字 | 概念讲解、原理普及 |
| `marketing.md` | 营销种草 | 强冲击 / 痛点 / 价格 | 产品测评、带货 |
| `story.md` | 故事段子 | 场景 / 悬念 / 冲突 | 反转故事、vlog |

新类型按相同格式添加。`/video-init` 会用 `AskUserQuestion` 让用户选类型。
