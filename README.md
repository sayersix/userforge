# UserForge

A 100% **offline** local generator for candidate short usernames (3–4 characters) — featuring a premium desktop GUI and a full-featured CLI, for manually checking on WhatsApp or any platform that supports short usernames.

أداة محلية **بدون أي اتصال بالإنترنت** لتوليد قوائم يوزرات مرشّحة بطول 3 أو 4 أحرف — بواجهة رسومية فخمة (GUI) وواجهة سطر أوامر (CLI) كاملة، لتجربتها يدويًا داخل واتساب أو أي منصة تدعم يوزرات ثنائيه ثلاثيه رباعيه.

---

## Features / المميزات

| EN | عربي |
|---|---|
| Unique 3 or 4 character combinations (letters / digits / mixed / custom charset) | تركيبات فريدة بطول 3 أو 4 أحرف (حروف / أرقام / مزيج / مجموعة حروف مخصصة) |
| **Pronounceable mode**: consonant-vowel pattern for natural-looking results | وضع **Pronounceable**: نمط ساكن-متحرك يطلع نتائج أقرب لاسم حقيقي |
| Filters: starts-with / ends-with / contains / exclude chars | فلاتر: starts-with / ends-with / contains / exclude chars |
| `--seed` for reproducible output | بذرة عشوائية (`--seed`) لنتائج قابلة لإعادة الإنتاج |
| Generate multiple lengths at once (3 and 4 together) | توليد لعدة أطوال دفعة وحدة (3 و4 مع بعض) |
| Search-space statistics (theoretical max combinations) | إحصائية حجم فضاء البحث (كم تركيبة ممكنة نظريًا) |
| Export to .txt / .json, or copy to clipboard (GUI) | تصدير txt / json، أو نسخ مباشر للحافظة (بالـGUI) |
| Premium GUI: gradient header, cards, tabs (Generate / About) | GUI فخم: هيدر بتدرج لوني، بطاقات، تبويبات (Generate / About) |
| Full CLI for scripting/automation, with colored output | CLI كامل للأتمتة والسكربتة، بمخرجات ملونة |

---

## Run — GUI
<img width="1911" height="881" alt="image" src="https://github.com/user-attachments/assets/1d4efbee-0429-40d1-959c-c51acbcebc3f" />

```bash
python userforge_gui.py
```

## Run — CLI
<img width="1278" height="481" alt="image" src="https://github.com/user-attachments/assets/4de201ec-fbc6-4be3-8ddf-fa9d56dd3ed8" />

```bash
# Generate 50 pronounceable 3-char letter usernames
python cli.py -l 3 -m letters --pronounceable -n 50

# Both lengths at once + export
python cli.py -l 3 -l 4 -m mixed -n 200 --starts-with k --out results --format both

# Custom charset + fixed seed for reproducible results
python cli.py -l 3 --charset "kxzqj" -n 20 --seed 42

# Just show search-space stats, no generation
python cli.py -l 3 -m mixed --stats

# Clean output for piping (no colors/banner)
python cli.py -l 3 -n 20 --quiet --no-color > list.txt
```

Run `python cli.py --help` for all options. / شغّل `python cli.py --help` لكل الخيارات.

---

## Requirements / المتطلبات

Python 3.8+ only. Tkinter (for the GUI) ships with most default Python installs. No external libraries, no network access required.

Python 3.8+ فقط. Tkinter (للـGUI) مدمج بالتنصيب الافتراضي لمعظم الأنظمة. لا توجد أي مكتبات خارجية ولا حاجة لاتصال شبكي.

---

## Project structure / بنية المشروع

```
userforge/
├── engine.py          # Core generation logic — zero network calls / محرك التوليد، بدون أي شبكة
├── userforge_gui.py    # GUI (Tkinter) / الواجهة الرسومية
├── cli.py              # Command-line interface / واجهة سطر الأوامر
└── README.md
```

---

## Creator / صاحب المشروع

- guns.lol: https://guns.lol/SayerSix
- YouTube: https://www.youtube.com/@sayersix-s
- Discord server: https://discord.gg/isi
- Discord: `sayersix`
