import os
import sys
import discord
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime, timedelta
from dotenv import load_dotenv
import json

print("بدء تشغيل البوت...")

# تحميل المتغيرات البيئية
try:
    load_dotenv()
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("خطأ: لم يتم العثور على التوكن في ملف .env")
        sys.exit(1)
    print("تم تحميل التوكن بنجاح")
except Exception as e:
    print(f"خطأ في تحميل ملف .env: {e}")
    sys.exit(1)

# إعداد البوت
try:
    print("جاري إعداد البوت...")
    intents = discord.Intents.all()  # تفعيل جميع الصلاحيات
    bot = commands.Bot(command_prefix='!', intents=intents)  # استخدام ! فقط
    print("تم إعداد البوت بنجاح")
except Exception as e:
    print(f"خطأ في إعداد البوت: {e}")
    sys.exit(1)

# قاموس لتخزين الإحصائيات
stats = {}

# قاموس لتخزين حالة الأوامر (مفعلة/معطلة)
commands_status = {
    'stats': True,
    'allstats': True,
    'top': True,
    'reset': True,
    'resetall': True,
    'streak': True,
    'topstreak': True,
    'server': True,
    'ping': True
}

def init_user_stats(user_id):
    """تهيئة إحصائيات المستخدم"""
    if user_id not in stats:
        stats[user_id] = {
            'images': 0,
            'videos': 0,
            'last_media': None,
            'streak': 0,
            'longest_streak': 0
        }

# إضافة فحص حالة الأمر قبل تنفيذه
def command_enabled():
    async def predicate(ctx):
        command_name = ctx.command.name
        if command_name not in commands_status:
            return True
        if not commands_status[command_name]:
            await ctx.send(f"⚠️ عذراً، الأمر `{command_name}` معطل حالياً")
            return False
        return True
    return commands.check(predicate)

@bot.event
async def on_ready():
    print(f'{bot.user} تم تشغيل البوت بنجاح!')
    try:
        synced = await bot.tree.sync()
        print(f"تم مزامنة {len(synced)} من الأوامر")
    except Exception as e:
        print(f"حدث خطأ أثناء مزامنة الأوامر: {e}")
    check_streaks.start()

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    init_user_stats(str(message.author.id))
    user_stats = stats[str(message.author.id)]

    # حساب الصور والفيديوهات
    media_found = False
    for attachment in message.attachments:
        if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif']):
            user_stats['images'] += 1
            media_found = True
        elif any(attachment.filename.lower().endswith(ext) for ext in ['.mp4', '.mov', '.avi', '.webm']):
            user_stats['videos'] += 1
            media_found = True
    
    if media_found:
        now = datetime.now()
        user_stats['last_media'] = now.isoformat()

    await bot.process_commands(message)

@tasks.loop(hours=24)
async def check_streaks():
    """التحقق من التتابع اليومي"""
    now = datetime.now()
    for user_id in stats:
        user_stats = stats[user_id]
        if user_stats['last_media']:
            last_media = datetime.fromisoformat(user_stats['last_media'])
            if (now - last_media).days <= 1:
                user_stats['streak'] += 1
                user_stats['longest_streak'] = max(user_stats['streak'], user_stats['longest_streak'])
            else:
                user_stats['streak'] = 0

@bot.command(name='me')
async def me_command(ctx):
    """عرض إحصائياتي"""
    user_id = str(ctx.author.id)
    init_user_stats(user_id)

    embed = discord.Embed(title=f"إحصائياتك | {ctx.author.display_name}", color=discord.Color.green())
    
    # إضافة صورة المستخدم
    embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
    
    # إحصائيات الوسائط
    media_stats = discord.Embed(title="📊 إحصائيات الوسائط", color=discord.Color.blue())
    media_stats.add_field(name="🖼️ الصور", value=f"`{stats[user_id]['images']}`", inline=True)
    media_stats.add_field(name="🎥 الفيديوهات", value=f"`{stats[user_id]['videos']}`", inline=True)
    media_stats.add_field(name="📑 المجموع", value=f"`{stats[user_id]['images'] + stats[user_id]['videos']}`", inline=True)
    
    # إحصائيات التتابع
    streak_stats = discord.Embed(title="🔥 إحصائيات التتابع", color=discord.Color.orange())
    streak_stats.add_field(name="📈 التتابع الحالي", value=f"`{stats[user_id]['streak']} يوم`", inline=True)
    streak_stats.add_field(name="🏆 أطول تتابع", value=f"`{stats[user_id]['longest_streak']} يوم`", inline=True)
    
    if stats[user_id]['last_media']:
        last_media = datetime.fromisoformat(stats[user_id]['last_media'])
        streak_stats.add_field(name="⏰ آخر نشاط", value=f"`{last_media.strftime('%Y-%m-%d %H:%M')}`", inline=True)
    
    await ctx.send(embeds=[embed, media_stats, streak_stats])

@bot.command(name='commands')
async def help_command(ctx):
    """عرض قائمة الأوامر المتاحة"""
    embed = discord.Embed(title="قائمة الأوامر المتاحة", color=discord.Color.blue())
    embed.add_field(name="!me", value="عرض إحصائياتك بشكل مفصل ومميز", inline=False)
    embed.add_field(name="!stats [@user]", value="عرض إحصائيات عضو معين (أو إحصائياتك إذا لم تحدد عضو)", inline=False)
    embed.add_field(name="!allstats", value="عرض إحصائيات جميع الأعضاء (للمشرفين فقط)", inline=False)
    embed.add_field(name="!top", value="عرض أفضل 5 أعضاء في نشر الصور والفيديوهات", inline=False)
    embed.add_field(name="!reset", value="إعادة تعيين إحصائياتك", inline=False)
    embed.add_field(name="!resetall", value="إعادة تعيين إحصائيات الجميع (للمشرفين فقط)", inline=False)
    embed.add_field(name="!streak", value="عرض تتابعك اليومي في نشر الوسائط", inline=False)
    embed.add_field(name="!topstreak", value="عرض أفضل 5 أعضاء في التتابع اليومي", inline=False)
    embed.add_field(name="!server", value="عرض إحصائيات السيرفر", inline=False)
    embed.add_field(name="!ping", value="عرض سرعة استجابة البوت", inline=False)
    await ctx.send(embed=embed)

@bot.command(name='stats')
async def stats_command(ctx, member: discord.Member = None):
    """عرض إحصائيات المستخدم"""
    if member is None:
        member = ctx.author

    user_id = str(member.id)
    init_user_stats(user_id)

    embed = discord.Embed(title=f"إحصائيات {member.display_name}", color=discord.Color.blue())
    embed.add_field(name="الصور", value=stats[user_id]['images'], inline=True)
    embed.add_field(name="الفيديوهات", value=stats[user_id]['videos'], inline=True)
    embed.add_field(name="المجموع", value=stats[user_id]['images'] + stats[user_id]['videos'], inline=True)
    embed.add_field(name="التتابع الحالي", value=f"{stats[user_id]['streak']} يوم", inline=True)
    embed.add_field(name="أطول تتابع", value=f"{stats[user_id]['longest_streak']} يوم", inline=True)
    
    if stats[user_id]['last_media']:
        last_media = datetime.fromisoformat(stats[user_id]['last_media'])
        embed.add_field(name="آخر نشاط", value=last_media.strftime("%Y-%m-%d %H:%M"), inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='streak')
async def streak_command(ctx):
    """عرض التتابع اليومي"""
    user_id = str(ctx.author.id)
    init_user_stats(user_id)

    embed = discord.Embed(title="التتابع اليومي", color=discord.Color.purple())
    embed.add_field(name="التتابع الحالي", value=f"{stats[user_id]['streak']} يوم", inline=True)
    embed.add_field(name="أطول تتابع", value=f"{stats[user_id]['longest_streak']} يوم", inline=True)
    await ctx.send(embed=embed)

@bot.command(name='topstreak')
async def topstreak_command(ctx):
    """عرض أفضل 5 تتابعات"""
    users_streaks = []
    for user_id in stats:
        try:
            member = await ctx.guild.fetch_member(int(user_id))
            if member:
                users_streaks.append((member, stats[user_id]['streak'], stats[user_id]['longest_streak']))
        except:
            continue
    
    users_streaks.sort(key=lambda x: (x[1], x[2]), reverse=True)
    
    embed = discord.Embed(title="أفضل 5 تتابعات يومية", color=discord.Color.gold())
    
    for i, (member, streak, longest) in enumerate(users_streaks[:5], 1):
        embed.add_field(
            name=f"#{i} - {member.display_name}",
            value=f"التتابع الحالي: {streak} يوم\nأطول تتابع: {longest} يوم",
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.command(name='server')
async def server_command(ctx):
    """عرض إحصائيات السيرفر"""
    total_images = sum(user_stats['images'] for user_stats in stats.values())
    total_videos = sum(user_stats['videos'] for user_stats in stats.values())
    total_media = total_images + total_videos
    
    active_users = len([user_id for user_id in stats if stats[user_id]['images'] + stats[user_id]['videos'] > 0])
    
    embed = discord.Embed(title=f"إحصائيات سيرفر {ctx.guild.name}", color=discord.Color.green())
    embed.add_field(name="مجموع الصور", value=total_images, inline=True)
    embed.add_field(name="مجموع الفيديوهات", value=total_videos, inline=True)
    embed.add_field(name="المجموع الكلي", value=total_media, inline=True)
    embed.add_field(name="الأعضاء النشطين", value=active_users, inline=True)
    embed.add_field(name="متوسط المشاركات", value=f"{total_media/active_users:.1f}" if active_users > 0 else "0", inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='ping')
async def ping_command(ctx):
    """عرض سرعة استجابة البوت"""
    latency = round(bot.latency * 1000)
    embed = discord.Embed(title="سرعة الاستجابة", color=discord.Color.blue())
    embed.add_field(name="البينج", value=f"{latency}ms")
    await ctx.send(embed=embed)

@bot.command(name='allstats')
@commands.has_permissions(administrator=True)
async def allstats_command(ctx):
    """عرض إحصائيات جميع الأعضاء"""
    embed = discord.Embed(title="إحصائيات جميع الأعضاء", color=discord.Color.green())
    
    for user_id in stats:
        try:
            member = await ctx.guild.fetch_member(int(user_id))
            if member:
                total = stats[user_id]['images'] + stats[user_id]['videos']
                embed.add_field(
                    name=member.display_name,
                    value=f"صور: {stats[user_id]['images']}\nفيديوهات: {stats[user_id]['videos']}\nالمجموع: {total}",
                    inline=True
                )
        except:
            continue

    await ctx.send(embed=embed)

@bot.command(name='top')
async def top_command(ctx):
    """عرض أفضل 5 أعضاء"""
    users_stats = []
    for user_id in stats:
        try:
            member = await ctx.guild.fetch_member(int(user_id))
            if member:
                total = stats[user_id]['images'] + stats[user_id]['videos']
                users_stats.append((member, total, stats[user_id]['images'], stats[user_id]['videos']))
        except:
            continue
    
    users_stats.sort(key=lambda x: x[1], reverse=True)
    
    embed = discord.Embed(title="أفضل 5 أعضاء نشاطاً", color=discord.Color.gold())
    
    for i, (member, total, images, videos) in enumerate(users_stats[:5], 1):
        embed.add_field(
            name=f"#{i} - {member.display_name}",
            value=f"المجموع: {total}\nصور: {images}\nفيديوهات: {videos}",
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.command(name='reset')
async def reset_command(ctx):
    """إعادة تعيين إحصائياتك"""
    user_id = str(ctx.author.id)
    if user_id in stats:
        stats[user_id] = {
            'images': 0,
            'videos': 0,
            'last_media': None,
            'streak': 0,
            'longest_streak': 0
        }
        await ctx.send("تم إعادة تعيين إحصائياتك بنجاح!")
    else:
        await ctx.send("لا توجد لديك أي إحصائيات لإعادة تعيينها!")

@bot.command(name='resetall')
@commands.has_permissions(administrator=True)
async def resetall_command(ctx):
    """إعادة تعيين إحصائيات جميع الأعضاء"""
    stats.clear()
    await ctx.send("تم إعادة تعيين إحصائيات جميع الأعضاء بنجاح!")

# تشغيل البوت
try:
    print("جاري محاولة الاتصال بـ Discord...")
    bot.run(token)
except discord.LoginFailure:
    print("خطأ: فشل تسجيل الدخول. تأكد من صحة التوكن")
except discord.PrivilegedIntentsRequired:
    print("خطأ: البوت يحتاج إلى تفعيل Privileged Intents في Discord Developer Portal")
except Exception as e:
    print(f"خطأ غير متوقع: {e}") 