#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
早安图生成脚本 - 样图测试版
"""

import os
import sys
import json
import random
import requests
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

# ============================================================
# 配置
# ============================================================
BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"
OUTPUT_DIR = BASE_DIR / "output"

OUTPUT_WIDTH = 1080
OUTPUT_HEIGHT = 1920

# 字体路径
FONT_QUOTE = str(FONTS_DIR / "DreamHanSerif-W13.ttc")       # 早安语录
FONT_DATE_INFO = str(FONTS_DIR / "DreamHanSerif-W20.ttc")    # 年月/星期/温度
FONT_DAY_NUM = str(FONTS_DIR / "站酷小微LOGO体.ttf")         # 日期数字

# 固定元素
FIXED_ELEMENTS = str(ASSETS_DIR / "fixed_elements.png")

# 语录库
QUOTES_FILE = str(BASE_DIR / "data" / "quotes.json")

# Unsplash 关键词
UNSPLASH_KEYWORDS = ["landscape", "nature", "scenery", "forest", "mountain", "ocean", "lake", "garden", "sunrise", "sunset"]

# ============================================================
# 语录库
# ============================================================
DEFAULT_QUOTES = [
    "人生真正的丰盈，不是拥有多少，而是内心始终留得住从容。",
    "每一个清晨，都是一次重新出发的机会。",
    "愿你眼里有光，心中有爱，脚下有路。",
    "生活不是等待暴风雨过去，而是学会在雨中起舞。",
    "温柔半两，从容一生。",
    "山高水长，怕什么来不及，慌什么到不了。",
    "时光会老，容颜不老，愿你被岁月温柔以待。",
    "心若向阳，无畏悲伤。",
    "最好的时光，是当下。",
    "愿你三冬暖，愿你春不寒。",
    "人生没有白走的路，每一步都算数。",
    "所有美好，都值得等待。",
    "愿你成为自己的太阳，无需凭借谁的光。",
    "生活明朗，万物可爱。",
    "愿你历尽千帆，归来仍是少年。",
    "把每一天都当作生命的最后一天来过。",
    "心有猛虎，细嗅蔷薇。",
    "愿你被这个世界温柔以待。",
    "岁月静好，现世安稳。",
    "愿你所有的努力都不被辜负。",
]


def get_random_quote():
    """获取随机语录"""
    if os.path.exists(QUOTES_FILE):
        with open(QUOTES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            quotes = [q["content"] for q in data.get("quotes", []) if q.get("enabled", True)]
            if quotes:
                return random.choice(quotes)
    return random.choice(DEFAULT_QUOTES)


def get_weekday_chinese(weekday):
    """星期数字转中文"""
    return ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][weekday]


# ============================================================
# 图片获取
# ============================================================
def fetch_unsplash_image():
    """从 Unsplash 获取随机风景图片"""
    keyword = random.choice(UNSPLASH_KEYWORDS)
    
    print(f"正在从 Unsplash 获取图片 (关键词: {keyword})...")
    
    for attempt in range(3):
        try:
            # 使用 Unsplash API (demo key for development)
            api_url = f"https://api.unsplash.com/photos/random"
            params = {
                "query": keyword,
                "orientation": "portrait",
                "client_id": "Wdi2qF7xGzJ9T6sJmFqBkG8r4XzLpNaHc3YvEwDkM0o"
            }
            resp = requests.get(api_url, params=params, timeout=15)
            
            if resp.status_code == 200:
                data = resp.json()
                # 获取图片下载链接
                img_url = data.get("urls", {}).get("regular", "")
                if img_url:
                    img_resp = requests.get(img_url, timeout=30)
                    if img_resp.status_code == 200 and len(img_resp.content) > 10000:
                        img = Image.open(BytesIO(img_resp.content))
                        if is_grayscale(img):
                            print(f"  图片为黑白，重新获取...")
                            continue
                        print(f"  获取成功: {img.size}")
                        return img
            else:
                print(f"  API 返回 {resp.status_code}, 尝试备用方式...")
        except Exception as e:
            print(f"  请求异常: {e}, 重试...")
        
        # 备用方式1: 使用 Unsplash Source（风景图片，无需 API key）
        try:
            source_url = f"https://source.unsplash.com/{OUTPUT_WIDTH}x{OUTPUT_HEIGHT}/?landscape,nature,scenery"
            resp = requests.get(source_url, timeout=30, allow_redirects=True)
            if resp.status_code == 200 and len(resp.content) > 10000:
                img = Image.open(BytesIO(resp.content))
                if is_grayscale(img):
                    print(f"  图片为黑白，重新获取...")
                    continue
                print(f"  Unsplash Source 获取成功: {img.size}")
                return img
        except Exception as e:
            print(f"  Unsplash Source 失败: {e}")
        
        # 备用方式2: 使用 Lorem Flickr（风景图片）
        try:
            flickr_url = f"https://loremflickr.com/{OUTPUT_WIDTH}/{OUTPUT_HEIGHT}/landscape,nature"
            resp = requests.get(flickr_url, timeout=30, allow_redirects=True)
            if resp.status_code == 200 and len(resp.content) > 5000:
                img = Image.open(BytesIO(resp.content))
                if is_grayscale(img):
                    print(f"  图片为黑白，重新获取...")
                    continue
                print(f"  Lorem Flickr 获取成功: {img.size}")
                return img
        except Exception as e:
            print(f"  Lorem Flickr 失败: {e}")
    
    # 所有尝试失败，使用纯色渐变背景
    print("  所有尝试失败，使用渐变背景")
    return create_gradient_background()


def is_grayscale(img):
    """检查图片是否为黑白"""
    img_small = img.resize((100, 100))
    pixels = list(img_small.getdata())
    if len(pixels[0]) == 4:
        pixels = [(r, g, b) for r, g, b, a in pixels]
    elif len(pixels[0]) == 1:
        return True
    
    # 计算饱和度
    gray_count = 0
    for p in pixels:
        r, g, b = p[0], p[1], p[2]
        max_c = max(r, g, b)
        min_c = min(r, g, b)
        if max_c == 0:
            saturation = 0
        else:
            saturation = (max_c - min_c) / max_c
        if saturation < 0.1:
            gray_count += 1
    
    gray_ratio = gray_count / len(pixels)
    return gray_ratio > 0.8


def create_gradient_background():
    """创建渐变背景作为备用"""
    img = Image.new("RGB", (OUTPUT_WIDTH, OUTPUT_HEIGHT))
    draw = ImageDraw.Draw(img)
    
    # 柔和的暖色渐变
    for y in range(OUTPUT_HEIGHT):
        ratio = y / OUTPUT_HEIGHT
        r = int(200 + 55 * ratio)
        g = int(180 + 50 * ratio)
        b = int(160 + 60 * ratio)
        draw.line([(0, y), (OUTPUT_WIDTH, y)], fill=(r, g, b))
    
    return img


# ============================================================
# 天气获取
# ============================================================
def fetch_weather():
    """获取海口天气"""
    try:
        # 使用 wttr.in 免费 API
        url = "https://wttr.in/Haikou?format=j1"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            current = data["current_condition"][0]
            temp_c = current["temp_C"]
            # 尝试获取今日最高最低温
            weather = data.get("weather", [])
            if weather:
                today = weather[0]
                max_temp = today["maxtempC"]
                min_temp = today["mintempC"]
                return {
                    "min_temp": min_temp,
                    "max_temp": max_temp,
                    "current_temp": temp_c,
                    "desc": current.get("lang_zh", [{}])[0].get("value", current.get("weatherDesc", [{}])[0].get("value", ""))
                }
            return {
                "min_temp": temp_c,
                "max_temp": temp_c,
                "current_temp": temp_c,
                "desc": ""
            }
    except Exception as e:
        print(f"天气获取失败: {e}")
    
    return {"min_temp": "--", "max_temp": "--", "current_temp": "--", "desc": ""}


# ============================================================
# 图片生成核心
# ============================================================
def generate_morning_poster(background_img, weather, quote, date_info):
    """生成早安图"""
    
    # 1. 创建画布
    canvas = Image.new("RGB", (OUTPUT_WIDTH, OUTPUT_HEIGHT), (255, 255, 255))
    
    # 2. 处理背景图片 - 裁剪为竖版并放置在上部
    img_area_height = 1300  # 风景区图片高度 1300px
    bg_resized = ImageOps.fit(background_img, (OUTPUT_WIDTH, img_area_height), method=Image.LANCZOS)
    canvas.paste(bg_resized, (0, 0))
    
    # 3. 下半部分白色背景
    info_area_top = img_area_height
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([(0, info_area_top), (OUTPUT_WIDTH, OUTPUT_HEIGHT)], fill=(255, 255, 255))
    
    # 4. 加载字体
    try:
        font_quote = ImageFont.truetype(FONT_QUOTE, 40)  # 早安语录 40px
    except:
        font_quote = ImageFont.truetype(FONT_QUOTE, 40, index=0)
    
    # 5. 绘制日期区域
    # 新布局：年月(旋转90°)在日期左侧 | 日期数字 | 星期和温度在日期右侧
    date_start_y = img_area_height + 45  # 日期上移10px（原55-10=45）
    week_start_y = img_area_height + 80  # 星期的顶部（比日期少5px）
    shift_left = 165  # 整体向左移动165px（原150+15=165）
    
    # 日期数字 (大号，居中对齐)
    day_text = date_info["day"]
    font_day_num = ImageFont.truetype(FONT_DAY_NUM, 150)
    bbox = draw.textbbox((0, 0), day_text, font=font_day_num)
    day_width = bbox[2] - bbox[0]
    day_height = bbox[3] - bbox[1]
    day_x = OUTPUT_WIDTH - 80 - day_width // 2 - shift_left  # 日期数字位置，向左移动150px
    day_y = date_start_y
    draw.text((day_x, day_y), day_text, font=font_day_num, fill=(0, 0, 0))
    
    # 年月 (顺时针旋转90°，放置在日期左侧，距离15px，顶部距风景图片100px)
    year_month_text = date_info["year_month"]
    font_year_month = ImageFont.truetype(FONT_DATE_INFO, 28)
    # 获取年月文字的尺寸
    year_month_bbox = draw.textbbox((0, 0), year_month_text, font=font_year_month)
    year_month_height = year_month_bbox[3] - year_month_bbox[1]
    # 创建临时图片（刚好容纳文字）
    temp_img = Image.new("RGBA", (200, year_month_height + 10), (255, 255, 255, 0))
    temp_draw = ImageDraw.Draw(temp_img)
    temp_draw.text((0, 0), year_month_text, font=font_year_month, fill=(0, 0, 0, 255))
    # 顺时针旋转90°
    year_month_rotated = temp_img.rotate(-90, expand=True, fillcolor=(255, 255, 255, 0))
    # 放置在日期左侧，间距15px，顶部距风景图片100px
    year_month_x = day_x - year_month_rotated.width - 15
    year_month_y = img_area_height + 100  # 顶部距风景图片100px
    canvas.paste(year_month_rotated, (int(year_month_x), int(year_month_y)), year_month_rotated)
    
    # 星期 (字号53px) 和 温度 放在日期右侧，垂直排列
    font_week = ImageFont.truetype(FONT_DATE_INFO, 53)
    week_text = date_info["week"]
    bbox = draw.textbbox((0, 0), week_text, font=font_week)
    week_width = bbox[2] - bbox[0]
    week_height = bbox[3] - bbox[1]
    
    font_temp = ImageFont.truetype(FONT_DATE_INFO, 28)
    temp_text = f"{weather['min_temp']}°~{weather['max_temp']}°"
    bbox = draw.textbbox((0, 0), temp_text, font=font_temp)
    temp_width = bbox[2] - bbox[0]
    temp_height = bbox[3] - bbox[1]
    
    # 右侧内容起始位置（在日期数字右侧，间距15px）
    right_x = day_x + day_width + 15
    # 星期
    draw.text((right_x, week_start_y), week_text, font=font_week, fill=(0, 0, 0))
    # 温度（在星期下方，间距35px）
    draw.text((right_x, week_start_y + week_height + 35), temp_text, font=font_temp, fill=(0, 0, 0))
    
    # 6. 绘制早安语录 (左侧区域)
    quote_y = img_area_height + 100  # 语录距离风景框 100px
    draw_quote_text(draw, quote, font_quote, 60, quote_y, OUTPUT_WIDTH - 160)
    
    # 7. 叠加固定元素 (缩小版，四边留 60px 边距)
    if os.path.exists(FIXED_ELEMENTS):
        fixed = Image.open(FIXED_ELEMENTS).convert("RGBA")
        # 计算缩放比例，确保四边都有 60px 边距
        margin = 60
        available_width = OUTPUT_WIDTH - 2 * margin
        available_height = OUTPUT_HEIGHT - 2 * margin
        fixed_w, fixed_h = fixed.size
        
        # 按宽高比计算缩放
        scale_w = available_width / fixed_w
        scale_h = available_height / fixed_h
        scale = min(scale_w, scale_h)
        
        new_w = int(fixed_w * scale)
        new_h = int(fixed_h * scale)
        fixed_scaled = fixed.resize((new_w, new_h), Image.LANCZOS)
        
        # 居中放置
        x = (OUTPUT_WIDTH - new_w) // 2
        y = (OUTPUT_HEIGHT - new_h) // 2
        
        # 使用 mask 处理透明通道
        canvas.paste(fixed_scaled, (x, y), fixed_scaled)
    
    return canvas


def draw_quote_text(draw, text, font, x, y, max_width):
    """绘制自动换行的语录文本
    规则：
    1. 遇到逗号（，）自动断行
    2. 句号（。）不能单独断行
    """
    lines = []
    current_line = ""
    
    for i, char in enumerate(text):
        test_line = current_line + char
        bbox = draw.textbbox((0, 0), test_line, font=font)
        line_width = bbox[2] - bbox[0]
        
        # 规则1：遇到逗号自动断行
        if char == "，":
            lines.append(test_line)
            current_line = ""
            continue
        
        # 规则2：句号不能单独断行
        if line_width > max_width:
            # 检查如果断行，句号是否会单独一行
            if current_line and current_line[-1] == "。":
                # 句号不能单独一行，把句号移回当前行末尾
                lines.append(current_line)
                current_line = char
            else:
                # 正常断行
                lines.append(current_line)
                current_line = char
        else:
            current_line = test_line
    
    if current_line:
        lines.append(current_line)
    
    # 合并只有句号的行到上一行末尾
    merged_lines = []
    for line in lines:
        if line == "。" and merged_lines:
            merged_lines[-1] = merged_lines[-1] + "。"
        else:
            merged_lines.append(line)
    
    lines = merged_lines
    
    # 绘制每一行
    line_height = int(40 * 1.75)  # 行间距 1.75 倍
    for i, line in enumerate(lines):
        draw.text((x, y + i * line_height), line, font=font, fill=(0, 0, 0))


# ============================================================
# 主程序
# ============================================================
def main():
    print("=" * 50)
    print("早安图生成 - 样图测试")
    print("=" * 50)
    
    # 1. 获取数据
    print("\n[1/4] 获取风景图片...")
    background = fetch_unsplash_image()
    
    print("\n[2/4] 获取天气数据...")
    weather = fetch_weather()
    print(f"  海口天气: {weather['min_temp']}°~{weather['max_temp']}°")
    
    print("\n[3/4] 选择早安语录...")
    quote = get_random_quote()
    print(f"  语录: {quote}")
    
    # 2. 获取日期信息
    now = datetime.now()
    date_info = {
        "year_month": now.strftime("%Y/%m"),
        "day": now.strftime("%d"),
        "week": get_weekday_chinese(now.weekday()),
    }
    print(f"  日期: {date_info['year_month']} {date_info['day']} {date_info['week']}")
    
    # 3. 生成早安图
    print("\n[4/4] 生成早安图...")
    poster = generate_morning_poster(background, weather, quote, date_info)
    
    # 4. 保存
    output_dir = OUTPUT_DIR / now.strftime("%Y-%m-%d")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"morning_{now.strftime('%Y%m%d_%H%M%S')}.jpg"
    poster.save(str(output_path), "JPEG", quality=95)
    
    print(f"\n✅ 早安图已保存: {output_path}")
    return str(output_path)


if __name__ == "__main__":
    from io import BytesIO
    main()
