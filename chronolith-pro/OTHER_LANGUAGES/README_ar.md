# Chronolith Pro: إطار الاستمرارية الصناعي

![Version](https://img.shields.io/badge/version-3.2.1-blue.svg)

#### الإصدارات

[![LITE](https://img.shields.io/badge/Edition-LITE-black)](../../chronolith-lite/) [![PRO](https://img.shields.io/badge/Edition-PRO-black)](../../chronolith-pro/) [![OMEGA](https://img.shields.io/badge/Edition-OMEGA-black)](../../chronolith-omega/)

#### اللغات

[![ES](https://img.shields.io/badge/ES-white)](../OTHER_LANGUAGES/README_es.md) [![JA](https://img.shields.io/badge/JA-white)](../OTHER_LANGUAGES/README_ja.md) [![RU](https://img.shields.io/badge/RU-white)](../OTHER_LANGUAGES/README_ru.md) [![ZH](https://img.shields.io/badge/ZH-white)](../OTHER_LANGUAGES/README_zh.md) [![FR](https://img.shields.io/badge/FR-white)](../OTHER_LANGUAGES/README_fr.md) [![IT](https://img.shields.io/badge/IT-white)](../OTHER_LANGUAGES/README_it.md) [![DE](https://img.shields.io/badge/DE-white)](../OTHER_LANGUAGES/README_de.md) [![PT](https://img.shields.io/badge/PT-white)](../OTHER_LANGUAGES/README_pt.md) [![KO](https://img.shields.io/badge/KO-white)](../OTHER_LANGUAGES/README_ko.md) [![AR](https://img.shields.io/badge/AR-white)](../OTHER_LANGUAGES/README_ar.md) [![EN](https://img.shields.io/badge/EN-white)](../README.md)

---

<div dir="rtl" markdown="1">

**Pro** يقدّم كل ما في Lite، بالإضافة إلى برهان يستطيع غريب التحقّق منه دون أن يثق بك.

```bash
pip install chronolith-pro
chronolith-pro sovereign-init     # مفاتيح توقيع Ed25519 + تشفير X25519
chronolith-pro check              # خط الأساس صار موقّعًا فعليًا
chronolith-pro verify             # للقراءة فقط؛ الأمر الذي يشغّله المتشكّك
```

---

## `verify`: الأمر الذي يذكر ما لم يُثبته

يعيد `verify` حساب الجذر، ويقارنه بخط الأساس الموقّع، ويتحقّق من توقيع Ed25519 ومن سلسلة الشفافية بالكامل. ثم — وهذا هو الجزء الجدير بالقراءة — يذكر ما **لم** يُثبته:

```
! authenticity NOT verified: no --expect-fingerprint. This proves internal
  integrity only; a fork that swapped the whole key set would still pass.
```

لسدّ هذه الثغرة، مرّر `--expect-fingerprint` ببصمة حصلت عليها من قناة مستقلة. الأداة تعلن حدودها بنفسها بدلًا من أن تترك المستخدم يفترض أكثر مما جرى التحقّق منه فعلًا.

---

## التشفير السيادي

- **تكامل ميركل المرتبط بالمسار**: كل ملف ورقة مفتاحها مسارها. تعديل بايت واحد — أو إعادة تسمية، أو تبادل المحتوى بين ملفين — يغيّر جذر التجزئة.

- **خطوط أساس موقّعة بـ Ed25519**: المجموع الاختباري وحده يكشف الحوادث؛ التوقيع هو ما يكشف التزوير.

- **سلسلة شفافية الحمض النووي**: نسب للجذور يُضاف إليه فقط، وأي بتر يكشفه رأس السلسلة المرتبط بخط الأساس.

- **براهين انتماء ميركل**: يتحقّق `prove` من انتماء ملف واحد إلى الجذر بعدد تجزئات من رتبة O(log n) دون إعادة تجزئة المستودع.

- **سياق مختوم حقيقي**: X25519 مع ChaCha20-Poly1305، وخزنة مفاتيح محمية بعبارة مرور.

- **تدوير المفاتيح**: المفتاح القديم يوقّع تسليمًا إلى الجديد، فيبقى التاريخ الموقّع بمفاتيح متقاعدة قابلًا للتحقّق.

---

## شاهد خارجي: مرساة البيتكوين

```bash
chronolith-pro anchor
```

يضع طابعًا زمنيًا على رأس سلسلة الشفافية عبر OpenTimestamps، فيتمكّن طرف ثالث من تأكيد وجود حالة الحمض النووي في وقت محدّد دون الوثوق بالمشغّل.

توجد مرساة حقيقية في [`docs/evidence/`](../../docs/evidence/) — الكتلة 958484.

تتأكّد المراسي بشكل غير متزامن، ويُكمل `chronolith-pro upgrade-anchors` ما بقي معلّقًا. وهو بلا أثر بعد التأكيد، فيصلح للتشغيل المجدول.

---

## حدود معروفة

أمران متأصّلان في هذا التصميم، وموثّقان صراحةً:

- **فرع باستبدال المفاتيح**: نسخة استبدلت مجموعة المفاتيح كاملةً تبقى متسقة داخليًا، وستجتاز التحقّق ما لم تثبّت بصمة حصلت عليها من قناة مستقلة.

- **التراجع**: بدون مرساة بيتكوين مؤكَّدة، لا يمكن لطرف خارجي كشف العودة إلى حالة سابقة صالحة.

التفاصيل الكاملة: [SOVEREIGN_SECURITY.md](../SOVEREIGN_SECURITY.md)

---

| الدليل | الرابط |
| :--- | :--- |
| [**البداية السريعة**](../../GETTING_STARTED.md) | [GETTING_STARTED.md](../../GETTING_STARTED.md) |
| [**الدليل الصناعي**](../../HOW_TO_USE_IT.md) | [HOW_TO_USE_IT.md](../../HOW_TO_USE_IT.md) |
| [**الأمن**](../SOVEREIGN_SECURITY.md) | [SOVEREIGN_SECURITY.md](../SOVEREIGN_SECURITY.md) |

---

*Chronolith: نحمي النسب المنطقي لبرمجياتك.*

</div>
