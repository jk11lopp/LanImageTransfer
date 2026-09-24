# -*- coding: utf-8 -*-

"""
============================================================
天空蓝科技风 · 局域网手机图片上传工具
更新：手机端图片预览、可删除待上传图片
============================================================

功能：
1. 手机扫码上传图片，选择后预览图片，可单独删除不需要图片
2. 电脑与手机只需要处于同一局域网 / 手机热点
3. Flask 本地 HTTP 服务
4. PyQt5 天空蓝科技风 GUI
5. 自动获取局域网 IP
6. 自动生成二维码
7. 自定义图片保存目录
8. 实时运行日志

【Windows重要提示】
第一次启动Flask，如果Windows防火墙弹窗，请勾选【专用网络】允许访问。
防火墙拦截8888端口会导致手机无法访问网页。
============================================================
"""

import sys
import os
import socket
import threading
import time

from flask import Flask, request, render_template_string

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QLabel,
    QTextEdit,
    QFileDialog,
    QFrame,
    QSizePolicy
)

from PyQt5.QtCore import (
    Qt,
    QPoint,
    QTimer
)

from PyQt5.QtGui import (
    QFont,
    QPixmap,
    QColor,
    QPainter,
    QLinearGradient,
    QBrush,
    QIcon
)

import qrcode
from io import BytesIO


# ============================================================
# Flask
# ============================================================

app = Flask(__name__)


# ============================================================
# 全局状态
# ============================================================

class AppState:

    def __init__(self):

        self.save_dir = os.path.join(
            os.getcwd(),
            "upload_images"
        )

        self.flask_thread = None

        self.is_running = False

        self.upload_count = 0

        self.start_time = None


STATE = AppState()


# ============================================================
# 获取局域网 IP
# ============================================================

def get_local_hotspot_ips():

    ip_list = []

    try:

        s = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )

        s.connect(
            ("8.8.8.8", 80)
        )

        primary_ip = s.getsockname()[0]

        s.close()

        if primary_ip not in ip_list:

            ip_list.append(primary_ip)

    except Exception:
        pass

    try:

        host_name = socket.gethostname()

        _, _, addrs = socket.gethostbyname_ex(
            host_name
        )

        for ip in addrs:

            if (
                not ip.startswith("127.")
                and ip not in ip_list
            ):

                ip_list.append(ip)

    except Exception:
        pass

    return ip_list


# ============================================================
# 手机端网页【已更新：图片预览 + 删除单张】
# ============================================================

HTML_UPLOAD_PAGE = """

<!DOCTYPE html>

<html lang="zh-CN">

<head>

<meta charset="UTF-8">

<meta
name="viewport"
content="width=device-width,
initial-scale=1.0,
maximum-scale=1.0,
user-scalable=no">

<title>局域网图片传输</title>

<style>

*{
    box-sizing:border-box;
    margin:0;
    padding:0;
}

body{

    min-height:100vh;

    font-family:
    -apple-system,
    BlinkMacSystemFont,
    "Segoe UI",
    "Microsoft YaHei",
    sans-serif;

    background:
    linear-gradient(
        145deg,
        #eaf7ff 0%,
        #d7efff 45%,
        #f5fbff 100%
    );

    color:#17324d;

    padding:24px 18px 40px;

}


/* 顶部 */

.header{

    text-align:center;

    margin-bottom:24px;

}

.logo{

    width:76px;
    height:76px;

    margin:0 auto 14px;

    border-radius:24px;

    display:flex;

    align-items:center;

    justify-content:center;

    font-size:38px;

    background:
    linear-gradient(
        145deg,
        #4ebcff,
        #168ee8
    );

    box-shadow:
    0 12px 30px
    rgba(30,150,230,.25);

}

.header h1{

    font-size:25px;

    font-weight:800;

    color:#155783;

    margin-bottom:8px;

}

.header p{

    color:#6b8da5;

    font-size:14px;

}


/* 卡片 */

.card{

    max-width:520px;

    margin:0 auto 18px;

    background:
    rgba(255,255,255,.92);

    border-radius:24px;

    padding:22px;

    box-shadow:
    0 12px 35px
    rgba(39,139,199,.12);

    border:
    1px solid
    rgba(255,255,255,.9);

}


/* 上传区域 */

.upload-area{

    border:
    2px dashed
    #8bd1f7;

    border-radius:20px;

    padding:24px 20px;

    text-align:center;

    background:
    linear-gradient(
        180deg,
        #f5fcff,
        #edf9ff
    );

    transition:.2s;

}

.upload-area:hover{

    border-color:#38a9ee;

}


/* 图标 */

.upload-icon{

    font-size:50px;

    margin-bottom:12px;

}

.upload-title{

    font-size:18px;

    font-weight:700;

    color:#216489;

    margin-bottom:7px;

}

.upload-desc{

    font-size:13px;

    color:#8aa5b8;

    margin-bottom:22px;

}


/* 文件选择 */

.file-box{

    display:block;

    width:100%;

    padding:13px;

    background:#e9f7ff;

    border-radius:14px;

    color:#2576a3;

    font-size:14px;

    margin-bottom:14px;

}


/* 上传按钮 */

button{

    width:100%;

    border:none;

    padding:15px;

    border-radius:15px;

    font-size:17px;

    font-weight:700;

    color:white;

    cursor:pointer;

    background:
    linear-gradient(
        135deg,
        #55c4ff,
        #168fe5
    );

    box-shadow:
    0 8px 22px
    rgba(28,149,224,.25);

}

button:active{

    transform:scale(.98);

}

button:disabled{
    background:#b4d8f0;
}


/* 消息 */

#msg{

    margin-top:16px;

    padding:13px;

    border-radius:13px;

    font-size:14px;

    display:none;

}

.success{

    display:block !important;

    background:#e7f9ef;

    color:#238653;

}

.error{

    display:block !important;

    background:#fff0f0;

    color:#c34c4c;

}


/* 底部信息 */

.info{

    max-width:520px;

    margin:auto;

    display:flex;

    gap:10px;

}

.info-item{

    flex:1;

    padding:15px;

    background:
    rgba(255,255,255,.75);

    border-radius:16px;

    text-align:center;

}

.info-item .icon{

    font-size:23px;

}

.info-item span{

    display:block;

    margin-top:5px;

    font-size:12px;

    color:#7896aa;

}


/* 隐藏原生文件控件 */

input[type=file]{

    width:100%;

    margin-bottom:14px;

}

/* ============新增预览图片样式============ */
.preview-wrap{
    margin-top:16px;
    text-align:left;
}
.preview-title{
    font-size:14px;
    color:#216489;
    font-weight:600;
    margin-bottom:10px;
}
.preview-grid{
    display:grid;
    grid-template-columns: repeat(auto-fill, minmax(90px,1fr));
    gap:10px;
}
.preview-item{
    position:relative;
    border-radius:10px;
    overflow:hidden;
    background:#ffffff;
    border:1px solid #c8e7f7;
}
.preview-item img{
    width:100%;
    height:90px;
    object-fit:cover;
    display:block;
}
.del-btn{
    position:absolute;
    top:4px;
    right:4px;
    width:24px;
    height:24px;
    border-radius:50%;
    background:#ef5353;
    color:#fff;
    font-size:16px;
    display:flex;
    align-items:center;
    justify-content:center;
    cursor:pointer;
    border:none;
    box-shadow:0 2px 6px rgba(0,0,0,0.22);
}

</style>

</head>


<body>


<div class="header">

    <div class="logo">
        📷
    </div>

    <h1>
        局域网图片传输
    </h1>

    <p>
        无需互联网 · 手机扫码即可上传
    </p>

</div>


<div class="card">

    <div class="upload-area">

        <div class="upload-icon">
            ☁️
        </div>

        <div class="upload-title">
            选择需要上传的图片
        </div>

        <div class="upload-desc">
            支持手机相册批量选择图片，可删除不需要图片
        </div>

        <input
            type="file"
            id="fileInput"
            accept="image/*"
            multiple
        >
        <!--图片预览区域-->
        <div class="preview-wrap" id="previewWrap" style="display:none;">
            <div class="preview-title">待上传图片 <span id="fileCount">(0张)</span></div>
            <div class="preview-grid" id="previewGrid"></div>
        </div>

        <button id="uploadBtn" onclick="doUpload()" disabled>
            🚀 开始上传
        </button>

        <div id="msg"></div>

    </div>

</div>


<div class="info">

    <div class="info-item">

        <div class="icon">
            🔒
        </div>

        <span>
            局域网传输
        </span>

    </div>


    <div class="info-item">

        <div class="icon">
            ⚡
        </div>

        <span>
            极速上传
        </span>

    </div>


    <div class="info-item">

        <div class="icon">
            🛡️
        </div>

        <span>
            本地保存
        </span>

    </div>

</div>


<script>
//保存选中的文件数组，支持删除单张
let selectedFiles = [];

const fileInput = document.getElementById("fileInput");
const previewWrap = document.getElementById("previewWrap");
const previewGrid = document.getElementById("previewGrid");
const fileCountText = document.getElementById("fileCount");
const uploadBtn = document.getElementById("uploadBtn");
const msg = document.getElementById("msg");

//监听文件选择
fileInput.addEventListener('change',function(e){
    const files = Array.from(e.target.files);
    for(let f of files){
        selectedFiles.push(f);
    }
    renderPreview();
    //清空input，保证同一文件可以重复选
    fileInput.value = '';
})

//渲染预览
function renderPreview(){
    previewGrid.innerHTML = '';
    if(selectedFiles.length <= 0){
        previewWrap.style.display = 'none';
        uploadBtn.disabled = true;
        return;
    }
    previewWrap.style.display = 'block';
    uploadBtn.disabled = false;
    fileCountText.innerText = `(${selectedFiles.length}张)`;

    selectedFiles.forEach((file,idx)=>{
        const item = document.createElement('div');
        item.className = 'preview-item';

        const img = document.createElement('img');
        img.src = URL.createObjectURL(file);

        const delBtn = document.createElement('button');
        delBtn.className = 'del-btn';
        delBtn.innerText = '×';
        delBtn.onclick = function(){
            //释放内存
            URL.revokeObjectURL(img.src);
            selectedFiles.splice(idx,1);
            renderPreview();
        }

        item.appendChild(img);
        item.appendChild(delBtn);
        previewGrid.appendChild(item);
    })
}


async function doUpload(){
    msg.className = "";
    msg.style.display = "block";

    if(!selectedFiles || selectedFiles.length === 0){
        msg.innerText = "⚠️ 请先选择图片";
        msg.className = "error";
        return;
    }

    let successCount = 0;
    let errorCount = 0;

    msg.innerText = "⏳ 正在上传，请稍候...";

    for(let i=0;i<selectedFiles.length;i++){
        const formData = new FormData();
        formData.append("file", selectedFiles[i]);

        try{
            const res = await fetch("/upload", {
                method:"POST",
                body:formData
            });
            const data = await res.json();
            if(data.code === 200){
                successCount++;
            }else{
                errorCount++;
            }
        }
        catch(err){
            errorCount++;
        }
    }

    if(errorCount === 0){
        msg.innerText = "✅ 全部上传成功，共 " + successCount + " 张图片";
        msg.className = "success";
    }
    else{
        msg.innerText = "⚠️ 上传完成：成功 " + successCount + " 张，失败 " + errorCount + " 张";
        msg.className = "error";
    }
    //上传完成清空选择
    selectedFiles = [];
    renderPreview();
}

</script>


</body>

</html>

"""


# ============================================================
# Flask 路由
# ============================================================

@app.route("/", methods=["GET"])
def index():

    return render_template_string(
        HTML_UPLOAD_PAGE
    )


@app.route("/upload", methods=["POST"])
def upload_file():

    try:

        if "file" not in request.files:

            return {
                "code":400,
                "msg":"没有上传文件"
            },400


        f = request.files["file"]

        filename = f.filename


        if not filename:

            return {
                "code":400,
                "msg":"空文件名"
            },400


        os.makedirs(
            STATE.save_dir,
            exist_ok=True
        )


        # 防止简单的路径穿越
        filename = os.path.basename(
            filename
        )


        save_path = os.path.join(
            STATE.save_dir,
            filename
        )


        # 文件重名自动处理
        if os.path.exists(save_path):

            base, ext = os.path.splitext(
                filename
            )

            index = 1

            while os.path.exists(
                save_path
            ):

                new_name = (
                    f"{base}_{index}{ext}"
                )

                save_path = os.path.join(
                    STATE.save_dir,
                    new_name
                )

                index += 1


        f.save(save_path)


        STATE.upload_count += 1


        if main_win:

            main_win.append_log(
                f"✓ 收到图片："
                f"{os.path.basename(save_path)}"
            )

            main_win.update_upload_count()


        return {

            "code":200,

            "msg":"上传成功",

            "path":save_path

        },200


    except Exception as e:

        err_msg = (
            f"上传异常：{str(e)}"
        )


        if main_win:

            main_win.append_log(
                f"✕ {err_msg}"
            )


        return {

            "code":500,

            "msg":err_msg

        },500


# ============================================================
# Flask 服务
# ============================================================

main_win = None


def run_flask_server():

    try:

        STATE.is_running = True

        STATE.start_time = time.time()


        if main_win:

            main_win.update_service_status(
                True
            )


        app.run(
            host="0.0.0.0",
            port=8888,
            debug=False,
            use_reloader=False
        )


    except Exception as e:

        if main_win:

            main_win.append_log(
                f"✕ HTTP服务异常：{e}"
            )


    finally:

        STATE.is_running = False


        if main_win:

            main_win.update_service_status(
                False
            )

            main_win.append_log(
                "● HTTP服务已停止"
            )


# ============================================================
# 主窗口
# ============================================================

class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()


        global main_win

        main_win = self


        self._drag_pos = QPoint()


        self.setWindowFlags(
            Qt.FramelessWindowHint
        )

        self.setAttribute(
            Qt.WA_TranslucentBackground
        )


        self.resize(
            1200,
            900
        )


        self.setMinimumSize(
            900,
            650
        )


        self.build_ui()


        self.refresh_ip()


        # 状态刷新定时器
        self.timer = QTimer(self)

        self.timer.timeout.connect(
            self.refresh_status
        )

        self.timer.start(
            1000
        )


    # ========================================================
    # 主 UI
    # ========================================================

    def build_ui(self):

        root = QWidget()

        self.setCentralWidget(
            root
        )


        root.setStyleSheet("""

        QWidget{

            font-family:
            "Microsoft YaHei",
            "Segoe UI";

            color:#23445c;

        }

        """)


        root_layout = QVBoxLayout(
            root
        )

        root_layout.setContentsMargins(
            0,0,0,0
        )

        root_layout.setSpacing(
            0
        )


        # ====================================================
        # 标题栏
        # ====================================================

        self.title_bar = QFrame()

        self.title_bar.setFixedHeight(
            68
        )

        self.title_bar.setStyleSheet("""

        QFrame{

            background:
            qlineargradient(
                x1:0,y1:0,
                x2:1,y2:0,
                stop:0 #43B9F5,
                stop:0.5 #229BE5,
                stop:1 #1686D2
            );

            border-top-left-radius:20px;
            border-top-right-radius:20px;

        }

        """)


        title_layout = QHBoxLayout(
            self.title_bar
        )

        title_layout.setContentsMargins(
            24,0,14,0
        )


        # Logo

        logo = QLabel("☁")

        logo.setFixedSize(
            42,
            42
        )

        logo.setAlignment(
            Qt.AlignCenter
        )

        logo.setStyleSheet("""

        QLabel{

            background:
            rgba(255,255,255,.18);

            border-radius:13px;

            color:white;

            font-size:25px;

        }

        """)


        title_layout.addWidget(
            logo
        )


        title_box = QVBoxLayout()

        title_box.setSpacing(
            0
        )


        title = QLabel(
            "局域网图片传输中心"
        )

        title.setStyleSheet("""

        QLabel{

            color:white;

            font-size:19px;

            font-weight:800;

        }

        """)


        subtitle = QLabel(
            "LAN IMAGE TRANSFER  •  LOCAL NETWORK"
        )

        subtitle.setStyleSheet("""

        QLabel{

            color:
            rgba(255,255,255,.75);

            font-size:9px;

            letter-spacing:1px;

        }

        """)


        title_box.addWidget(
            title
        )

        title_box.addWidget(
            subtitle
        )


        title_layout.addLayout(
            title_box
        )


        title_layout.addStretch()


        # 最小化

        self.btn_min = QPushButton(
            "—"
        )

        self.btn_min.setFixedSize(
            40,
            40
        )

        self.btn_min.setStyleSheet("""

        QPushButton{

            background:
            rgba(255,255,255,.12);

            border:none;

            border-radius:12px;

            color:white;

            font-size:20px;

        }

        QPushButton:hover{

            background:
            rgba(255,255,255,.25);

        }

        """)


        self.btn_min.clicked.connect(
            self.showMinimized
        )


        # 关闭

        self.btn_close = QPushButton(
            "×"
        )

        self.btn_close.setFixedSize(
            40,
            40
        )

        self.btn_close.setStyleSheet("""

        QPushButton{

            background:
            rgba(255,255,255,.12);

            border:none;

            border-radius:12px;

            color:white;

            font-size:25px;

        }

        QPushButton:hover{

            background:#EF6262;

        }

        """)


        self.btn_close.clicked.connect(
            self.close
        )


        title_layout.addWidget(
            self.btn_min
        )

        title_layout.addSpacing(
            7
        )

        title_layout.addWidget(
            self.btn_close
        )


        self.title_bar.mousePressEvent = \
            self.mouse_press_event

        self.title_bar.mouseMoveEvent = \
            self.mouse_move_event


        root_layout.addWidget(
            self.title_bar
        )


        # ====================================================
        # 内容背景
        # ====================================================

        content = QFrame()

        content.setStyleSheet("""

        QFrame{

            background:
            #F2FAFF;

            border-bottom-left-radius:20px;

            border-bottom-right-radius:20px;

        }

        """)


        content_layout = QVBoxLayout(
            content
        )

        content_layout.setContentsMargins(
            25,22,25,20
        )

        content_layout.setSpacing(
            16
        )


        root_layout.addWidget(
            content
        )


        # ====================================================
        # 顶部状态区
        # ====================================================

        status_layout = QHBoxLayout()

        status_layout.setSpacing(
            15
        )


        # 服务状态

        self.status_card = \
            self.create_info_card(
                "●",
                "服务状态",
                "未启动"
            )

        status_layout.addWidget(
            self.status_card
        )


        # IP

        self.ip_card = \
            self.create_info_card(
                "🌐",
                "局域网地址",
                "检测中..."
            )

        status_layout.addWidget(
            self.ip_card
        )


        # 上传数量

        self.count_card = \
            self.create_info_card(
                "📤",
                "已接收图片",
                "0 张"
            )

        status_layout.addWidget(
            self.count_card
        )


        content_layout.addLayout(
            status_layout
        )


        # ====================================================
        # 主区域
        # ====================================================

        main_area = QHBoxLayout()

        main_area.setSpacing(
            18
        )


        # 左侧

        left = QVBoxLayout()

        left.setSpacing(
            15
        )


        # 保存目录

        dir_card = QFrame()

        dir_card.setStyleSheet(
            self.card_style()
        )


        dir_layout = QVBoxLayout(
            dir_card
        )

        dir_layout.setContentsMargins(
            20,18,20,18
        )

        dir_layout.setSpacing(
            10
        )


        dir_title = QLabel(
            "📂  图片保存位置"
        )

        dir_title.setStyleSheet("""

        QLabel{

            font-size:15px;

            font-weight:700;

            color:#28627F;

        }

        """)


        dir_layout.addWidget(
            dir_title
        )


        self.edit_dir = QLineEdit()

        self.edit_dir.setText(
            STATE.save_dir
        )

        self.edit_dir.setReadOnly(
            True
        )

        self.edit_dir.setStyleSheet("""

        QLineEdit{

            background:#F1F9FE;

            border:
            1px solid #D4EAF7;

            border-radius:11px;

            padding:11px;

            color:#4B7188;

            font-size:15px;

        }

        """)


        dir_layout.addWidget(
            self.edit_dir
        )


        btn_dir = QPushButton(
            "选择保存文件夹"
        )

        btn_dir.setStyleSheet(
            self.secondary_button()
        )

        btn_dir.clicked.connect(
            self.select_folder
        )


        dir_layout.addWidget(
            btn_dir
        )


        left.addWidget(
            dir_card
        )


        # 网络访问卡片

        network_card = QFrame()

        network_card.setStyleSheet(
            self.card_style()
        )


        network_layout = QVBoxLayout(
            network_card
        )

        network_layout.setContentsMargins(
            20,18,20,18
        )

        network_layout.setSpacing(
            10
        )


        network_title = QLabel(
            "📡  手机访问地址"
        )

        network_title.setStyleSheet("""

        QLabel{

            font-size:15px;

            font-weight:700;

            color:#28627F;

        }

        """)


        network_layout.addWidget(
            network_title
        )


        self.edit_ip = QLineEdit()

        self.edit_ip.setReadOnly(
            True
        )

        self.edit_ip.setStyleSheet("""

        QLineEdit{

            background:#EDF9FF;

            border:
            1px solid #BDE4F8;

            border-radius:12px;

            padding:12px;

            color:#1788C8;

            font-size:15px;

            font-weight:bold;

        }

        """)


        network_layout.addWidget(
            self.edit_ip
        )


        self.btn_refresh_ip = QPushButton(
            "⟳  刷新局域网地址"
        )

        self.btn_refresh_ip.setStyleSheet(
            self.secondary_button()
        )

        self.btn_refresh_ip.clicked.connect(
            self.refresh_ip
        )


        network_layout.addWidget(
            self.btn_refresh_ip
        )


        left.addWidget(
            network_card
        )


        # 服务控制

        control_card = QFrame()

        control_card.setStyleSheet(
            self.card_style()
        )


        control_layout = QVBoxLayout(
            control_card
        )

        control_layout.setContentsMargins(
            20,18,20,18
        )


        control_title = QLabel(
            "⚡  服务控制"
        )

        control_title.setStyleSheet("""

        QLabel{

            font-size:15px;

            font-weight:700;

            color:#28627F;

        }

        """)


        control_layout.addWidget(
            control_title
        )


        buttons = QHBoxLayout()

        buttons.setSpacing(
            10
        )


        self.btn_start = QPushButton(
            "▶  启动上传服务"
        )

        self.btn_start.setMinimumHeight(
            45
        )

        self.btn_start.setStyleSheet(
            self.primary_button()
        )

        self.btn_start.clicked.connect(
            self.start_service
        )


        self.btn_stop = QPushButton(
            "■  停止服务"
        )

        self.btn_stop.setMinimumHeight(
            45
        )

        self.btn_stop.setEnabled(
            False
        )

        self.btn_stop.setStyleSheet(
            self.danger_button()
        )

        self.btn_stop.clicked.connect(
            self.stop_service
        )


        buttons.addWidget(
            self.btn_start
        )

        buttons.addWidget(
            self.btn_stop
        )


        control_layout.addLayout(
            buttons
        )


        left.addWidget(
            control_card
        )


        main_area.addLayout(
            left,
            3
        )


        # ====================================================
        # 右侧二维码
        # ====================================================

        qr_card = QFrame()

        qr_card.setStyleSheet(
            self.card_style()
        )


        qr_layout = QVBoxLayout(
            qr_card
        )

        qr_layout.setContentsMargins(
            22,20,22,20
        )

        qr_layout.setSpacing(
            10
        )


        qr_title = QLabel(
            "📱  手机扫码连接"
        )

        qr_title.setAlignment(
            Qt.AlignCenter
        )

        qr_title.setStyleSheet("""

        QLabel{

            font-size:17px;

            font-weight:800;

            color:#28627F;

        }

        """)


        qr_layout.addWidget(
            qr_title
        )


        qr_desc = QLabel(
            "手机与电脑连接同一 Wi‑Fi / 热点"
        )

        qr_desc.setAlignment(
            Qt.AlignCenter
        )

        qr_desc.setStyleSheet("""

        QLabel{

            color:#8BA8B9;

            font-size:15px;

        }

        """)


        qr_layout.addWidget(
            qr_desc
        )


        self.qr_label = QLabel()

        self.qr_label.setFixedSize(
            250,
            250
        )

        self.qr_label.setAlignment(
            Qt.AlignCenter
        )

        self.qr_label.setStyleSheet("""

        QLabel{

            background:white;

            border:
            8px solid white;

            border-radius:18px;

        }

        """)


        qr_layout.addWidget(
            self.qr_label,
            alignment=Qt.AlignCenter
        )


        self.qr_url = QLabel(
            "启动服务后自动生成"
        )

        self.qr_url.setAlignment(
            Qt.AlignCenter
        )

        self.qr_url.setWordWrap(
            True
        )

        self.qr_url.setStyleSheet("""

        QLabel{

            color:#188BD0;

            font-size:15px;

            font-weight:bold;

            background:#EDF9FF;

            border-radius:10px;

            padding:9px;

        }

        """)


        qr_layout.addWidget(
            self.qr_url
        )


        main_area.addWidget(
            qr_card,
            2
        )


        content_layout.addLayout(
            main_area,
            stretch=1
        )


        # ====================================================
        # 日志
        # ====================================================

        log_card = QFrame()

        log_card.setStyleSheet(
            self.card_style()
        )


        log_layout = QVBoxLayout(
            log_card
        )

        log_layout.setContentsMargins(
            18,14,18,14
        )


        log_header = QHBoxLayout()


        log_title = QLabel(
            "📋  运行日志"
        )

        log_title.setStyleSheet("""

        QLabel{

            font-size:14px;

            font-weight:700;

            color:#28627F;

        }

        """)


        log_header.addWidget(
            log_title
        )


        log_header.addStretch()


        self.log_state = QLabel(
            "● READY"
        )

        self.log_state.setStyleSheet("""

        QLabel{

            color:#58A9D7;

            font-size:12px;

            font-weight:bold;

        }

        """)


        log_header.addWidget(
            self.log_state
        )


        log_layout.addLayout(
            log_header
        )


        self.log_text = QTextEdit()

        self.log_text.setReadOnly(
            True
        )

        self.log_text.setMinimumHeight(
            105
        )

        self.log_text.setStyleSheet("""

        QTextEdit{

            background:#F5FBFE;

            border:
            1px solid #DCEEF7;

            border-radius:12px;

            padding:10px;

            color:#4D7389;

            font-family:
            "Consolas",
            "Microsoft YaHei";

            font-size:13px;

        }

        """)


        log_layout.addWidget(
            self.log_text
        )


        content_layout.addWidget(
            log_card
        )


        # ====================================================
        # 底部
        # ====================================================

        footer = QLabel(
            "☁ LAN Image Transfer   •   本地局域网安全传输   •   Port 8888"
        )

        footer.setAlignment(
            Qt.AlignCenter
        )

        footer.setStyleSheet("""

        QLabel{

            color:#9AB7C8;

            font-size:12px;

        }

        """)


        content_layout.addWidget(
            footer
        )


    # ========================================================
    # 卡片
    # ========================================================

    def create_info_card(
        self,
        icon,
        title,
        value
    ):

        card = QFrame()

        card.setMinimumHeight(
            78
        )

        card.setStyleSheet("""

        QFrame{

            background:white;

            border:
            1px solid #E1F1F8;

            border-radius:17px;

        }

        """)


        layout = QHBoxLayout(
            card
        )

        layout.setContentsMargins(
            15,12,15,12
        )


        icon_label = QLabel(
            icon
        )

        icon_label.setFixedSize(
            42,
            42
        )

        icon_label.setAlignment(
            Qt.AlignCenter
        )

        icon_label.setStyleSheet("""

        QLabel{

            background:#EAF8FF;

            border-radius:13px;

            color:#24A2E6;

            font-size:20px;

        }

        """)


        layout.addWidget(
            icon_label
        )


        text_layout = QVBoxLayout()

        text_layout.setSpacing(
            2
        )


        title_label = QLabel(
            title
        )

        title_label.setStyleSheet("""

        QLabel{

            color:#8BA6B6;

            font-size:12px;

        }

        """)


        value_label = QLabel(
            value
        )

        value_label.setStyleSheet("""

        QLabel{

            color:#27749A;

            font-size:15px;

            font-weight:800;

        }

        """)


        text_layout.addWidget(
            title_label
        )

        text_layout.addWidget(
            value_label
        )


        layout.addLayout(
            text_layout
        )


        card.value_label = value_label

        card.icon_label = icon_label


        return card


    # ========================================================
    # 卡片样式
    # ========================================================

    def card_style(self):

        return """

        QFrame{

            background:white;

            border:
            1px solid #E1F1F8;

            border-radius:18px;

        }

        """


    # ========================================================
    # 主按钮
    # ========================================================

    def primary_button(self):

        return """

        QPushButton{

            background:
            qlineargradient(
                x1:0,y1:0,
                x2:1,y2:1,
                stop:0 #53C6FF,
                stop:1 #168FDF
            );

            color:white;

            border:none;

            border-radius:12px;

            font-size:13px;

            font-weight:700;

        }

        QPushButton:hover{

            background:#28A7EB;

        }

        QPushButton:pressed{

            background:#147FC6;

        }

        QPushButton:disabled{

            background:#B9D9E9;

        }

        """


    # ========================================================
    # 次按钮
    # ========================================================

    def secondary_button(self):

        return """

        QPushButton{

            background:#EAF7FD;

            color:#2186B5;

            border:
            1px solid #CBEAF7;

            border-radius:11px;

            padding:9px;

            font-size:12px;

            font-weight:600;

        }

        QPushButton:hover{

            background:#DDF2FC;

            border-color:#9ED7F2;

        }

        """


    # ========================================================
    # 警告按钮
    # ========================================================

    def danger_button(self):

        return """

        QPushButton{

            background:#FFF1F1;

            color:#D35D5D;

            border:
            1px solid #FFD6D6;

            border-radius:12px;

            font-size:13px;

            font-weight:700;

        }

        QPushButton:hover{

            background:#FFE4E4;

        }

        QPushButton:disabled{

            color:#B7C4CA;

            background:#F5F8FA;

        }

        """


    # ========================================================
    # 拖动窗口
    # ========================================================

    def mouse_press_event(
        self,
        event
    ):

        if event.button() == Qt.LeftButton:

            self._drag_pos = (
                event.globalPos()
                -
                self.frameGeometry().topLeft()
            )


    def mouse_move_event(
        self,
        event
    ):

        if (
            event.buttons()
            &
            Qt.LeftButton
        ):

            self.move(
                event.globalPos()
                -
                self._drag_pos
            )


    # ========================================================
    # 二维码
    # ========================================================

    def generate_qr(
        self,
        ip
    ):

        url = (
            f"http://{ip}:8888"
        )


        qr = qrcode.QRCode(
            border=2,
            box_size=8
        )


        qr.add_data(
            url
        )

        qr.make(
            fit=True
        )


        img = qr.make_image(
            fill_color="#164D6B",
            back_color="white"
        )


        bio = BytesIO()

        img.save(
            bio,
            format="PNG"
        )


        bio.seek(0)


        pix = QPixmap()

        pix.loadFromData(
            bio.getvalue()
        )


        self.qr_label.setPixmap(
            pix.scaled(
                230,
                230,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )


        self.qr_url.setText(
            f"🌐 {url}"
        )


    # ========================================================
    # 刷新 IP
    # ========================================================

    def refresh_ip(self):

        ip_list = \
            get_local_hotspot_ips()


        if not ip_list:

            self.edit_ip.setText(
                "未检测到局域网地址"
            )

            self.ip_card.value_label.setText(
                "未检测到"
            )

            self.qr_label.clear()

            self.qr_label.setText(
                "暂无可用地址"
            )

            self.qr_url.setText(
                "请连接 Wi‑Fi / 手机热点"
            )


            self.append_log(
                "⚠ 未检测到有效局域网 IP"
            )

            return


        show_str = \
            "  |  ".join(
                ip_list
            )


        self.edit_ip.setText(
            show_str
        )


        self.ip_card.value_label.setText(
            ip_list[0]
        )


        self.generate_qr(
            ip_list[0]
        )


        self.append_log(
            "✓ 检测到局域网地址："
            +
            show_str
        )


    # ========================================================
    # 选择目录
    # ========================================================

    def select_folder(self):

        path = \
            QFileDialog.getExistingDirectory(
                self,
                "选择图片保存文件夹"
            )


        if path:

            STATE.save_dir = path


            os.makedirs(
                STATE.save_dir,
                exist_ok=True
            )


            self.edit_dir.setText(
                path
            )


            self.append_log(
                "📂 保存目录："
                +
                path
            )


    # ========================================================
    # 启动
    # ========================================================

    def start_service(self):

        if STATE.is_running:

            self.append_log(
                "⚠ 服务已经运行"
            )

            return


        STATE.flask_thread = \
            threading.Thread(
                target=run_flask_server,
                daemon=True
            )


        STATE.flask_thread.start()


        self.btn_start.setEnabled(
            False
        )

        self.btn_stop.setEnabled(
            True
        )


        self.refresh_ip()


        self.append_log(
            "✓ 正在启动局域网 HTTP 服务..."
        )


        # 延迟提示
        QTimer.singleShot(
            800,
            lambda:
            self.append_log(
                "✓ 手机与电脑连接同一网络即可扫码上传"
            )
        )


    # ========================================================
    # 停止
    # ========================================================

    def stop_service(self):

        # Flask 原生 app.run 没有直接 shutdown
        # 保持原项目行为，提示用户关闭程序

        self.btn_start.setEnabled(
            True
        )

        self.btn_stop.setEnabled(
            False
        )


        STATE.is_running = False


        self.update_service_status(
            False
        )


        self.append_log(
            "● 已停止服务状态"
        )


        self.append_log(
            "提示：Flask 后台线程可能仍保持监听，彻底停止请关闭程序"
        )


    # ========================================================
    # 服务状态
    # ========================================================

    def update_service_status(
        self,
        running
    ):

        if running:

            self.status_card.value_label.setText(
                "● 运行中"
            )

            self.status_card.value_label.setStyleSheet("""

            QLabel{

                color:#24A96A;

                font-size:15px;

                font-weight:800;

            }

            """)


            self.status_card.icon_label.setStyleSheet("""

            QLabel{

                background:#E8FAF1;

                border-radius:13px;

                color:#22A56A;

                font-size:20px;

            }

            """)


            self.log_state.setText(
                "● ONLINE"
            )

            self.log_state.setStyleSheet("""

            QLabel{

                color:#28A76B;

                font-size:12px;

                font-weight:bold;

            }

            """)

        else:

            self.status_card.value_label.setText(
                "● 未启动"
            )

            self.status_card.value_label.setStyleSheet("""

            QLabel{

                color:#8AA5B5;

                font-size:15px;

                font-weight:800;

            }

            """)


            self.status_card.icon_label.setStyleSheet("""

            QLabel{

                background:#EDF7FB;

                border-radius:13px;

                color:#66A5C5;

                font-size:20px;

            }

            """)


            self.log_state.setText(
                "● OFFLINE"
            )

            self.log_state.setStyleSheet("""

            QLabel{

                color:#9DB5C3;

                font-size:13px;

                font-weight:bold;

            }

            """)


    # ========================================================
    # 上传数量
    # ========================================================

    def update_upload_count(self):

        self.count_card.value_label.setText(
            f"{STATE.upload_count} 张"
        )


    # ========================================================
    # 日志
    # ========================================================

    def append_log(
        self,
        text
    ):

        now = time.strftime(
            "%H:%M:%S"
        )


        self.log_text.append(
            f"<span style='color:#8DB3C7'>"
            f"[{now}]"
            f"</span> "
            f"{text}"
        )


        scrollbar = \
            self.log_text.verticalScrollBar()


        scrollbar.setValue(
            scrollbar.maximum()
        )


    # ========================================================
    # 状态刷新
    # ========================================================

    def refresh_status(self):

        self.update_service_status(
            STATE.is_running
        )


    # ========================================================
    # 关闭
    # ========================================================

    def closeEvent(
        self,
        event
    ):

        STATE.is_running = False

        event.accept()


# ============================================================
# 程序入口
# ============================================================

if __name__ == "__main__":

    app_qt = QApplication(
        sys.argv
    )


    app_qt.setApplicationName(
        "天空蓝局域网图片传输"
    )


    # 全局字体

    font = QFont(
        "Microsoft YaHei"
    )

    font.setPointSize(
        10
    )

    app_qt.setFont(
        font
    )


    main_win = MainWindow()


    main_win.show()


    sys.exit(
        app_qt.exec_()
    )
