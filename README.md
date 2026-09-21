# AirBeam ⚡

[![DevSponsors](https://img.shields.io/badge/DevSponsors-Verified_OSS-6366f1?style=for-the-badge&logo=github)](https://devsponsors.github.io)
[![Sponsor](https://img.shields.io/badge/Sponsor-DevSponsors_Hub-emerald?style=for-the-badge&logo=github-sponsors)](https://devsponsors.github.io)
![Python](https://img.shields.io/badge/Python-3.7+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20|%20macOS%20|%20Linux-0078D6?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green.style=for-the-badge)

سیستم انتقال فایل محلی فوق‌سریع و ضدقطعی برای فایل‌های فوق‌سنگین (۲۰ گیگابایت به بالا) در شبکه محلی (LAN/Wi-Fi) با رابط کاربری وب مدرن و فونت استاندارد **وزیرمتن**.

بدون نیاز به اینترنت، بدون نیاز به نصب نرم‌افزار روی دستگاه مقصد، و بدون وابستگی خارجی (Zero Dependencies - فقط کتابخانه استاندارد پایتون).

---

## ✨ قابلیت‌های کلیدی

- **🛡️ ضد قطعی و ادامه خودکار (Resumable Chunking):** فایل‌ها به قطعات ۸ مگابایتی تقسیم می‌شوند. در صورت قطع وای‌فای، خواب رفتن سیستم یا بستن تب، انتقال از بایت باقیمانده ادامه می‌یابد.
- **📱 اتصال فوری با QR Code (Zero-Type UX):** اسکن بارکد با دوربین گوشی یا سیستم مقابل بدون تایپ IP.
- **📁 پشتیبانی از انتقال پوشه کامل (Folder Drag & Drop):** ارسال کل یک پوشه به همراه تمام زیرپوشه‌ها و ساختار درختی آن.
- **🗑️ مدیریت و حذف مستقیم فایل‌ها از داخل پنل وب:** امکان حذف فایل‌های به اشتراک‌گذاشته شده با دکمه اختصاصی.
- **📋 اشتراک فوری کلیپ‌بورد و متن (Instant Text Sync):** تب مجزا برای انتقال لحظه‌ای پسوردها، توکن‌ها، لینک‌ها و یادداشت‌های متنی.
- **🔒 امنیت و تطبیق دستگاه‌ها (Security PIN):** کد پین اعتبارسنجی برای جلوگیری از اتصال‌های ناخواسته در شبکه‌های عمومی/کافه‌ها.
- **☕ بیدار نگه‌داشتن صفحه (Screen Wake Lock):** جلوگیری از خواب رفتن سیستم و قطع شبکه در حین ارسال فایل‌های حجیم.
- **🎨 رابط کاربری مدرن:** طراحی Dark Mode با فونت استاندارد فارسی Vazirmatn.

---

## 📶 شرایط اتصال و پیش‌نیازها

1. هر دو دستگاه باید به **یک شبکه وای‌فای یا کابل LAN مشترک** متصل باشند (حتی بدون اینترنت).
2. دستگاه مقصد فقط نیاز به یک مرورگر دارد (Chrome, Safari, Edge, Firefox بر روی موبایل، تبلت یا دسکتاپ).

---

## 🚀 راهنمای اجرا روی انواع سیستم‌عامل‌ها

بدون نیاز به `pip install` یا هیچ پیش‌نیاز خارجی:

### ۱. مک (macOS) و لینوکس (Linux)

```bash
git clone https://github.com/ketabchi-ar/airbeam.git
cd airbeam
python3 airbeam.py
```

### ۲. ویندوز (Windows)

```cmd
git clone https://github.com/ketabchi-ar/airbeam.git
cd airbeam
python airbeam.py
```

---

## ⚙️ تنظیمات اختیاری (پورت و مسیر ذخیره)

به طور پیش‌فرض، فایل‌ها در مسیر `~/LAN_Share` و روی پورت `8989` سرو می‌شوند:

```bash
# لینوکس و مک:
export AIRBEAM_PORT=9090
export AIRBEAM_STORAGE="/مسیر/دلخواه/شما"
python3 airbeam.py

# ویندوز (PowerShell):
$env:AIRBEAM_PORT="9090"
$env:AIRBEAM_STORAGE="D:\\SharedFiles"
python airbeam.py
```

---

## 📄 لایسنس

این پروژه تحت مجوز [MIT](LICENSE) منتشر شده است.

