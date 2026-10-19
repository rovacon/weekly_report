# OrderPin 数字员工周报

提供给 OrderPin 同事的 AI 周报 skill。数字员工根据本人授权的工作记录整理周报，并通过 DWS CLI 提交钉钉日志，减少手工填报。

当前仅支持周报。优秀数字员工奖申请后续再开放，不会因安装或运行本 skill 自动申请奖项。

## 1. 安装 DWS

DWS 是钉钉官方开源的命令行工具。安装来源：[DingTalk Workspace CLI](https://github.com/DingTalk-Real-AI/dingtalk-workspace-cli#installation)。

macOS / Linux：

```bash
curl -fsSL https://raw.githubusercontent.com/DingTalk-Real-AI/dingtalk-workspace-cli/main/scripts/install.sh | sh
dws version
dws auth login
```

已安装 Node.js 的同事也可以使用官方 npm 包：

```bash
npm install -g dingtalk-workspace-cli
dws version
dws auth login
```

按浏览器提示登录自己的钉钉账号，选择工作组织并授权。企业尚未开放 CLI 时，需要管理员开通。SSH / 无浏览器环境使用 `dws auth login --device`；国际版钉钉登录使用 `--intl`。

本仓库的安装和更新脚本使用 Bash、Git，适用于 macOS / Linux，以及在 WSL 内运行 Agent 的 Windows 用户。Windows 原生 DWS 安装方法见官方文档；本仓库暂未提供 PowerShell 安装脚本。WSL 的 Git、DWS、Agent 和登录应在同一环境配置。

## 2. 安装周报 skill

需要先安装 Git。将仓库克隆到固定目录，安装后不要删除这个目录：

```bash
git clone https://github.com/rovacon/weekly_report.git "$HOME/.local/share/orderpin-weekly-report"
bash "$HOME/.local/share/orderpin-weekly-report/scripts/install.sh"
```

默认在 `~/.agents/skills/orderpin-weekly-report` 建立链接，源文件仍由这个 Git 仓库管理。支持共享技能目录的 Agent 可直接发现；重新打开 Agent 会话后调用 `$orderpin-weekly-report`。

如果 Agent 只识别自己的 skills 目录，用同一源目录安装到对应位置，避免同一 Agent 同时发现两份：

```bash
# Codex 独立技能目录
bash "$HOME/.local/share/orderpin-weekly-report/scripts/install.sh" --target "$HOME/.codex/skills"

# Claude Code 独立技能目录
bash "$HOME/.local/share/orderpin-weekly-report/scripts/install.sh" --target "$HOME/.claude/skills"
```

安装器遇到同名其他文件或技能时会停止，不覆盖。可让 Agent 完成安装，并读取仓库里的 `skills/orderpin-weekly-report/SKILL.md`。不支持 skill 的工具也可以让 Agent 直接读取该文件，但仍需先执行下面的更新步骤。

## 3. 每次先更新 再运行

```bash
bash "$HOME/.local/share/orderpin-weekly-report/skills/orderpin-weekly-report/scripts/update.sh"
```

更新成功后，让 Agent **重新读取更新后的 SKILL.md**，再生成或提交周报。只执行 `git pull` 而继续使用上下文里的旧规则不算完成更新。skill 本身也要求检查本次更新结果，避免遗漏。

可以直接向 Agent 发送：

> 先执行 `~/.local/share/orderpin-weekly-report/skills/orderpin-weekly-report/scripts/update.sh`，更新成功后重新读取最新的 `$orderpin-weekly-report`。根据我授权的 OrderPin 工作记录整理上周周报，先展示钉钉最终四栏内容，不提交。

确认预览后发送：

> 按刚才的预览提交周报，收件人为我本人。

首次提交给其他人时，明确收件人姓名，Agent 会通过 DWS 解析账号；有同名时需确认。不会默认发给仓库作者或某位主管。可一次说明“生成并直接提交，收件人为……”，无需每次多轮确认。

更新器仅接受本仓库 `origin` 的 `main` 分支，并只做快进更新。有本地修改、本地提交、分叉或网络错误时会停止；不会 reset、stash 或强推，也不会静默继续旧版。请先保留并处理本地修改，不要直接删除文件。

### DWS 自身的升级

周报规则更新与 DWS 软件升级是两件事。每周运行只自动更新本仓库，不自动升级员工电脑上的 DWS。

```bash
dws upgrade --check
# 官方独立二进制安装：
dws upgrade
# npm 安装：
npm install -g dingtalk-workspace-cli
```

其他安装方式按官方说明升级。遇到命令或字段变化，先核对当前 DWS schema，必要时再升级。升级后重新验证自己的登录和命令，不复制他人的登录凭据。

## 4. 每周五自动上报

本仓库不创建定时任务。完成首次预览和试提交后，在自己已有的 Agent 中配置每周五下班前运行的任务；具体时间、时区由本人确定，电脑或执行环境需要支持定时运行及 DWS 登录。

定时任务应保存本人明确授权的工作记录范围、钉钉组织账号、周报模板和收件人，不能把凭据放进提示词。可以采用以下提示词，再替换方括号中的个人配置：

```text
每周五下班前执行我的 OrderPin 工作周报任务。
1. 先运行 [仓库绝对路径]/skills/orderpin-weekly-report/scripts/update.sh。
2. 成功后重新读取 [仓库绝对路径]/skills/orderpin-weekly-report/SKILL.md。
3. 仅使用我授权的 [OrderPin 工作目录及工作会话来源]，汇总本周一至本次执行时刻的工作。
4. 使用我明确指定的 [钉钉组织账号] 和 [周报模板]，按最新 skill 生成最终四栏内容。
5. 我授权本定时任务将该周期周报自动提交给 [已确认的收件人]，无需逐次确认。
6. 提交前检查同周期回执和发件箱，避免重复提交；提交后回查并保存回执。
7. 更新失败、记录来源未授权、账号/收件人不明确或提交状态不确定时，停止并提醒我。
8. 不读取私人内容，不发起奖项申请。
```

Agent 不具备某项记录的读取能力时，不会假装已覆盖。不要为了周报授权整个个人目录或全部聊天。定时提交无需人工逐次确认，但员工发现事实错误时应及时更正。

## 5. 周报格式和隐私

- 内容主要为 OrderPin 工作，覆盖任务、交付、业务效果、问题及下一步。
- 主工作栏保留预览中的三列表格，区分产出与验证边界；其余内容按钉钉实际四栏组织，提交前后不擅自改写。
- 不编造节省工时、成本和上线结果；文档、原型、构建、测试、实机及上线证据分别表述。
- 仅读取本人授权的工作记录，不上报完整 AI 对话、私人会话、个人文件及个人隐私；客户或同事敏感信息脱敏，凭据不进入周报。
- CLI 回读只能证明正文已保存，不能证明钉钉客户端表格排版。若客户端显示异常，先查已有记录，不自动再创建一篇。

本仓库是公开仓库。真实周报、收件人配置、提交回执等只保存在本机，例如仓库 `.local/` 目录；不要提交到 Git。后续奖项申请会单独维护，仍坚持员工主动申请、AI 协助填报，不包含既定项目任务本身。

## 维护与验证

维护者修改 `skills/orderpin-weekly-report/` 后提交到 `main`，员工下次运行前自动更新即可。不要在每个人的安装目录里独立修改规则。

```bash
python3 -m unittest discover -s tests -v
git diff --check
```
