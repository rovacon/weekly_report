# 使用 DWS 提交日志周报

使用 `dws report`，不是 OA 审批、文档或群消息。下面是已验证过的命令路径；实际参数或安全要求不明确时，仅查询对应 leaf 的 schema。命令变化先核对当前 schema/精确 leaf help，必要时按官方方式升级 DWS，不连续猜命令。

## 账号 收件人与模板

多账号时使用本人指定的稳定 profile（`corpId:userId`），或唯一明确的当前账号；不选列表第一项。后续读取、人员解析、写入及回查使用同一 profile。可先用 `dws profile list --format json` 查看身份，必要时询问。

```bash
# 核对报告作者身份；正式收件人另行解析为骆华根
dws contact +me --format json

# 唯一定位模板；不把销售周报当作普通周报
dws report +template-search --query 周报 --format json
dws report template get --name 周报 --format json

# 提交参数与门禁不明确时查精确 schema
dws schema --cli-path 'report entry submit' --compact -f json
```

正式收件人用 `dws aisearch person --query '骆华根' --dimension name --format json` 解析 userId，并核对当前工作组织及姓名。重名或查无结果时先消歧；不将姓名直接传给 `--to-user-ids`，不使用其他组织或历史示例 ID，不自动抄送。仅在当次明确要求试发给本人时使用当前作者 userId，并标记试发。

## 检查重复

```bash
dws report +outbox-list --start '<提交窗口起始ISO时间>' --end '<结束ISO时间>' --template-name '周报' --cursor 0 --size 20 --format json
```

时间用带时区 ISO-8601，每个窗口最多20天，按真实游标翻页；从返回的稳定 reportId 按需读取正文，确认报告覆盖周期和身份。分页未知或查询失败时不能声称“没有重复”。用户明确要求再次提交时，告知旧记录保留，不自行删除。

## 锁定请求并提交一次

`contents` 是 JSON 数组，字段名、排序和 type 取自实时模板。文本正文采用 `contentType: "markdown"`。如下仅示意一项，不是完整模板，更不能把这条示例发送到钉钉：

```json
[
  {
    "key": "本周完成工作",
    "sort": "0",
    "contentType": "markdown",
    "type": "1",
    "content": "## OrderPin 工作周报\n周期：实际报告周期\n\n| 工作事项 | 产出与进展 | 验证边界 |\n|---|---|---|\n| 实际事项 | 有证据的进展 | 尚未验证的范围 |"
  }
]
```

从模板取得的其他字段也一并构造。准备用户看到的最终预览后，不再次改写正文。JSON 文件必须在本次命令工作目录内，用相对路径传入，例如 `.local/weekly-report.json`；不要放在公开的已跟踪目录，不打印凭据。

```bash
dws report entry submit --template-id '<实时模板ID>' --contents-file ./.local/weekly-report.json --to-user-ids '<已解析的收件人ID>' --format json
```

普通创建按 live schema 不需额外确认 flag；用户已授权时直接执行。若 runtime 要求确认，以实际门禁为准处理，不以静默添加 `--yes` 绕过。除非用户另有要求，不加 `--to-chat`，不另外转发聊天。

## 最小回查与故障恢复

```bash
dws report entry get --report-id '<提交返回的reportId>' --format json
```

必须同时具有成功状态、稳定 reportId，以及读回的正确模板和字段正文。读回成功也不能推断收件人已阅读或客户端渲染正常。保存服务端返回的打开链接，不自行拼造。

超时、断连、未知响应或写后回查失败时不重复创建。先用同一 profile、精确提交窗口查询发件箱并核对正文。只有明确证明请求未写入且用户仍授权，才可再次提交；无法确认则报告状态不确定及已有回执。

缺权限或未登录时停止提交，让本人完成 `dws auth login` 或管理员授权。不要向员工索要 token，不把其他人的登录状态复制过去。
