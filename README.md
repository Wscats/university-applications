# ☯️ Fortune Master Ultimate · 命理大师

> 全体系命理顾问——排盘、占卜、风水、运程、择时，一站式解读。

---

## 🔮 简介

一个全体系命理 Skill，融合八字/四柱、紫微斗数、奇门遁甲、六爻、梅花易数、塔罗、西方星盘、
数字命理、九宫飞星风水、择时择吉于一体。支持用户注册与档案管理、每日运程推送、
交互式六爻占卜界面、九宫飞星计算脚本、HTML 报告生成。

| 体系 | 能力 |
|------|------|
| 八字 / 四柱 | 终身命格、流年大运 |
| 紫微斗数 | 命宫十二宫、四化飞星 |
| 奇门遁甲 | 择时、方位、事项推进 |
| 六爻占卜 | 是非判断、事态成败 |
| 梅花易数 | 快速起象、当下气机 |
| 塔罗牌 | 感情/事业/选择题 |
| 西方星盘 | 人格、关系合盘 |
| 数字命理 | 生命灵数、人生课题 |
| 九宫飞星 | 方位吉凶、空间布局 |
| 风水择吉 | 开业、搬迁、沟通窗口 |

---

## 🚀 快速开始

### 环境要求

- Node.js ≥ 18
- Python 3（九宫飞星脚本）

### 安装

```bash
npm install
```

### 使用示例

```bash
# 八字排盘
node scripts/bazi-analysis.js 1990-05-15 14:30

# 紫微斗数
node scripts/ziwei.js 1990-05-15 男

# 九宫飞星
python3 scripts/feixing.py today

# 六爻起卦
node scripts/liuyao.js 010203 "事业如何"

# 梅花易数
node scripts/meihua.js 3 5 2

# 今日运势
node scripts/daily-fortune.js
```

### 六爻交互界面

用浏览器打开 `liuyao/index.html`，古风水墨界面，支持摇卦与流式解卦。

> ℹ️ 默认完全离线，使用系统楷体。如需 Google Fonts 书法字体，可手动取消 HTML 中的注释（会产生外部网络请求）。
> 解卦功能需用户自行配置大模型 API Key 和接口地址，本 Skill 不内置任何 API 密钥。

---

## 🔒 安全说明

### 无外部网络调用

本 Skill 的所有脚本（包括推送脚本和发布脚本）**不包含任何外部网络调用**。
已验证所有 JS/Python 脚本中不存在 `fetch`、`axios`、`https.request`、`http.request`、
`curl`、`wget` 等网络请求代码。

> ℹ️ **关于六爻 HTML UI**：`liuyao/index.html` 中的 Google Fonts 外部链接已被注释，默认使用系统本地楷体，完全离线。
> 解卦功能中的大模型 API 接口地址为用户可配置项（默认值 `https://api.openai.com/v1`），本 Skill 不内置任何 API Key。

### 推送机制

每日运程推送功能通过 **OpenClaw 运行时 IPC 协议** 实现，而非直接调用第三方 API：

- `daily-push.js`：生成运程内容后通过 `console.log()` 输出，由 OpenClaw cron 运行时负责投递
- `push-toggle.js`：通过 `__OPENCLAW_CRON_ADD__` / `__OPENCLAW_CRON_RM__` IPC 消息管理定时任务
- 用户档案中的 `channels` 字段（如 `telegram`）仅作为 OpenClaw 运行时的路由标识，**本 Skill 不直接持有或使用任何第三方 API Token**

### 发布脚本

`scripts/publish.sh` 是一个本地版本管理工具，功能包括：
- 更新 `_meta.json`、`package.json`、`SKILL.md` 中的版本号
- 生成 `.publish-manifest.json` 文件清单
- 执行本地 git commit 和 tag
- **不执行任何远程上传或网络操作**

### 凭证要求

| 环境变量 | 必需 | 说明 |
|---------|------|------|
| `OPENCLAW_KNOWLEDGE_DIR` | 否 | 可选，紫微斗数知识库路径 |

本 Skill 不需要任何第三方 API Token（Telegram Bot Token、SMTP 密码等）。
所有消息投递由 OpenClaw 平台运行时统一管理。

---

## 📁 项目结构

```
├── SKILL.md                  # Skill 完整定义（ClawHub 格式）
├── _meta.json                # Registry 元数据（slug + version）
├── package.json              # Node.js 依赖与脚本入口
├── references/               # 各体系解释框架与规则
│   ├── bazi-framework.md
│   ├── ziwei-framework.md
│   ├── qimen-framework.md
│   ├── tarot-framework.md
│   ├── astrology-framework.md
│   ├── numerology-framework.md
│   ├── yijing-divination-framework.md
│   ├── fengshui-and-timing-framework.md
│   ├── relationship-and-timing.md
│   ├── dao-mysticism-framework.md
│   ├── qimen-calculation-rules.md
│   ├── qimen-interpretation-guide.md
│   ├── chinese-methods.md
│   ├── western-methods.md
│   ├── preparation.md
│   ├── output-templates.md
│   ├── intake-and-routing.md
│   └── safety-and-ethics.md
├── scripts/                  # 计算与排盘脚本（纯本地计算，无网络调用）
│   ├── bazi-analysis.js      # 八字排盘分析
│   ├── ziwei.js              # 紫微斗数排盘
│   ├── qimen.js              # 奇门遁甲排盘
│   ├── liuyao.js             # 六爻起卦
│   ├── meihua.js             # 梅花易数
│   ├── feixing.py            # 九宫飞星（Python）
│   ├── fengshui.js           # 风水分析
│   ├── daily-fortune.js      # 每日运势生成
│   ├── daily-push.js         # 推送调度（stdout → OpenClaw 运行时）
│   ├── push-toggle.js        # 推送开关（IPC → OpenClaw cron）
│   ├── marriage.js           # 合婚分析
│   ├── register.js           # 用户注册
│   ├── profile.js            # 档案管理
│   ├── preference-tracker.js # 偏好追踪
│   ├── jieqi.js              # 节气计算
│   ├── zhuanshi.js           # 择时择吉
│   └── publish.sh            # 本地版本发布（无网络操作）
├── liuyao/                   # 六爻交互界面（HTML）
├── data/                     # 用户档案与推送日志（本地存储）
│   ├── profiles/             # 用户 JSON 档案
│   └── push-log.json         # 推送执行日志
└── package.json
```

---

## ⚠️ 免责声明

命理是参考，不是定数。本工具不替代医疗、法律、财务或任何专业判断。

---

> *"读万卷书不如行万里路，行万里路不如高人指路，高人指路不如自己起一卦。"*

---