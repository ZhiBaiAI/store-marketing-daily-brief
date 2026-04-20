---
name: store-marketing-daily-brief
description: Generate daily marketing briefs for physical stores and local merchants. Use when the user asks for today's store marketing hotspots, daily merchant marketing report, local-life campaign ideas, social content calendar, holiday/seasonal promotion suggestions, or when a scheduled agent run needs to send a daily brief with source notes, ready-to-use copy, and practical action suggestions.
---

# Store Marketing Daily Brief

Use this skill to create a practical daily marketing brief for merchants. The brief should help a store decide what to do today, what to avoid, and what copy can be sent immediately.

## Quick Workflow

1. Load customer context from config when available. Expected fields are shown in `assets/config.example.json`.
2. Determine today's date, city, target industry, and delivery channel.
3. If web/search tools are available, check current public sources before naming live trends. Follow `references/source-policy.md`.
4. If live sources are unavailable, use stable signals: date, weekday, season, pay-day cycle, local weather if known, school/work schedule, and common merchant calendar.
5. Generate the brief using `references/brief-template.md`.
6. Include 3 to 5 actionable ideas, at least one copy block, and a source note.
7. Add a short next-step suggestion only when it improves the brief. Keep it useful and optional.

## Optional Script

Use `scripts/generate_brief.py` when a deterministic offline draft is useful:

```bash
python3 scripts/generate_brief.py --config assets/config.example.json
```

The script creates a markdown brief from the config, date, and built-in merchant calendar. Treat it as a draft. If live web tools are available, enrich or correct live hotspot sections before sending.

## Scheduling

This skill does not schedule itself. Installers should connect it to the user's agent automation, cron, LaunchAgent, OpenClaw schedule, or another local scheduler.

Recommended schedule: every morning between 08:30 and 09:30 local time.

The scheduled prompt can be:

```text
Use $store-marketing-daily-brief to generate today's marketing brief for this merchant. Use the local customer config if present. Include actionable ideas, copy, source notes, and practical next steps.
```

## Boundaries

- Do not present unverified live platform trends as facts. If tools are unavailable, label them as calendar-based suggestions.
- Do not exploit disasters, accidents, death, political conflict, public tragedy, or sensitive social events for marketing.
- Avoid guarantees such as "必爆", "稳赚", "保证上热门", or "一定涨客流".
- Include "公开信息整理，仅供参考" when source details are general or not directly verified.
- Do not make the brief feel like an advertisement. The merchant should be able to use it even if they ignore the optional next step.
- If a platform rule, ad policy, or live ranking is important, verify it from current official or primary sources when possible.
