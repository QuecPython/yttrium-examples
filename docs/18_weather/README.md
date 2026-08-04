# 天气应用

通过蜂窝网络（4G）获取 wttr.in 实时天气数据，展示当前天气和三日预报。

## 功能概述

- 数据源：wttr.in 免费 API（HTTP）
- 当前天气：温度、描述、湿度
- 三日预报：最高/最低温度 + 天气图标
- 城市切换：点击城市名循环切换 5 个城市
- 15 分钟自动刷新

## 界面布局

```
┌─────────────────────────────┐
│ 2026/07/31    [☀️]  32°     │
│ 14:30:45      晴            │
│ Guilin >     💧65%          │
│ OK 14:30                    │
├────────┬────────┬───────────┤
│  ☀️     │  🌤️    │  ☁️       │
│ Today  │Tomorrow│  Day+2    │
│ 32/25  │ 31/24  │  30/23    │
└────────┴────────┴───────────┘
```

## 关键代码

```python
# 拉取数据
url = "http://wttr.in/Guilin?format=j1"
data = request.get(url).json()
cur = data["current_condition"][0]
cur["temp_C"]         # 温度
cur["weatherDesc"]    # 描述

# 三日预报
for d in data["weather"][:3]:
    d["maxtempC"], d["mintempC"]   # 最高/最低温
```

## 天气图标

7 个 48×48 PNG，根据 wttr.in 天气码自动切换：

| 图标 | 天气 |
|---|---|
| `weather_sunny.png` | 晴 |
| `weather_partly_cloudy.png` | 多云 |
| `weather_cloudy.png` | 阴 |
| `weather_rainy.png` | 雨 |
| `weather_thunder.png` | 雷暴 |
| `weather_snowy.png` | 雪 |
| `weather_foggy.png` | 雾 |

## 代码位置

[src/weather.py](../../src/weather.py) → `class WeatherPage(AppPage)`

## 涉及模块

| 模块 | 用途 |
|---|---|
| `request` | HTTP 请求 |
| `lvgl` | card、img、label、timer、btn |
