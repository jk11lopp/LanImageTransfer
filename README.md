# 📱 局域网图片传输中心

> **手机选择图片 → 扫码连接 → 批量上传 → 图片直接保存到电脑**
>
> 无需互联网、云盘、数据线，手机和电脑在同一 Wi-Fi / 热点即可传输。

---

## ⭐ 支持

欢迎 ⭐ Star、🍴 Fork、🐛 提交 Issue、💡 提交功能建议。

<p align="center">
  <img src="./g.png" alt="赞赏" width="500">
</p>

---

## 🖥️ 软件界面

<p align="center">
  <img src="./w.png" alt="局域网图片传输中心" width="900">
</p>

---

## 📥 Windows 版本下载

<p align="center">
  <a href="https://release-assets.githubusercontent.com/github-production-release-asset/1385811367/66ee2d73-3d29-49b1-b37b-b7d5b738008d?sp=r&sv=2018-11-09&sr=b&spr=https&se=2026-09-25T02%3A20%3A44Z&rscd=attachment%3B+filename%3Dm.exe&rsct=application%2Foctet-stream&skoid=96c2d410-5711-43a1-aedd-ab1947aa7ab0&sktid=398a6654-997b-47e9-b12b-9515b896b4de&skt=2026-09-25T01%3A20%3A05Z&ske=2026-09-25T02%3A20%3A44Z&sks=b&skv=2018-11-09&sig=NGGT7Nm%2Bqc6Lgd5uEyo0K3BC0kswHShgK6MCgxtsT9M%3D&jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmVsZWFzZS1hc3NldHMuZ2l0aHVidXNlcmNvbnRlbnQuY29tIiwia2V5Ijoia2V5MSIsImV4cCI6MTc5MDMwMjU3OCwibmJmIjoxNzkwMzAwNzc4LCJwYXRoIjoicmVsZWFzZWFzc2V0cHJvZHVjdGlvbi5ibG9iLmNvcmUud2luZG93cy5uZXQifQ.zbascFWYd06GuO-j62pjGWNZ2RJA9IhHAbP9PaIvV7w&response-content-disposition=attachment%3B%20filename%3Dm.exe&response-content-type=application%2Foctet-stream">
    <strong>⬇️ 下载 m.exe</strong>
  </a>
  <br>
  免安装，下载后直接运行。
</p>

---

## ✨ 简介

基于 **Python + PyQt5 + Flask** 的本地图片传输工具：手机浏览器访问电脑本地页面，选图后经局域网传到电脑指定文件夹。全程无需互联网，图片不上传第三方云服务器。

---

## 🚀 核心特点

- 📡 **无需互联网**：手机与电脑在同一 Wi-Fi / 热点即可
- 📱 **扫码即用**：自动检测局域网 IP 并生成二维码，无需注册、登录、数据线、网盘
- 🖼️ **批量选图**：一次可选多张，带缩略图预览
- ❌ **可删除误选**：点图片右上角 `×` 删除
- ♾️ **无固定数量上限**：实际受手机内存、浏览器、网速等影响
- ⚡ **直传电脑**：本地 Flask 服务 `0.0.0.0:8888`
- 📂 **自定义保存位置**：默认 `程序目录/upload_images`
- 🔒 **本地传输**：手机 → 局域网 → 电脑 → 本地磁盘
- 🎨 **天空蓝科技风界面**

---

## 📱 使用流程

1. 电脑启动程序，点击 `▶ 启动上传服务`
2. 确认手机与电脑在同一局域网
3. 手机扫描二维码进入上传页
4. 选择图片（支持多选）
5. 检查，点 `×` 删除不需要的
6. 点击 `🚀 开始上传`

---

## 📂 图片保存

```text
upload_images/
├── IMG_001.jpg
├── IMG_002.jpg
└── ...
```

同名文件自动加编号（`IMG_001_1.jpg`），避免覆盖。

---

## 🛠️ 技术栈

| 技术 | 用途 |
| --- | --- |
| Python | 核心开发语言 |
| PyQt5 | Windows 桌面 GUI |
| Flask | 本地 HTTP 图片上传服务 |
| HTML / CSS / JS | 手机端上传页面 |
| qrcode | 自动生成二维码 |
| Socket | 获取局域网 IP |

---

## 📦 运行环境

Windows 10 / 11，Python 3.9+

```bash
pip install PyQt5 Flask qrcode
python main.py
```

---

## 📁 项目结构

```text
LAN-Image-Transfer/
├── main.py
├── README.md
├── requirements.txt
├── ScreenShot_2026-09-24_230717_024.png
└── upload_images/
```

---

## 🔥 防火墙与端口

首次启动可能弹出防火墙提示，需允许访问（建议“专用网络”）。默认端口 `8888`，如电脑 IP 为 `192.168.1.100`，手机访问 `http://192.168.1.100:8888`。

---

## 🔐 隐私与安全

传输路径：手机 → 局域网 → 你的电脑 → 指定文件夹，不会自动上传第三方云存储。

> ⚠️ 当前为 HTTP 局域网传输，非 HTTPS 加密。建议仅在信任的家庭 Wi-Fi、热点、实验室/办公室局域网使用，**不要在不可信公共网络开启服务**。

---

## 📌 注意事项

- 手机和电脑必须能互相访问：检查同一 Wi-Fi/热点、防火墙 `8888` 端口、路由器 AP/客户端隔离、多网卡、二维码 IP
- “无需互联网”仍需局域网连接
- 图片数量无固定上限，大量图片建议分批
- 同名文件自动加编号，避免覆盖

---

## 🧪 适用场景

- 🔬 科研实验：菌落、真菌培养、病害症状、植物、显微镜、实验过程、野外调查照片
- 🌱 植物病害调查：野外拍图 → 回实验室扫码批量上传
- 📷 手机照片整理：相册批量选择 → 局域网传输 → 电脑文件夹

---

## 🆚 与传统方式对比

| 方式 | 需要互联网 | 数据线 | 云服务器 | 批量选择 | 本地保存 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 本项目 | ❌ | ❌ | ❌ | ✅ | ✅ |
| 数据线 | ❌ | ✅ | ❌ | ✅ | ✅ |
| 网盘 | ✅ | ❌ | ✅ | ✅ | ✅ |
| 微信文件传输 | 通常需要 | ❌ | ✅ | ✅ | ❌ |
| 蓝牙 | ❌ | ❌ | ❌ | ✅ | ✅ |

---

## 📜 开源及使用许可

仅供个人学习、科研工作、非商业用途、内部使用、技术交流。

**未经作者明确书面授权，禁止将本项目用于任何商业用途**（包括商业软件/网站/APP、收费服务、商业销售、商业集成等）。商业用途请联系作者取得授权。

```text
Non-Commercial Use Only

Copyright (c) 2026

本项目仅允许个人学习、科研及其他非商业用途使用。
禁止未经授权的商业使用、商业销售、商业部署或商业集成。
商业用途请联系作者获得授权。
```

---

## ⚠️ 免责声明

本项目为个人开发工具，仅用于学习、科研和非商业用途。使用者应自行确保合法合规使用、对传输图片拥有合法使用权、不传输违法侵权内容、公共网络使用时自担风险、妥善保管数据。作者不对数据丢失、文件损坏、网络安全问题或其他间接损失承担责任。

---

## 🔧 后续开发计划

- [ ] 图片拖拽上传 / 进度条 / 速度 / 剩余时间
- [ ] 上传失败自动重试 / 记录 / 去重
- [ ] 图片自动分类 / 按日期建文件夹 / 文件夹管理
- [ ] 暗色模式 / EXIF 读取 / HEIC 支持
- [ ] HTTPS 加密 / 上传密码 PIN
- [ ] 开机启动 / 系统托盘 / EXE 便携版

---

## 📮 问题反馈

可提交 GitHub Issue，建议提供：

```text
QQ：3013633802
操作系统 / Windows 版本 / Python 版本：
手机型号 / 手机系统 / 浏览器：
网络环境：
错误信息：
```

---

> **无需互联网 · 无需数据线 · 无需云盘**
>
> **手机 → 📡 局域网 → 💻 电脑**
