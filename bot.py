import discord
from discord import app_commands  # المكتبة المسؤولة عن السلاش
from discord.ext import commands
import aiohttp
from deep_translator import GoogleTranslator
import urllib.request
import re
import random


# 1. إعداد البوت مع الصلاحيات
class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    # دالة لمزامنة أوامر السلاش مع سيرفرات ديسكورد عند التشغيل
    async def setup_hook(self):
        await self.tree.sync()
        print(f"✅ تم مزامنة أوامر السلاش بنجاح!")


bot = MyBot()
OMDB_API_KEY = 'abda7299'


# ---------------------------------------------------------
# 🔍 دالة البحث عن التريلر (لا تتغير)
# ---------------------------------------------------------
def get_trailer_link(movie_name):
    try:
        search_keyword = movie_name.replace(" ", "+") + "+official+trailer"
        html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + search_keyword)
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        if video_ids:
            return f"https://www.youtube.com/watch?v={video_ids[0]}"
        return None
    except:
        return None


# ---------------------------------------------------------
# 🎬 أمر البحث عن الأفلام (/movie)
# ---------------------------------------------------------
@bot.tree.command(name="movie", description="البحث عن تفاصيل فيلم أو مسلسل")
@app_commands.describe(movie_name="اكتب اسم الفيلم بالإنجليزية")
async def movie(interaction: discord.Interaction, movie_name: str):
    # في نظام السلاش نستخدم interaction.response بدلاً من ctx.send
    await interaction.response.send_message(f'⏳ جاري البحث عن **"{movie_name}"**...')

    url = f"http://www.omdbapi.com/?t={movie_name}&apikey={OMDB_API_KEY}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()

    if data.get("Response") == "False":
        await interaction.edit_original_response(content=f'❌ لم أجد فيلماً بهذا الاسم: `{movie_name}`')
        return

    title = data.get("Title")
    year = data.get("Year")
    rating = data.get("imdbRating")
    plot_eng = data.get("Plot")
    poster_url = data.get("Poster")

    try:
        plot_ar = GoogleTranslator(source='auto', target='ar').translate(plot_eng)
    except:
        plot_ar = plot_eng

    trailer_url = get_trailer_link(f"{title} {year}")

    embed = discord.Embed(
        title=f"🎬 {title} ({year})",
        description=f"**القصة:**\n{plot_ar}",
        color=discord.Color.blue()
    )
    embed.add_field(name="⭐ تقييم IMDb", value=f"**{rating}/10**")
    if poster_url and poster_url != "N/A":
        embed.set_thumbnail(url=poster_url)

    content_text = f"🍿 **التريلر:** {trailer_url}" if trailer_url else ""
    await interaction.edit_original_response(content=content_text, embed=embed)


# ---------------------------------------------------------
# 💡 أمر الاقتراحات المطور (/suggest)
# ---------------------------------------------------------
@bot.tree.command(name="suggest", description="اقتراح عمل سينمائي عشوائي")
@app_commands.choices(category=[
    app_commands.Choice(name="جريمة وغموض 🕵️‍♂️", value="جريمة"),
    app_commands.Choice(name="فانتازيا وخيال 🐉", value="فانتازيا"),
    app_commands.Choice(name="حروب وتاريخ ⚔️", value="تاريخ"),
    app_commands.Choice(name="أكشن وإثارة 🔥", value="أكشن")
])
async def suggest(interaction: discord.Interaction, category: app_commands.Choice[str]):
    # هنا تظهر قوة السلاش! المستخدم يختار من قائمة بدلاً من الكتابة
    library = {
        "جريمة": ["The Silence of the Lambs", "Se7en", "Prisoners", "Zodiac", "Dexter"],
        "فانتازيا": ["The Lord of the Rings", "The Witcher", "Dune", "Game of Thrones"],
        "تاريخ": ["Gladiator", "Kingdom of Heaven", "Saving Private Ryan", "Braveheart"],
        "أكشن": ["The Dark Knight", "Inception", "John Wick", "The Matrix"]
    }

    selected = random.choice(library[category.value])
    await interaction.response.send_message(f"🎲 بما أنك تحب **{category.name}**، إليك هذا الاقتراح:")

    # استدعاء دالة البحث مباشرة لعرض النتائج
    # ملاحظة: في السلاش نفضل تكرار المنطق أو استدعاء دالة مشتركة
    await movie.callback(interaction, selected)


@bot.event
async def on_ready():
    print(f'✅ {bot.user.name} جاهز بنظام السلاش!')


# ضع التوكن الخاص بك هنا
bot.run('MTQ4Njc2MzQzNTkyNzc5NzkxMA.G6K9Ap.z0C0E0lubNFw8T9jQDjjBgVvmx_RvHfQhjLhoo')