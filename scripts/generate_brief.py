#!/usr/bin/env python3
"""Generate an offline daily marketing brief for local merchants."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path


WEEKDAY_NAMES = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

FIXED_SIGNALS = {
    "01-01": "元旦",
    "02-14": "情人节",
    "03-08": "女神节",
    "03-15": "消费者权益日",
    "05-01": "劳动节",
    "05-20": "520",
    "06-01": "儿童节",
    "09-10": "教师节",
    "10-01": "国庆节",
    "11-11": "双11",
    "12-12": "双12",
    "12-24": "平安夜",
    "12-25": "圣诞节",
}

INDUSTRY_ACTIONS = {
    "餐饮": {
        "store": "推出今日限定双人/工作餐套餐，门口和社群同步露出。",
        "community": "在社群发起今天午餐或晚餐投票，给投票用户一个到店小礼。",
        "social": "发一条真实出餐短视频，标题突出附近、今天、限时。",
        "copy": "今天不想纠结吃什么，可以直接来店里点这份今日套餐，分量够、出餐快，适合附近上班和下班顺路吃。",
    },
    "美业": {
        "store": "设置今日空档体验名额，用低门槛单项服务带动预约。",
        "community": "发起老客带新客预约，双方都获得护理或小样权益。",
        "social": "发布一个真实案例前后对比，强调过程、时长和适合人群。",
        "copy": "今天有少量空档，适合想快速变精致但不想办卡的顾客，先体验一次，再决定是否继续。",
    },
    "教培": {
        "store": "开放今日测评名额，用诊断报告承接试听课。",
        "community": "给家长群发一个学习小测试，引导预约一对一分析。",
        "social": "发布一个常见学习问题拆解，结尾引导预约测评。",
        "copy": "先别急着报课，今天可以先做一次基础测评，看看问题具体卡在哪里，再决定后面怎么补。",
    },
    "健身": {
        "store": "开放下班后一小时体验课，降低第一次到店压力。",
        "community": "发起三天轻运动打卡，完成后送体测或体验课。",
        "social": "发布一个新手友好动作，强调不卷、可坚持。",
        "copy": "今天先不用练很猛，来做一次轻量体验，知道自己的身体状态，再开始更容易坚持。",
    },
    "零售": {
        "store": "做今日新品或组合陈列，把主推款放到入口动线。",
        "community": "给会员发今日到店专属款或组合价。",
        "social": "发布三件单品搭配或使用场景，减少选择成本。",
        "copy": "今天到店可以重点看这组新搭配，适合日常使用，也适合顺路给自己或家人添一件。",
    },
    "母婴": {
        "store": "按月龄整理今日推荐清单，并设置到店咨询时间。",
        "community": "发一个新手爸妈避坑小贴士，承接到店咨询。",
        "social": "发布一个真实育儿场景解决方案，避免夸大功效。",
        "copy": "今天整理了一份按月龄选购的小清单，新手爸妈可以先看需求，再决定买什么，少踩坑。",
    },
    "宠物": {
        "store": "推出今日美容/护理预约名额，附宠物照片服务。",
        "community": "邀请老客晒宠物照片，抽一个小护理权益。",
        "social": "发布一个宠物护理前后变化或到店花絮。",
        "copy": "今天还有少量护理预约，适合想让毛孩子舒服一点、顺便留张可爱照片的家长。",
    },
    "咖啡": {
        "store": "设置上午提神杯和下午第二杯优惠，覆盖通勤和办公场景。",
        "community": "在社群发布今日豆子/特调说明，限时预留。",
        "social": "发布一条出杯过程短视频，强调今天适合的口味。",
        "copy": "今天适合来一杯不费脑子的提神咖啡，上午赶路、下午办公都刚好。",
    },
}


def load_config(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def pick_industry(config: dict) -> str:
    profile = config.get("customer_profile", {})
    industry = profile.get("industry") or ""
    if industry:
        return industry
    industries = config.get("target_industries") or ["餐饮"]
    return industries[0]


def seasonal_signal(today: dt.date) -> str:
    month = today.month
    if month in (3, 4, 5):
        return "春季焕新"
    if month in (6, 7, 8):
        return "夏季清爽与夜间消费"
    if month in (9, 10, 11):
        return "秋季开学、换季与聚会"
    return "冬季暖心、节庆与年终消费"


def payday_signal(today: dt.date) -> str:
    if 1 <= today.day <= 5:
        return "月初预算刚释放，适合会员充值和套餐"
    if 15 <= today.day <= 20:
        return "月中适合做轻促销和复购提醒"
    if today.day >= 25:
        return "月底适合做库存、预约和下月预售"
    return "常规经营日，适合做低门槛到店理由"


def next_step_note(config: dict) -> str:
    brand = config.get("brand_name") or "大可AI"
    website = config.get("website") or "https://duckai.cn"
    lines = [
        "今天先执行其中一个动作即可，建议晚上复盘曝光、咨询、到店和成交四个数字。",
        "",
        f"如果后续要做成门店专属营销日历、活动方案和 AI 智能体自动化，可以访问{brand}了解更多：{website}",
    ]
    if config.get("wechat"):
        lines.append(f"微信：{config['wechat']}")
    if config.get("phone"):
        lines.append(f"电话：{config['phone']}")
    return "\n".join(lines)


def build_brief(config: dict, today: dt.date) -> str:
    profile = config.get("customer_profile", {})
    city = profile.get("city") or config.get("default_city") or "本地"
    industry = pick_industry(config)
    actions = INDUSTRY_ACTIONS.get(industry, INDUSTRY_ACTIONS["餐饮"])
    weekday = WEEKDAY_NAMES[today.weekday()]
    fixed = FIXED_SIGNALS.get(today.strftime("%m-%d"))
    signals = [f"{weekday}经营节奏", seasonal_signal(today), payday_signal(today)]
    if fixed:
        signals.insert(0, fixed)

    source_note = "信息整理来源：公开节日节点、通用行业营销日历及大可AI本地生活运营经验。本简报未接入实时热搜，仅供今日运营参考。"

    video_titles = [
        f"{city}{industry}今天可以这样做一个到店理由",
        f"{weekday}别空档，{industry}门店用这招拉一波客流",
        "一个低成本活动，今天就能开始试",
    ]

    return f"""# 今日实体店营销简报

日期：{today.isoformat()}（{weekday}）
城市：{city}
适用行业：{industry}

## 今日判断
今天适合围绕“{signals[0]}”做轻量活动，重点不是大促，而是给老客和附近潜在顾客一个今天到店或预约的理由。

## 可借势热点
1. {signals[0]}：适合做今日限定、预约提醒或会员权益。
   适合门店：{industry}及附近社区型门店
   今日动作：把活动门槛降低，主推一个最容易下单或预约的产品。

2. {signals[1]}：适合结合季节需求做内容和陈列。
   适合门店：有季节产品、护理、餐饮、课程或服务项目的门店
   今日动作：用一条朋友圈或短视频说明“为什么今天适合来”。

3. {signals[2]}：适合做复购、预售或会员沟通。
   适合门店：有会员、社群、预约或套餐的门店
   今日动作：对老客发一条一对一或社群提醒，不要群发硬广。

## 今天可以直接执行
- 到店活动：{actions['store']}
- 社群动作：{actions['community']}
- 朋友圈/视频号：{actions['social']}
- 团购/点评页：检查主图、套餐名和营业时间，把今日主推放在第一屏。

## 可复制文案
朋友圈：
{actions['copy']}

社群：
今天店里准备了一个小活动，适合最近正好有需要的朋友。想了解的话可以直接回我，我按你的情况推荐，不用盲选。

短视频标题：
""" + "\n".join(f"- {title}" for title in video_titles) + f"""

## 不建议蹭的内容
- 不蹭灾害、事故、冲突、疾病和负面社会事件。
- 不用“保证有效”“一定涨客流”“必爆”等承诺。
- 没有核实的平台热搜，不要写成官方趋势。

## 信息来源
{source_note}

## 下一步建议
{next_step_note(config)}
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="assets/config.example.json", help="Path to customer config JSON")
    parser.add_argument("--date", help="Date in YYYY-MM-DD format. Defaults to today.")
    args = parser.parse_args()

    today = dt.date.fromisoformat(args.date) if args.date else dt.date.today()
    config = load_config(Path(args.config))
    print(build_brief(config, today))


if __name__ == "__main__":
    main()
