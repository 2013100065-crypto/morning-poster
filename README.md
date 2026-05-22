# 云禾早安图

每天自动生成精美的早安图片，包含风景背景、日期、天气和早安语录。

## 功能特点

- 🌅 自动获取高质量风景图片
- 📅 自动显示当日日期和星期
- 🌡️ 自动获取海口市天气
- 💬 随机选择早安语录
- ⏰ 每天北京时间 00:01 自动生成

## 项目结构

```
云禾早安图/
├── .github/
│   └── workflows/
│       └── generate.yml    # GitHub Actions 配置
├── assets/
│   ├── fonts/              # 字体文件
│   │   ├── DreamHanSerif-W13.ttc
│   │   ├── DreamHanSerif-W20.ttc
│   │   └── 站酷小微LOGO体.ttf
│   └── fixed_elements.png  # 固定元素
├── data/
│   └── quotes.json         # 早安语录库
├── output/                 # 生成的早安图
├── generate.py             # 主程序
├── requirements.txt        # Python 依赖
└── README.md
```

## 设计参数

| 参数 | 值 |
|:---|:---|
| 画布尺寸 | 1080 × 1920 px |
| 风景图片高度 | 1300 px |
| 固定元素边距 | 60 px |
| 语录字号 | 40 px（梦源宋体 W13） |
| 语录行间距 | 1.75 倍 |
| 日期数字字号 | 150 px（站酷小微LOGO体） |
| 星期字号 | 53 px（梦源宋体 W20） |

## 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 运行生成
python generate.py
```

## 自动运行

本项目使用 GitHub Actions 实现每天自动生成：
- 运行时间：每天 UTC 16:01（北京时间 00:01）
- 生成的图片保存在 `output/` 目录
- 支持手动触发运行

## 字体来源

- 梦源宋体：[Google Fonts](https://fonts.google.com/)
- 站酷小微LOGO体：[站酷](https://www.zcool.com.cn/)
