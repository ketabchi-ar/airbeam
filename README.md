<p align="center">
  <img src="assets/banner.svg" alt="AirBeam Banner" width="100%">
</p>

# AirBeam ⚡

<p align="center">
  <img src="assets/logo.svg" alt="AirBeam Logo" width="96" height="96">
</p>

<p align="center">
  <strong>Ultra-fast, Resumable Local Network File Transfer for LAN / Wi-Fi</strong><br>
  <strong>انتقال فایل محلی فوق‌سریع، سبک و ضدقطعی برای شبکه‌های LAN / Wi-Fi</strong>
</p>

<p align="center">
  <a href="https://devsponsors.github.io"><img src="https://devsponsors.github.io/assets/badges/sponsor.svg" alt="DevSponsors"></a>
  <a href="https://devsponsors.github.io"><img src="https://img.shields.io/badge/DevSponsors-Verified_OSS-6366f1?style=for-the-badge&logo=github" alt="DevSponsors"></a>
  <a href="https://devsponsors.github.io"><img src="https://img.shields.io/badge/Sponsor-DevSponsors_Hub-emerald?style=for-the-badge&logo=github-sponsors" alt="Sponsor"></a>
  <a href="https://devsponsors.github.io/mediakit.html"><img src="https://img.shields.io/badge/Infrastructure-DevSponsors_Cloud-ec4899?style=for-the-badge&logo=server" alt="Cloud"></a>
<img src="https://img.shields.io/badge/Python-3.7+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Platform-Windows%20|%20macOS%20|%20Linux-0078D6?style=for-the-badge" alt="Platform">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

---

## 🌐 Languages / زبان‌ها
- [English](#-english)
- [فارسی](#-فارسی)

---

## 🇬🇧 English

### Overview
AirBeam is a high-speed, zero-dependency local network transfer utility. No external dependencies, no cloud storage, and no client installation needed on receiver devices.

### 📸 Screenshots
#### Dashboard & Instant QR Code Pair:
![AirBeam Dashboard Preview](assets/preview.png)

#### Smart Wizard for Heavy Files:
![AirBeam Wizard](assets/wizard.png)

---

### ⚡ Quick Start (One-Liner)

#### macOS & Linux:
```bash
curl -sSL https://raw.githubusercontent.com/ketabchi-ar/airbeam/main/airbeam.py | python3
```

#### Windows (PowerShell):
```powershell
irm https://raw.githubusercontent.com/ketabchi-ar/airbeam/main/airbeam.py | python
```

---

### ✨ Features
- **⚡ Turbo Multi-Thread Download:** Built-in web download manager using parallel streams to maximize Wi-Fi throughput without requiring IDM.
- **🛡️ Resumable Transfers:** Chunked 8MB uploads with auto-resume on network drop or sleep.
- **📡 Auto Network Discovery:** Background UDP beacon broadcasting for instant peer discovery.
- **📱 Zero-Config QR Code:** Scan and pair instantly from mobile or another PC.
- **📁 Full Folder Uploads:** Drag-and-drop entire folders preserving directory structures.
- **🌐 Dual Language Support:** Instant switch between English and Persian.
- **🔒 Security PIN:** Prevents unauthorized network guests from accessing shared files.
- **☕ Screen Wake Lock:** Keeps device screen alive during transfers to prevent OS sleep.

---

## 🇮🇷 فارسی

### معرفی پروژه
ایربیم (AirBeam) یک ابزار فوق‌سریع و سبک برای انتقال فایل در شبکه محلی بدون نیاز به اینترنت و بدون حتی یک وابستگی خارجی (Zero Dependencies - فقط کتابخانه استاندارد پایتون) است.

### ⚡ اجرای سریع (تک‌دستوری)

#### در مک و لینوکس:
```bash
curl -sSL https://raw.githubusercontent.com/ketabchi-ar/airbeam/main/airbeam.py | python3
```

#### در ویندوز (PowerShell):
```powershell
irm https://raw.githubusercontent.com/ketabchi-ar/airbeam/main/airbeam.py | python
```

---

### ✨ قابلیت‌های کلیدی
- **⚡ دانلود فوق‌سریع موازی (Built-in Turbo Download):** دانلود چندکانکشنه مستقیم در داخل صفحه وب برای پر کردن سقف پهنای باند وای‌فای بدون نیاز به نصب دانلود منیجر مجزا.
- **🛡️ ضدقطعی و ادامه خودکار (Resumable Chunking):** قطعه‌بندی ۸ مگابایتی و ادامه انتقال در صورت قطعی اتصال یا اسلیپ سیستم.
- **📡 کشف خودکار در شبکه محلی (UDP Beacon Discovery):** ارسال پیام برودکست در شبکه محلی برای شناسایی دستگاه‌ها.
- **📱 جفت‌سازی فوری با QR Code:** اتصال سریع موبایل و لپ‌تاپ با اسکن دوربین بدون نیاز به تایپ دستی آدرس.
- **📁 پشتیبانی از انتقال پوشه کامل (Folder Drag & Drop):** آپلود ساختار کامل پوشه‌ها بدون نیاز به Zip کردن.
- **🌐 پشتیبانی کامل دو زبانه (فارسی / انگلیسی):** تغییر آنی زبان محیط کاربری.
- **🔒 پین‌کد امنیتی (Security PIN):** محافظت از حریم خصوصی در شبکه‌های وای‌فای اشتراکی.
- **☕ بیدار نگه‌داشتن صفحه (Screen Wake Lock):** جلوگیری از قطع ارتباط ناشی از به خواب رفتن دستگاه.

---

## ⚙️ Configuration / تنظیمات پیشرفته

```bash
# macOS & Linux
export AIRBEAM_PORT=9090
export AIRBEAM_STORAGE="~/Downloads/LAN_Share"
python3 airbeam.py

# Windows (PowerShell)
$env:AIRBEAM_PORT="9090"
$env:AIRBEAM_STORAGE="D:\\LAN_Share"
python airbeam.py
```

---

## 📄 License
Released under the [MIT License](LICENSE).
