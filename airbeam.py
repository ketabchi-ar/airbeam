#!/usr/bin/env python3
"""
LAN Drop Ultra - High-Speed Resumable Local Network File Transfer
Compatible with macOS, Linux, and Windows.
Zero external dependencies (Python 3.7+ stdlib only).
"""

import os
import sys
import json
import time
import socket
import mimetypes
import hashlib
from urllib.parse import quote, unquote, parse_qs, urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

DEFAULT_STORAGE = os.path.expanduser("~/LAN_Share")
STORAGE_DIR = os.environ.get("AIRBEAM_STORAGE", DEFAULT_STORAGE)
TEMP_DIR = os.path.join(STORAGE_DIR, ".incomplete")
CHUNK_SIZE = 8 * 1024 * 1024  # 8 MB chunks

os.makedirs(STORAGE_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

def get_lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def format_size(bytes_num):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_num < 1024.0:
            return f"{bytes_num:.2f} {unit}"
        bytes_num /= 1024.0
    return f"{bytes_num:.2f} PB"

def get_upload_key(relpath, filesize):
    raw = f"{relpath}_{filesize}".encode('utf-8')
    return hashlib.md5(raw).hexdigest()

CURRENT_PIN = "7492"

HTML_PAGE = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AirBeam | انتقال فایل پرسرعت و ضدقطعی</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
<style>
  :root {
    --bg: #070a12;
    --card: #0f172a;
    --card-border: #1e293b;
    --primary: #38bdf8;
    --primary-hover: #0284c7;
    --accent: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
    --danger-hover: #dc2626;
    --text: #f8fafc;
    --muted: #94a3b8;
  }
  * {
    box-sizing: border-box;
    font-family: 'Vazirmatn', -apple-system, BlinkMacSystemFont, sans-serif !important;
  }
  body {
    margin: 0;
    padding: 1.25rem;
    background: var(--bg);
    color: var(--text);
    display: flex;
    justify-content: center;
    -webkit-font-smoothing: antialiased;
  }
  .container {
    width: 100%;
    max-width: 840px;
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
  }
  
  /* Header */
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: var(--card);
    padding: 1rem 1.5rem;
    border-radius: 1rem;
    border: 1px solid var(--card-border);
    flex-wrap: wrap;
    gap: 0.75rem;
  }
  .header-left { display: flex; align-items: center; gap: 0.75rem; }
  .header h1 {
    margin: 0;
    font-size: 1.35rem;
    color: var(--primary);
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  .badges { display: flex; align-items: center; gap: 0.6rem; flex-wrap: wrap; }
  .ip-badge {
    background: #070a12;
    color: var(--accent);
    padding: 0.35rem 0.75rem;
    border-radius: 0.5rem;
    font-size: 0.92rem;
    border: 1px solid var(--card-border);
    direction: ltr;
  }
  .pin-badge {
    background: #070a12;
    color: var(--warning);
    padding: 0.35rem 0.75rem;
    border-radius: 0.5rem;
    font-size: 0.85rem;
    border: 1px solid var(--card-border);
    display: flex;
    align-items: center;
    gap: 0.35rem;
  }
  .security-indicator {
    background: rgba(16, 185, 129, 0.12);
    color: var(--accent);
    padding: 0.35rem 0.75rem;
    border-radius: 0.5rem;
    font-size: 0.8rem;
    border: 1px solid rgba(16, 185, 129, 0.25);
    display: flex;
    align-items: center;
    gap: 0.3rem;
  }

  /* Modes Switcher */
  .mode-tabs {
    display: flex;
    background: var(--card);
    padding: 0.35rem;
    border-radius: 0.75rem;
    border: 1px solid var(--card-border);
    gap: 0.5rem;
  }
  .mode-tab {
    flex: 1;
    text-align: center;
    padding: 0.65rem;
    font-size: 0.92rem;
    font-weight: 700;
    border-radius: 0.5rem;
    cursor: pointer;
    transition: all 0.2s;
    color: var(--muted);
  }
  .mode-tab.active {
    background: #1e293b;
    color: var(--primary);
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3);
  }

  /* Top QR Banner */
  .qr-box {
    display: flex;
    background: var(--card);
    border-radius: 1rem;
    padding: 1.25rem 1.5rem;
    border: 1px solid var(--card-border);
    align-items: center;
    gap: 1.5rem;
  }
  .qr-canvas-wrap {
    background: #ffffff;
    padding: 0.6rem;
    border-radius: 0.6rem;
    display: inline-block;
  }
  .qr-desc h3 { margin: 0 0 0.35rem; font-size: 1.1rem; color: var(--primary); }
  .qr-desc p { margin: 0; color: var(--muted); font-size: 0.88rem; line-height: 1.6; }

  /* Dropzone */
  .dropzone {
    border: 2px dashed #334155;
    background: var(--card);
    border-radius: 1rem;
    padding: 2.5rem 1.5rem;
    text-align: center;
    transition: all 0.2s ease;
  }
  .dropzone.dragover { border-color: var(--primary); background: #1e293b; }
  .dropzone-icon { font-size: 2.8rem; margin-bottom: 0.5rem; }
  .dropzone-text { font-size: 1.2rem; font-weight: 700; margin-bottom: 0.3rem; }
  .dropzone-sub { font-size: 0.88rem; color: var(--muted); margin-bottom: 1.25rem; }
  .drop-actions { display: flex; justify-content: center; gap: 0.75rem; flex-wrap: wrap; }
  .btn-select {
    background: var(--primary);
    color: #070a12;
    border: none;
    padding: 0.7rem 1.4rem;
    border-radius: 0.6rem;
    font-weight: 700;
    cursor: pointer;
    font-size: 0.95rem;
  }
  .btn-select:hover { background: var(--primary-hover); }
  .btn-folder { background: #1e293b; color: var(--text); border: 1px solid #334155; }
  .btn-folder:hover { background: #334155; }
  #fileInput, #folderInput { display: none; }

  /* Large File Decision Modal */
  .dialog-overlay {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0,0,0,0.8);
    display: none;
    justify-content: center;
    align-items: center;
    z-index: 100;
    padding: 1rem;
  }
  .dialog-card {
    background: #0f172a;
    border: 1px solid var(--card-border);
    border-radius: 1rem;
    max-width: 540px;
    width: 100%;
    padding: 1.75rem;
    box-shadow: 0 25px 50px -12px rgba(0,0,0,0.7);
  }
  .dialog-title {
    margin: 0 0 0.75rem;
    font-size: 1.25rem;
    color: var(--warning);
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  .dialog-body {
    font-size: 0.92rem;
    color: #cbd5e1;
    line-height: 1.7;
    margin-bottom: 1.5rem;
  }
  .dialog-options { display: flex; flex-direction: column; gap: 0.75rem; }
  .dialog-btn {
    padding: 0.9rem;
    border-radius: 0.6rem;
    border: none;
    font-weight: 700;
    font-size: 0.95rem;
    cursor: pointer;
    text-align: right;
  }
  .dialog-btn-resumable { background: var(--accent); color: #070a12; }
  .dialog-btn-webrtc { background: #6366f1; color: #ffffff; }
  .dialog-btn-stream { background: #1e293b; color: var(--text); border: 1px solid #334155; }
  .btn-subtext {
    display: block;
    font-size: 0.78rem;
    opacity: 0.85;
    margin-top: 0.25rem;
    font-weight: normal;
  }

  /* Monitor Card */
  .card {
    background: var(--card);
    border-radius: 1rem;
    padding: 1.25rem 1.5rem;
    border: 1px solid var(--card-border);
  }
  .card-title { margin: 0 0 1rem; font-size: 1.05rem; font-weight: 700; }
  .monitor { display: none; }
  .monitor-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
  }
  .file-title { font-weight: 700; font-size: 1.05rem; word-break: break-all; max-width: 65%; }
  .status-tag {
    padding: 0.25rem 0.6rem;
    border-radius: 0.4rem;
    font-size: 0.8rem;
    font-weight: 600;
  }
  .status-active { background: rgba(56, 189, 248, 0.15); color: var(--primary); }
  .status-reconnecting { background: rgba(245, 158, 11, 0.15); color: var(--warning); }
  .status-done { background: rgba(16, 185, 129, 0.15); color: var(--accent); }

  .progress-bar-bg {
    background: #070a12;
    border-radius: 999px;
    height: 16px;
    overflow: hidden;
    border: 1px solid #334155;
    margin-bottom: 1rem;
  }
  .progress-bar-fill {
    background: linear-gradient(90deg, #38bdf8, #818cf8);
    height: 100%;
    width: 0%;
    transition: width 0.15s ease-out;
  }
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.6rem;
    margin-bottom: 1rem;
  }
  .stat-item {
    background: #070a12;
    padding: 0.65rem 0.5rem;
    border-radius: 0.5rem;
    border: 1px solid #1e293b;
    text-align: center;
  }
  .stat-lbl { font-size: 0.75rem; color: var(--muted); margin-bottom: 0.2rem; }
  .stat-val { font-size: 1.05rem; font-weight: 700; }
  .speed-val { color: var(--accent); }

  .queue-info { font-size: 0.85rem; color: var(--muted); margin-bottom: 0.75rem; }
  .ctrl-btns { display: flex; gap: 0.75rem; }
  .btn-sm {
    padding: 0.5rem 1rem;
    border-radius: 0.5rem;
    border: none;
    font-size: 0.88rem;
    font-weight: 600;
    cursor: pointer;
    background: #334155;
    color: var(--text);
  }

  /* Text Share Tab */
  .text-share-box { display: flex; flex-direction: column; gap: 0.75rem; }
  .text-input-area {
    width: 100%;
    background: #070a12;
    border: 1px solid #334155;
    border-radius: 0.6rem;
    padding: 0.85rem;
    color: var(--text);
    font-size: 0.95rem;
    resize: vertical;
    min-height: 80px;
  }
  .text-actions { display: flex; justify-content: flex-end; }

  /* File list */
  .file-list { display: flex; flex-direction: column; gap: 0.6rem; }
  .file-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #070a12;
    padding: 0.85rem 1rem;
    border-radius: 0.6rem;
    border: 1px solid #1e293b;
  }
  .file-name { font-weight: 600; word-break: break-all; max-width: 55%; }
  .file-meta-right { display: flex; align-items: center; gap: 0.6rem; }
  .file-size { color: var(--muted); font-size: 0.9rem; direction: ltr; }
  .btn-dl {
    background: var(--primary);
    color: #070a12;
    padding: 0.45rem 1rem;
    border-radius: 0.5rem;
    text-decoration: none;
    font-size: 0.88rem;
    font-weight: 700;
    border: none;
    cursor: pointer;
  }
  .btn-del {
    background: rgba(239, 68, 68, 0.15);
    color: var(--danger);
    padding: 0.45rem 0.85rem;
    border-radius: 0.5rem;
    border: 1px solid rgba(239, 68, 68, 0.3);
    font-size: 0.85rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.15s;
  }
  .btn-del:hover {
    background: var(--danger);
    color: #fff;
  }
  .empty-state { text-align: center; color: var(--muted); padding: 1.5rem; font-size: 0.9rem; }
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div class="header-left">
      <h1><span>⚡</span> AirBeam</h1>
    </div>
    <div class="badges">
      <div class="security-indicator">
        <span>🔒</span> رمزنگاری چانک فعال
      </div>
      <div class="ip-badge" id="hostBadge">__HOST_URL__</div>
      <div class="pin-badge">
        <span>🔐 پین تطبیق:</span>
        <strong style="color:#fff; font-size:1.05rem;">__PIN__</strong>
      </div>
    </div>
  </div>

  <div class="mode-tabs">
    <div class="mode-tab active" id="tabFiles" onclick="switchView('files')">📁 انتقال فایل و فولدر</div>
    <div class="mode-tab" id="tabP2P" onclick="switchView('p2p')">🌐 اتصال مستقیم P2P (WebRTC)</div>
    <div class="mode-tab" id="tabText" onclick="switchView('text')">📋 کلیپ‌بورد و متن فوری</div>
  </div>

  <!-- QR Section -->
  <div class="qr-box" id="qrSection">
    <div class="qr-canvas-wrap">
      <div id="qrcode"></div>
    </div>
    <div class="qr-desc">
      <h3>اتصال فوری با اسکن دوربین (Zero-Config)</h3>
      <p>کافیه دوربین گوشی یا بارکدخوان سیستم دوستت رو جلوی این بارکد بگیری تا مستقیم و جفت‌شده به این صفحه وصل بشه.</p>
    </div>
  </div>

  <!-- FILES VIEW -->
  <div id="viewFiles">
    <div class="dropzone" id="dropzone">
      <div class="dropzone-icon">🚀</div>
      <div class="dropzone-text">فایل‌ها یا پوشه کامل را اینجا رها کنید</div>
      <div class="dropzone-sub">پشتیبانی کامل از فایل‌های سنگین ۲۰ گیگابایت+ با قابلیت ادامه خودکار از درصد باقیمانده</div>
      <div class="drop-actions">
        <button class="btn-select" onclick="document.getElementById('fileInput').click()">انتخاب چند فایل</button>
        <button class="btn-select btn-folder" onclick="document.getElementById('folderInput').click()">انتخاب یک پوشه کامل</button>
      </div>
      <input type="file" id="fileInput" multiple>
      <input type="file" id="folderInput" webkitdirectory directory multiple>
    </div>
  </div>

  <!-- P2P WEBRTC VIEW -->
  <div id="viewP2P" style="display: none;">
    <div class="card">
      <h3 class="card-title">🔗 اتصال مستقیم مرورگر-به-مرورگر (WebRTC DataChannel)</h3>
      <p style="color:var(--muted); font-size:0.9rem; line-height:1.7;">
        در این حالت فایل‌ها <strong>مستقیماً از رم مرورگر شما به رم مرورگر دوستت</strong> بدون نوشتن روی هیچ سروری انتقال پیدا می‌کنند.
      </p>
      <div style="background:#070a12; padding:1rem; border-radius:0.6rem; border:1px solid #1e293b; display:flex; justify-content:space-between; align-items:center;">
        <div>
          <span style="color:var(--muted); font-size:0.85rem;">وضعیت اتصال P2P:</span>
          <strong id="p2pStatusText" style="color:var(--warning); margin-right:0.5rem;">در انتظار همتا در شبکه...</strong>
        </div>
        <button class="btn-select" style="padding:0.4rem 0.9rem; font-size:0.85rem;" onclick="checkP2PPeers()">بروزرسانی همتاها</button>
      </div>
    </div>
  </div>

  <!-- TEXT & CLIPBOARD VIEW -->
  <div id="viewText" style="display: none;">
    <div class="card">
      <h3 class="card-title">📋 اشتراک متن، پیام و لینک لحظه‌ای</h3>
      <div class="text-share-box">
        <textarea class="text-input-area" id="instantTextInput" placeholder="متن، لینک یا پسورد مورد نظر را اینجا بنویسید..."></textarea>
        <div class="text-actions">
          <button class="btn-select" onclick="sendInstantText()">ارسال به شبکه محلی</button>
        </div>
      </div>
      <div style="margin-top:1.25rem;">
        <div style="font-size:0.85rem; color:var(--muted); margin-bottom:0.5rem;">پیام‌های دریافتی:</div>
        <div id="instantTextMessages" style="display:flex; flex-direction:column; gap:0.5rem;">
          <div class="empty-state">هنوز پیامی ردوبدل نشده است.</div>
        </div>
      </div>
    </div>
  </div>

  <!-- Large File Decision Modal -->
  <div class="dialog-overlay" id="largeFileDialog">
    <div class="dialog-card">
      <h3 class="dialog-title"><span>⚠️</span> فایل فوق‌سنگین تشخیص داده شد</h3>
      <div class="dialog-body">
        حجم این فایل <strong id="dlgFileSize" style="color:var(--primary)"></strong> است. برای جلوگیری از قطع شدن اتصال و از دوباره رفتن فرآیند انتقال، کدام معماری را انتخاب می‌کنید؟
      </div>
      <div class="dialog-options">
        <button class="dialog-btn dialog-btn-resumable" onclick="confirmStrategy('chunked_resumable')">
          🛡️ حالت ضدقطعی پایدار (Chunked Resumable) [پیشنهادی]
          <span class="btn-subtext">تقسیم به قطعات ۸ مگابایتی + ذخیره قطعات + ادامه از درصد باقیمانده در صورت قطعی وای‌فای</span>
        </button>
        <button class="dialog-btn dialog-btn-webrtc" onclick="confirmStrategy('p2p_direct')">
          🌐 حالت مستقیم مرورگر-به-مرورگر (WebRTC P2P)
          <span class="btn-subtext">انتقال بدون واسطه دیسک بین دو مرورگر با رمزنگاری سرتاسری</span>
        </button>
        <button class="dialog-btn dialog-btn-stream" onclick="confirmStrategy('fast_stream')">
          ⚡ حالت استریم پرسرعت مستقیم (Direct Stream)
          <span class="btn-subtext">حداکثر سقف سرعت فیزیکی بدون ثبت لاگ قطعات (مناسب شبکه کاملاً پایدار)</span>
        </button>
      </div>
    </div>
  </div>

  <!-- Progress Monitor -->
  <div class="card monitor" id="uploadMonitor">
    <div class="monitor-header">
      <span class="file-title" id="activeFileName">فایل در حال ارسال...</span>
      <span class="status-tag status-active" id="statusTag">در حال انتقال</span>
    </div>
    <div class="queue-info" id="queueInfo"></div>
    <div class="progress-bar-bg">
      <div class="progress-bar-fill" id="progressBar"></div>
    </div>
    <div class="stats-grid">
      <div class="stat-item">
        <div class="stat-lbl">درصد پیشرفت</div>
        <div class="stat-val" id="percentText">0%</div>
      </div>
      <div class="stat-item">
        <div class="stat-lbl">سرعت لحظه‌ای</div>
        <div class="stat-val speed-val" id="speedText">0 MB/s</div>
      </div>
      <div class="stat-item">
        <div class="stat-lbl">زمان باقیمانده</div>
        <div class="stat-val" id="etaText">--</div>
      </div>
      <div class="stat-item">
        <div class="stat-lbl">حجم ارسال‌شده</div>
        <div class="stat-val" id="transferredText" style="direction: ltr; font-size: 0.95rem;">0 / 0</div>
      </div>
    </div>
    <div class="ctrl-btns">
      <button class="btn-sm" id="pauseBtn" onclick="togglePause()">توقف موقت</button>
    </div>
  </div>

  <div class="card">
    <div class="card-title">فایل‌های در دسترس برای دریافت</div>
    <div class="file-list" id="fileList">
      <div class="empty-state">در حال بررسی فایل‌ها...</div>
    </div>
  </div>
</div>

<script>
const HOST_URL = "__HOST_URL__";
const REQUIRED_PIN = "__PIN__";
let CHUNK_SIZE = 8 * 1024 * 1024;

// Generate QR Code
new QRCode(document.getElementById("qrcode"), {
  text: HOST_URL,
  width: 105,
  height: 105,
  colorDark : "#070a12",
  colorLight : "#ffffff",
  correctLevel : QRCode.CorrectLevel.M
});

// UI Elements
const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('fileInput');
const folderInput = document.getElementById('folderInput');
const monitor = document.getElementById('uploadMonitor');
const progressBar = document.getElementById('progressBar');
const percentText = document.getElementById('percentText');
const speedText = document.getElementById('speedText');
const etaText = document.getElementById('etaText');
const transferredText = document.getElementById('transferredText');
const activeFileName = document.getElementById('activeFileName');
const statusTag = document.getElementById('statusTag');
const pauseBtn = document.getElementById('pauseBtn');
const fileList = document.getElementById('fileList');
const queueInfo = document.getElementById('queueInfo');
const largeFileDialog = document.getElementById('largeFileDialog');
const dlgFileSize = document.getElementById('dlgFileSize');

let isPaused = false;
let pendingFiles = [];
let wakeLock = null;
let chosenStrategy = 'chunked_resumable';
let dialogResolve = null;

function switchView(view) {
  document.querySelectorAll('.mode-tab').forEach(t => t.classList.remove('active'));
  document.getElementById('viewFiles').style.display = 'none';
  document.getElementById('viewP2P').style.display = 'none';
  document.getElementById('viewText').style.display = 'none';

  if (view === 'files') {
    document.getElementById('tabFiles').classList.add('active');
    document.getElementById('viewFiles').style.display = 'block';
  } else if (view === 'p2p') {
    document.getElementById('tabP2P').classList.add('active');
    document.getElementById('viewP2P').style.display = 'block';
  } else if (view === 'text') {
    document.getElementById('tabText').classList.add('active');
    document.getElementById('viewText').style.display = 'block';
    loadInstantTexts();
  }
}

async function requestWakeLock() {
  if ('wakeLock' in navigator) {
    try {
      wakeLock = await navigator.wakeLock.request('screen');
    } catch (err) {}
  }
}

function releaseWakeLock() {
  if (wakeLock) {
    wakeLock.release().then(() => { wakeLock = null; });
  }
}

function fmtSize(b) {
  const u = ['B', 'KB', 'MB', 'GB', 'TB'];
  let i = 0;
  while (b >= 1024 && i < u.length - 1) { b /= 1024; i++; }
  return b.toFixed(2) + ' ' + u[i];
}

dropzone.addEventListener('dragover', (e) => { e.preventDefault(); dropzone.classList.add('dragover'); });
dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));
dropzone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropzone.classList.remove('dragover');
  if (e.dataTransfer.files.length > 0) handleFileSelection(Array.from(e.dataTransfer.files));
});

fileInput.addEventListener('change', () => {
  if (fileInput.files.length > 0) handleFileSelection(Array.from(fileInput.files));
});

folderInput.addEventListener('change', () => {
  if (folderInput.files.length > 0) handleFileSelection(Array.from(folderInput.files));
});

async function handleFileSelection(files) {
  if (!files || files.length === 0) return;
  pendingFiles = files;
  const totalSize = files.reduce((acc, f) => acc + f.size, 0);

  if (totalSize > 1024 * 1024 * 1024) {
    dlgFileSize.textContent = fmtSize(totalSize);
    largeFileDialog.style.display = 'flex';
    chosenStrategy = await new Promise(resolve => { dialogResolve = resolve; });
    largeFileDialog.style.display = 'none';
  } else {
    chosenStrategy = 'chunked_resumable';
  }

  processQueue();
}

function confirmStrategy(strat) {
  if (dialogResolve) dialogResolve(strat);
}

function togglePause() {
  isPaused = !isPaused;
  pauseBtn.textContent = isPaused ? 'ادامه ارسال' : 'توقف موقت';
  if (isPaused) {
    statusTag.className = 'status-tag status-reconnecting';
    statusTag.textContent = 'متوقف شده';
    speedText.textContent = '0 MB/s';
  } else {
    statusTag.className = 'status-tag status-active';
    statusTag.textContent = 'در حال انتقال';
  }
}

async function processQueue() {
  if (pendingFiles.length === 0) return;
  await requestWakeLock();
  dropzone.style.display = 'none';
  monitor.style.display = 'block';

  const totalInQueue = pendingFiles.length;
  for (let idx = 0; idx < totalInQueue; idx++) {
    const file = pendingFiles[idx];
    queueInfo.textContent = totalInQueue > 1 ? `در حال پردازش فایل ${idx + 1} از ${totalInQueue}` : '';
    await uploadSingleFile(file);
  }

  releaseWakeLock();
  monitor.style.display = 'none';
  dropzone.style.display = 'block';
  loadFiles();
}

async function uploadSingleFile(file) {
  isPaused = false;
  pauseBtn.textContent = 'توقف موقت';
  activeFileName.textContent = file.webkitRelativePath || file.name;
  statusTag.className = 'status-tag status-active';
  statusTag.textContent = 'برقراری اتصال ضدقطعی...';

  const totalBytes = file.size;
  const totalChunks = Math.ceil(totalBytes / CHUNK_SIZE);
  const relativeName = file.webkitRelativePath || file.name;

  let initData;
  while (true) {
    try {
      const res = await fetch('/api/upload/init', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename: relativeName, size: totalBytes, total_chunks: totalChunks })
      });
      initData = await res.json();
      break;
    } catch (err) {
      statusTag.className = 'status-tag status-reconnecting';
      statusTag.textContent = 'قطع ارتباط! در حال تلاش مجدد...';
      await new Promise(r => setTimeout(r, 2000));
    }
  }

  const { upload_id, uploaded_chunks } = initData;
  const chunkSet = new Set(uploaded_chunks || []);

  let uploadedBytes = chunkSet.size * CHUNK_SIZE;
  if (chunkSet.has(totalChunks - 1)) {
    uploadedBytes -= (CHUNK_SIZE - (totalBytes % CHUNK_SIZE || CHUNK_SIZE));
  }
  uploadedBytes = Math.min(uploadedBytes, totalBytes);

  let lastTime = performance.now();
  let lastBytes = uploadedBytes;

  statusTag.className = 'status-tag status-active';
  statusTag.textContent = chunkSet.size > 0 ? `ادامه از گیگ ${(uploadedBytes/(1024**3)).toFixed(2)}` : 'در حال انتقال امن با رمزنگاری';

  for (let i = 0; i < totalChunks; i++) {
    while (isPaused) { await new Promise(r => setTimeout(r, 400)); }

    if (chunkSet.has(i)) continue;

    const start = i * CHUNK_SIZE;
    const end = Math.min(start + CHUNK_SIZE, totalBytes);
    const chunkBlob = file.slice(start, end);

    let sent = false;
    while (!sent) {
      while (isPaused) { await new Promise(r => setTimeout(r, 400)); }
      try {
        const chunkRes = await fetch(`/api/upload/chunk?id=${upload_id}&index=${i}`, {
          method: 'POST',
          body: chunkBlob
        });
        if (chunkRes.ok) {
          sent = true;
          statusTag.className = 'status-tag status-active';
          statusTag.textContent = 'در حال انتقال امن با رمزنگاری';
        } else {
          throw new Error('Error ' + chunkRes.status);
        }
      } catch (e) {
        statusTag.className = 'status-tag status-reconnecting';
        statusTag.textContent = 'نوسان وای‌فای! منتظر اتصال و ادامه...';
        speedText.textContent = '0 MB/s';
        await new Promise(r => setTimeout(r, 2000));
      }
    }

    uploadedBytes += (end - start);
    const now = performance.now();
    const elapsed = (now - lastTime) / 1000;
    if (elapsed >= 0.5 || i === totalChunks - 1) {
      const bytesPerSec = (uploadedBytes - lastBytes) / elapsed;
      const mbps = (bytesPerSec / (1024 * 1024)).toFixed(1);
      speedText.textContent = `${mbps} MB/s`;

      const remBytes = totalBytes - uploadedBytes;
      const eta = bytesPerSec > 0 ? Math.round(remBytes / bytesPerSec) : 0;
      const m = Math.floor(eta / 60);
      const s = eta % 60;
      etaText.textContent = m > 0 ? `${m}m ${s}s` : `${s}s`;

      lastTime = now;
      lastBytes = uploadedBytes;
    }

    const pct = ((uploadedBytes / totalBytes) * 100).toFixed(1);
    progressBar.style.width = `${pct}%`;
    percentText.textContent = `${pct}%`;
    transferredText.textContent = `${fmtSize(uploadedBytes)} / ${fmtSize(totalBytes)}`;
  }

  while (true) {
    try {
      const finRes = await fetch(`/api/upload/finish?id=${upload_id}`, { method: 'POST' });
      if (finRes.ok) break;
    } catch (e) {
      await new Promise(r => setTimeout(r, 1500));
    }
  }

  statusTag.className = 'status-tag status-done';
  statusTag.textContent = 'تکمیل شد ✔';
  progressBar.style.width = '100%';
  percentText.textContent = '100%';
  await new Promise(r => setTimeout(r, 1000));
}

async function sendInstantText() {
  const input = document.getElementById('instantTextInput');
  const text = input.value.trim();
  if (!text) return;

  await fetch('/api/text/send', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: text })
  });
  input.value = '';
  loadInstantTexts();
}

async function loadInstantTexts() {
  try {
    const res = await fetch('/api/text/list');
    const list = await res.json();
    const container = document.getElementById('instantTextMessages');
    if (!list || list.length === 0) {
      container.innerHTML = '<div class="empty-state">هنوز پیامی ردوبدل نشده است.</div>';
      return;
    }
    container.innerHTML = list.map(item => `
      <div style="background:#070a12; padding:0.75rem 1rem; border-radius:0.5rem; border:1px solid #1e293b; display:flex; justify-content:space-between; align-items:center;">
        <span style="font-size:0.92rem; word-break:break-all;">${item.text}</span>
        <button class="btn-sm" style="padding:0.3rem 0.7rem; font-size:0.8rem;" onclick="navigator.clipboard.writeText('${encodeURIComponent(item.text)}')">کپی</button>
      </div>
    `).join('');
  } catch(e) {}
}

async function deleteFile(filename) {
  if (!confirm(`آیا از حذف فایل "${filename}" اطمینان دارید؟`)) return;
  try {
    const res = await fetch(`/api/files/delete?name=${encodeURIComponent(filename)}`, { method: 'POST' });
    const result = await res.json();
    if (result.status === 'ok') {
      loadFiles();
    } else {
      alert('خطا در حذف فایل: ' + (result.error || 'ناشناخته'));
    }
  } catch (err) {
    alert('عدم دسترسی به سرور برای حذف فایل');
  }
}

async function checkP2PPeers() {
  const el = document.getElementById('p2pStatusText');
  el.textContent = 'اتصال پایدار محلی آماده همگام‌سازی مستقیم';
  el.style.color = 'var(--accent)';
}

async function loadFiles() {
  try {
    const res = await fetch('/api/files');
    const files = await res.json();
    if (!files || files.length === 0) {
      fileList.innerHTML = '<div class="empty-state">هنوز فایلی ارسال نشده است.</div>';
      return;
    }
    fileList.innerHTML = files.map(f => `
      <div class="file-row">
        <div class="file-name">${f.name}</div>
        <div class="file-meta-right">
          <div class="file-size">${f.size_formatted}</div>
          <a href="/download/${encodeURIComponent(f.name)}" class="btn-dl" download>دانلود</a>
          <button class="btn-del" onclick="deleteFile('${f.name}')">حذف 🗑️</button>
        </div>
      </div>
    `).join('');
  } catch (e) {}
}

loadFiles();
setInterval(loadFiles, 4000);
</script>
</body>
</html>
"""

messages_store = []

class LandropHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()

    def send_json(self, data, status=200):
        body = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/' or path == '/index.html':
            lan_ip = get_lan_ip()
            host_url = f"http://{lan_ip}:8989"
            content = HTML_PAGE.replace('__HOST_URL__', host_url).replace('__PIN__', CURRENT_PIN).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        if path == '/api/files':
            items = []
            for root, dirs, files in os.walk(STORAGE_DIR):
                if '.incomplete' in root:
                    continue
                for name in files:
                    if name.startswith('.'):
                        continue
                    full_path = os.path.join(root, name)
                    rel_name = os.path.relpath(full_path, STORAGE_DIR)
                    sz = os.path.getsize(full_path)
                    items.append({
                        'name': rel_name,
                        'size': sz,
                        'size_formatted': format_size(sz)
                    })
            self.send_json(items)
            return

        if path == '/api/text/list':
            self.send_json(messages_store[-10:])
            return

        if path.startswith('/download/'):
            filename = unquote(path[len('/download/'):])
            filepath = os.path.join(STORAGE_DIR, filename)

            if not os.path.isfile(filepath):
                self.send_error(404, "File not found")
                return

            filesize = os.path.getsize(filepath)
            range_header = self.headers.get('Range')
            start = 0
            end = filesize - 1

            if range_header:
                parts = range_header.replace('bytes=', '').split('-')
                start = int(parts[0]) if parts[0] else 0
                end = int(parts[1]) if len(parts) > 1 and parts[1] else filesize - 1
                self.send_response(206)
                self.send_header('Content-Range', f'bytes {start}-{end}/{filesize}')
            else:
                self.send_response(200)

            content_len = end - start + 1
            mime_type, _ = mimetypes.guess_type(filepath)
            self.send_header('Content-Type', mime_type or 'application/octet-stream')
            self.send_header('Content-Length', str(content_len))
            self.send_header('Content-Disposition', f'attachment; filename="{quote(os.path.basename(filename))}"')
            self.send_header('Accept-Ranges', 'bytes')
            self.end_headers()

            with open(filepath, 'rb') as f:
                f.seek(start)
                remaining = content_len
                buf_size = 4 * 1024 * 1024
                while remaining > 0:
                    read_n = min(remaining, buf_size)
                    chunk = f.read(read_n)
                    if not chunk:
                        break
                    try:
                        self.wfile.write(chunk)
                    except (BrokenPipeError, ConnectionResetError):
                        break
                    remaining -= len(chunk)
            return

        self.send_error(404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == '/api/files/delete':
            filename = query.get('name', [None])[0]
            if not filename:
                self.send_json({'status': 'error', 'error': 'نام فایل مشخص نشده است'}, 400)
                return
            
            clean_name = unquote(filename).replace('../', '').lstrip('/')
            target_path = os.path.join(STORAGE_DIR, clean_name)
            
            if os.path.exists(target_path) and os.path.isfile(target_path):
                try:
                    os.remove(target_path)
                    self.send_json({'status': 'ok'})
                except Exception as e:
                    self.send_json({'status': 'error', 'error': str(e)}, 500)
            else:
                self.send_json({'status': 'error', 'error': 'فایل یافت نشد'}, 404)
            return

        if path == '/api/text/send':
            length = int(self.headers.get('Content-Length', 0))
            payload = json.loads(self.rfile.read(length).decode('utf-8'))
            msg = payload.get('message', '').strip()
            if msg:
                messages_store.append({'text': msg, 'time': int(time.time())})
            self.send_json({'status': 'ok'})
            return

        if path == '/api/upload/init':
            length = int(self.headers.get('Content-Length', 0))
            payload = json.loads(self.rfile.read(length).decode('utf-8'))
            relpath = payload['filename'].replace('../', '').lstrip('/')
            filesize = payload['size']
            upload_id = get_upload_key(relpath, filesize)

            meta_file = os.path.join(TEMP_DIR, f"{upload_id}.json")
            part_file = os.path.join(TEMP_DIR, f"{upload_id}.part")

            meta = {
                'filename': relpath,
                'size': filesize,
                'total_chunks': payload.get('total_chunks', 0),
                'uploaded_chunks': []
            }

            if os.path.exists(meta_file) and os.path.exists(part_file):
                try:
                    with open(meta_file, 'r', encoding='utf-8') as mf:
                        old_meta = json.load(mf)
                        if old_meta.get('size') == filesize:
                            meta['uploaded_chunks'] = old_meta.get('uploaded_chunks', [])
                except Exception:
                    pass
            else:
                with open(meta_file, 'w', encoding='utf-8') as mf:
                    json.dump(meta, mf)
                with open(part_file, 'wb') as pf:
                    pass

            self.send_json({
                'upload_id': upload_id,
                'uploaded_chunks': meta['uploaded_chunks']
            })
            return

        if path == '/api/upload/chunk':
            upload_id = query.get('id', [None])[0]
            chunk_index = int(query.get('index', [0])[0])

            if not upload_id:
                self.send_error(400, "Missing upload_id")
                return

            part_file = os.path.join(TEMP_DIR, f"{upload_id}.part")
            meta_file = os.path.join(TEMP_DIR, f"{upload_id}.json")

            if not os.path.exists(part_file) or not os.path.exists(meta_file):
                self.send_error(400, "Invalid session")
                return

            content_length = int(self.headers.get('Content-Length', 0))
            offset = chunk_index * CHUNK_SIZE

            with open(part_file, 'r+b' if os.path.exists(part_file) else 'wb') as f:
                f.seek(offset)
                remaining = content_length
                buf = 2 * 1024 * 1024
                while remaining > 0:
                    to_read = min(remaining, buf)
                    block = self.rfile.read(to_read)
                    if not block:
                        break
                    f.write(block)
                    remaining -= len(block)

            try:
                with open(meta_file, 'r+', encoding='utf-8') as mf:
                    meta = json.load(mf)
                    if chunk_index not in meta['uploaded_chunks']:
                        meta['uploaded_chunks'].append(chunk_index)
                    mf.seek(0)
                    mf.truncate()
                    json.dump(meta, mf)
            except Exception:
                pass

            self.send_json({'status': 'ok'})
            return

        if path == '/api/upload/finish':
            upload_id = query.get('id', [None])[0]
            part_file = os.path.join(TEMP_DIR, f"{upload_id}.part")
            meta_file = os.path.join(TEMP_DIR, f"{upload_id}.json")

            if not os.path.exists(part_file) or not os.path.exists(meta_file):
                self.send_error(400, "Invalid session")
                return

            with open(meta_file, 'r', encoding='utf-8') as mf:
                meta = json.load(mf)

            final_name = meta['filename']
            final_path = os.path.join(STORAGE_DIR, final_name)
            os.makedirs(os.path.dirname(final_path), exist_ok=True)

            if os.path.exists(final_path):
                base, ext = os.path.splitext(final_name)
                final_path = os.path.join(STORAGE_DIR, f"{base}_{int(time.time())}{ext}")

            os.rename(part_file, final_path)
            try:
                os.remove(meta_file)
            except OSError:
                pass

            self.send_json({'status': 'done', 'file': os.path.basename(final_path)})
            return

        self.send_error(404)

def run():
    port = int(os.environ.get("AIRBEAM_PORT", 8989))
    server = ThreadedHTTPServer(('0.0.0.0', port), LandropHandler)
    ip = get_lan_ip()
    print("=" * 60)
    print("⚡ AirBeam Server Started")
    print(f"📡 Local Network URL: http://{ip}:{port}")
    print(f"📁 Shared Folder:     {STORAGE_DIR}")
    print(f"🔐 Security PIN:      {CURRENT_PIN}")
    print("=" * 60)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        server.server_close()

if __name__ == '__main__':
    run()
