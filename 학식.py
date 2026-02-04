#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import requests
from bs4 import BeautifulSoup
import re
from collections import OrderedDict

import shutil
from wcwidth import wcswidth

# 터미널 길이 크기만큼 horizontal line
def print_hr(char="="):
    width = shutil.get_terminal_size(fallback=(80, 20)).columns
    print(char * width)

# 한글은 터미널 2칸이더라고
def visual_len(s: str) -> int:
    """
    터미널에서 실제 차지하는 column 수
    (한글=2, 영문=1)
    """
    return wcswidth(s)

# 블록 단위 출력
def print_wrapped_menu(kind, menu,
                       base_indent="  ",
                       cont_indent="         "):
    width = shutil.get_terminal_size(fallback=(80, 20)).columns

    prefix = f"{base_indent}-{kind}: "
    current = prefix

    items = [x.strip() for x in menu.split(",") if x.strip()]

    for item in items:
        chunk = item + ", "

        if wcswidth(current + chunk) > width:
            print(current.rstrip())
            current = cont_indent + chunk
        else:
            current += chunk

    if current.strip():
        print(current.rstrip(", "))


URL = "https://cnutoday.jnu.ac.kr/Program/MealPlan.aspx"

# -------------------------
# rate limit
# -------------------------
_last_fetch = 0.0

def fetch_html():
    global _last_fetch
    dt = time.time() - _last_fetch
    if dt < 1.0:
        time.sleep(1.0 - dt)

    r = requests.get(URL, timeout=10)
    r.raise_for_status()
    _last_fetch = time.time()
    return r.text

# -------------------------
# utils
# -------------------------
def clean(x):
    return re.sub(r"\s+", " ", x).strip()

TARGET_RESTAURANTS = ["제1학생마루식당", "햇들마루"]

DAY_OFFSET = {
    "오늘": 0,
    "내일": 1,
    "모레": 2,
}

MEAL_ALIAS = {
    "점심": "중식",
    "중식": "중식",
    "저녁": "석식",
    "석식": "석식",
}

# -------------------------
# core logic
# -------------------------
def extract(doc, meal_type, day_offset):
    results = []

    for cont in doc.select("div.cont-b"):
        h5 = cont.select_one("h5")
        if not h5:
            continue

        name = clean(h5.text)
        if not any(r in name for r in TARGET_RESTAURANTS):
            continue

        for menu in cont.select("div.menu-container[data-isoperating='Y']"):
            p = menu.select_one("p")
            if not p:
                continue

            title = clean(p.text)
            if meal_type not in title:
                continue

            rows = [
                tr for tr in menu.select("tbody tr")
                if tr.select_one("td.food_month")
            ]

            if len(rows) <= day_offset:
                continue

            tr = rows[day_offset]
            tds = tr.select("td")

            results.append({
                "restaurant": name,
                "date": clean(tds[0].text),
                "kind": clean(tds[1].text),
                "menu": clean(tds[2].text),
            })

    return results

# -------------------------
# CLI
# -------------------------
def main():
    args = sys.argv[1:]

    # -------------------------
    # special command: 학식 사이트
    # -------------------------
    if len(args) == 1 and args[0] == "사이트":
        print("전남대 학식 사이트:")
        print(URL)
        return

    # -------------------------
    # argument parsing
    # -------------------------
    if len(args) == 0:
        day = "오늘"
        meal = "중식"
    elif len(args) == 2:
        day, meal = args
    else:
        print("사용법:")
        print("  학식")
        print("  학식 [오늘|내일|모레] [중식|석식]")
        print("  학식 사이트")
        sys.exit(1)

    meal = MEAL_ALIAS.get(meal)
    day_offset = DAY_OFFSET.get(day)

    if meal is None or day_offset is None:
        print("[ERROR] 인자 오류")
        sys.exit(1)

    # -------------------------
    # fetch & parse (1회만)
    # -------------------------
    html = fetch_html()
    doc = BeautifulSoup(html, "html.parser")

    menus = extract(doc, meal, day_offset)

    if not menus:
        print("[ERROR] 식단 정보 없음")
        return

    # -------------------------
    # group by restaurant
    # -------------------------
    from collections import OrderedDict
    grouped = OrderedDict()

    for m in menus:
        r = m["restaurant"]
        if r not in grouped:
            grouped[r] = {
                "date": m["date"],
                "items": []
            }
        grouped[r]["items"].append((m["kind"], m["menu"]))

    # -------------------------
    # output
    # -------------------------
    print(f"\n {day} {meal}")
    print_hr()

    for restaurant, data in grouped.items():
        print(f"■ {restaurant.split(":", 1)[0].strip()}")
        print(f"  {data['date']}")
        for kind, menu in data["items"]:
            print_wrapped_menu(kind, menu)
        print()

if __name__ == "__main__":
    main()
