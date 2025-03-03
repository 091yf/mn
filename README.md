# بوت إحصائيات الوسائط Discord

بوت Discord يقوم بتتبع وعرض إحصائيات الصور والفيديوهات المرسلة من قبل الأعضاء.

## المميزات
- تتبع عدد الصور والفيديوهات لكل عضو
- نظام التتابع اليومي
- إحصائيات مفصلة ومميزة
- عرض أفضل الأعضاء نشاطاً
- حفظ الإحصائيات بشكل دائم

## الأوامر
- `!me` - عرض إحصائياتك بشكل مفصل ومميز
- `!stats [@user]` - عرض إحصائيات عضو معين
- `!allstats` - عرض إحصائيات جميع الأعضاء (للمشرفين)
- `!top` - عرض أفضل 5 أعضاء
- `!streak` - عرض تتابعك اليومي
- `!topstreak` - عرض أفضل 5 تتابعات
- `!server` - عرض إحصائيات السيرفر
- `!ping` - عرض سرعة استجابة البوت

## التثبيت المحلي
1. قم بتثبيت المتطلبات:
```bash
pip install -r requirements.txt
```

2. قم بإنشاء ملف `.env` وأضف توكن البوت:
```env
DISCORD_TOKEN=your_bot_token_here
```

3. قم بتشغيل البوت:
```bash
python bot.py
```

## النشر على Railway
1. قم بربط حسابك على Railway بـ GitHub
2. قم بإنشاء مشروع جديد واختر هذا المستودع
3. أضف متغير البيئة `DISCORD_TOKEN` في إعدادات المشروع
4. سيتم نشر البوت تلقائياً

## المتطلبات
- Python 3.8 أو أحدث
- Discord.py 2.3.2
- متطلبات أخرى في `requirements.txt`

## الترخيص
هذا المشروع مرخص تحت [MIT License](LICENSE)

## ملاحظات
- يجب أن يكون للبوت الصلاحيات الكافية لقراءة الرسائل والمرفقات
- يتم تتبع الصور بامتدادات: png, jpg, jpeg, gif
- يتم تتبع الفيديوهات بامتدادات: mp4, mov, avi, webm 