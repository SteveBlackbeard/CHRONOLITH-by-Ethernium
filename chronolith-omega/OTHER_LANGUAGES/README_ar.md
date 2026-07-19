# Chronolith Omega: أوراكل المؤسسات

![Version](https://img.shields.io/badge/version-3.2.1-blue.svg)

#### الإصدارات

[![LITE](https://img.shields.io/badge/Edition-LITE-black)](../../chronolith-lite/) [![PRO](https://img.shields.io/badge/Edition-PRO-black)](../../chronolith-pro/) [![OMEGA](https://img.shields.io/badge/Edition-OMEGA-black)](../../chronolith-omega/)

#### اللغات

[![ES](https://img.shields.io/badge/ES-white)](../OTHER_LANGUAGES/README_es.md) [![JA](https://img.shields.io/badge/JA-white)](../OTHER_LANGUAGES/README_ja.md) [![RU](https://img.shields.io/badge/RU-white)](../OTHER_LANGUAGES/README_ru.md) [![ZH](https://img.shields.io/badge/ZH-white)](../OTHER_LANGUAGES/README_zh.md) [![FR](https://img.shields.io/badge/FR-white)](../OTHER_LANGUAGES/README_fr.md) [![IT](https://img.shields.io/badge/IT-white)](../OTHER_LANGUAGES/README_it.md) [![DE](https://img.shields.io/badge/DE-white)](../OTHER_LANGUAGES/README_de.md) [![PT](https://img.shields.io/badge/PT-white)](../OTHER_LANGUAGES/README_pt.md) [![KO](https://img.shields.io/badge/KO-white)](../OTHER_LANGUAGES/README_ko.md) [![AR](https://img.shields.io/badge/AR-white)](../OTHER_LANGUAGES/README_ar.md) [![EN](https://img.shields.io/badge/EN-white)](../README.md)

---

<div dir="rtl" markdown="1">

يجيب Lite وPro عن سؤال *«هل تغيّر هذا؟»*. أما **Omega** فيجيب عن *«لماذا قرّرنا هذا؟»* — بحث دلالي في المدوّنة المحكومة، محليًا بالكامل.

```bash
pip install chronolith-omega

chronolith-omega init      # نواة الذاكرة + خطّاف الفهرسة التلقائية
chronolith-omega index     # بناء مخزن المتجهات المحلي
chronolith-omega query "لماذا اخترنا Ed25519 للتوقيعات؟"
```

---

## استرجاع دلالي

يرتّب `query` المدوّنة بالمعنى لا بالكلمات المفتاحية، فيعثر على سجلّ القرار المتعلّق بالسؤال حتى لو لم ترد فيه كلمة «لماذا» ولا مرة واحدة.

كما يعبر حدود اللغات، لأن التضمينات متعدّدة اللغات: سؤال بالإنجليزية يعيد سجلّ قرار بالإسبانية لا يشترك معه في أي كلمة، بوصفه النتيجة الأولى.

تجري الفهرسة والاستعلام محليًا بالكامل؛ لا يغادر أي شيء من مدوّنتك جهازك.

---

## خريطة نسب القرارات

```bash
chronolith-omega map       # -> outputs/chronolith/cognitive_map.html
```

تُنتج رسمًا بيانيًا هرميًا تفاعليًا: كل قرار مسجَّل يصبح عقدة، مرتبطة بترتيب اتخاذها.

> **ملاحظة**: تحمّل الخريطة المولَّدة مكتبة `vis-network` من شبكة توصيل محتوى، لذا يحتاج ملف HTML ذاك وحده إلى اتصال بالشبكة كي يُعرض. أما الفهرسة والاستعلام فمحليان تمامًا.

---

## الميزات الرئيسية

- **استرجاع معزّز متقدّم**: بحث محلي فوق المدوّنة المحكومة.

- **خرائط معرفية**: تصوّر بصري لنسب القرارات.

- **تحليل الأثر**: كشف التناقضات الدلالية.

- **وعي عالمي**: توثيق ودعم لواجهة الأوامر بإحدى عشرة لغة.

---

| الدليل | الرابط |
| :--- | :--- |
| [**البداية السريعة**](../../GETTING_STARTED.md) | [GETTING_STARTED.md](../../GETTING_STARTED.md) |
| [**الدليل الصناعي**](../../HOW_TO_USE_IT.md) | [HOW_TO_USE_IT.md](../../HOW_TO_USE_IT.md) |

---

*Chronolith: نحمي النسب المنطقي لبرمجياتك.*

</div>
