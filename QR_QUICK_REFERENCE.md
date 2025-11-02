# QR Code Quick Reference Card

## 🎯 Quick Actions

| Action | How To |
|--------|--------|
| **View QR Code** | Click indigo QR button on survey card |
| **Download QR** | Click "Download QR Code" button |
| **Copy URL** | Click copy button (📋) next to URL |
| **Scan QR** | Open phone camera → Point at QR → Tap notification |
| **Share Survey** | Share QR image or URL |

## 🔘 Button Colors on Survey Card

| Color | Action | Who Can See |
|-------|--------|-------------|
| 🟣 Purple | Create new response | Everyone |
| 🟣 Indigo | **View QR Code** ⭐ | Everyone |
| 🔵 Blue | Edit survey | Staff only |
| 🟢 Green | View summary | Staff only |
| 🔴 Red | Delete survey | Staff only |

## 📐 QR Code Sizes

| Use Case | Recommended Size | Scan Distance |
|----------|------------------|---------------|
| Business card | 2-3 cm | 10-20 cm |
| A4 print | 5-10 cm | 25-50 cm |
| Poster | 15-30 cm | 50-100 cm |
| Banner | 20+ cm | 100-200 cm |

## 🖨️ Print Settings

✅ **Best Settings:**
- Paper: White, matte
- Size: 5-10 cm for A4
- Quality: High/Best
- Format: PNG (not JPEG)

❌ **Avoid:**
- Glossy paper
- Size < 2 cm
- JPEG compression
- Color QR codes

## 📱 Scanning Apps

| Platform | Method |
|----------|--------|
| iPhone (iOS 11+) | Camera app (built-in) |
| Android | Camera or Google Lens |
| Any phone | QR Code Reader apps |
| WeChat/Zalo | Scan feature |

## 🎨 Homepage Sections

| Section | Content | Visibility |
|---------|---------|------------|
| **Hero** | Title + CTA button | Everyone |
| **Stats** | Surveys, Users, Responses | Staff only |
| **Features** | QR Access, Easy Use, Secure | Public users |
| **Search** | Find surveys | Everyone |
| **Grid** | Survey cards (3 columns) | Everyone |

## 🔧 QR Page Features

| Feature | Description |
|---------|-------------|
| **QR Display** | Large, scannable code |
| **URL Bar** | Full survey URL |
| **Copy Button** | Copy URL to clipboard |
| **Download** | Get PNG file |
| **View Survey** | Open survey page |
| **Back** | Return to list |
| **Instructions** | How to scan |

## ⚠️ Troubleshooting

| Problem | Quick Fix |
|---------|-----------|
| QR won't scan | Increase brightness, move closer |
| Download failed | Check browser permissions |
| Blurry print | Use PNG, increase size |
| Wrong orientation | Hold phone vertically |

## 📊 File Names

| Type | Format |
|------|--------|
| Downloaded QR | `survey_<slug>_qr.png` |
| Example | `survey_customer-feedback_qr.png` |

## 🌐 URLs

| Page | Path |
|------|------|
| Homepage | `/` |
| Survey detail | `/detail/<slug>/` |
| QR code page | `/qr/<slug>/` |
| QR download | `/qr/<slug>/download/` |
| Create response | `/create/<slug>/` |

## 🎯 Use Cases

### For Staff:
1. **Print & distribute** at events
2. **Display on screens** in offices
3. **Add to presentations** in meetings
4. **Share via email** to teams

### For Users:
1. **Quick access** via phone scan
2. **No typing** URLs
3. **Instant response** creation
4. **Easy sharing** with others

## 💾 Technical Specs

| Specification | Value |
|---------------|-------|
| Format | PNG |
| Error correction | Level L (7%) |
| Box size | 10 pixels |
| Border | 4 modules |
| Colors | Black on white |
| File size | ~500 bytes |

## 🚀 Pro Tips

1. **Always test** QR codes before mass distribution
2. **Include URL text** as backup below QR
3. **Good lighting** required for scanning
4. **White space** around QR improves scan rate
5. **Test on multiple** devices

## 📞 Need Help?

1. Read: `QR_CODE_GUIDE.md` (detailed)
2. Read: `HUONG_DAN_SU_DUNG_QR.md` (Vietnamese)
3. Run tests: `python test_qr_code.py`
4. Contact: System administrator

## ✨ Quick Start (3 Steps)

```
1. Click QR button (indigo) → See QR code
2. Click "Download" → Get PNG file
3. Share → Users scan → Access survey
```

**That's it! Easy as 1-2-3!** 🎉

---

*Print this page for quick reference!*

**Version:** 1.0 | **Date:** 2025-01-02 | **Status:** ✅ Ready
