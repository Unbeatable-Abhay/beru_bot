import discord
from discord.ext import commands
import config
import os
import time
import asyncio
import replicate
import threading
from datetime import datetime

import utils
from dashboard import app as dashboard_app

os.environ["REPLICATE_API_TOKEN"] = config.REPLICATE_API_TOKEN or ""

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=',', intents=intents, help_command=None)

cooldowns = {}
video_cache = {}

PROGRESS_STAGES = [
    ("▓░░░░░░░░░", "🔄 Initializing model..."),
    ("▓▓▓░░░░░░░", "🎨 Analyzing your prompt..."),
    ("▓▓▓▓▓░░░░░", "🎬 Generating frames..."),
    ("▓▓▓▓▓▓▓░░░", "🎞️ Rendering video..."),
    ("▓▓▓▓▓▓▓▓▓░", "✨ Almost done..."),
]

SUPPORTED_PLATFORMS = ["youtube", "linkedin", "instagram", "twitter", "whatsapp"]


# ── Async Groq wrapper ─────────────────────────────────────────────────────────

async def groq_complete(messages, max_tokens=500, temperature=0.8):
    def _call():
        return utils.groq_complete(messages, max_tokens=max_tokens, temperature=temperature)
    return await asyncio.get_event_loop().run_in_executor(None, _call)


# ── Internal helpers for ,create ──────────────────────────────────────────────

async def _internal_trendscore(topic):
    return await asyncio.get_event_loop().run_in_executor(None, utils.gen_trendscore, topic)


async def _internal_hashtags(platform, topic):
    return await asyncio.get_event_loop().run_in_executor(None, utils.gen_hashtags, platform, topic)


async def _internal_virality(post_content, topic):
    return await asyncio.get_event_loop().run_in_executor(None, utils.gen_virality, post_content, topic)


async def generate_post_text(platform, topic, user_id=None):
    return await asyncio.get_event_loop().run_in_executor(None, utils.gen_post, platform, topic, user_id)


# ── Video helpers ──────────────────────────────────────────────────────────────

async def progress_updater(message, start_time, stop_event):
    i = 0
    while not stop_event.is_set():
        await asyncio.sleep(30)
        if stop_event.is_set():
            break
        elapsed = int(time.time() - start_time)
        mins = elapsed // 60
        secs = elapsed % 60
        time_str = f"{mins}m {secs}s" if mins > 0 else f"{secs}s"
        idx = min(i, len(PROGRESS_STAGES) - 1)
        bar, stage = PROGRESS_STAGES[idx]
        try:
            await message.edit(content=f"⏳ Generating your video...\n`{bar}` {time_str} elapsed\n{stage}")
        except Exception:
            pass
        i += 1


def generate_video(prompt):
    output = replicate.run(
        "minimax/video-01",
        input={"prompt": prompt, "prompt_optimizer": True}
    )
    print(f"Replicate raw output: {output!r}")
    if isinstance(output, list):
        return str(output[0])
    return str(output)


# ── Dashboard in background thread ────────────────────────────────────────────

def run_dashboard():
    port = int(os.environ.get("PORT", 5000))
    dashboard_app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


# ── Events ─────────────────────────────────────────────────────────────────────

@bot.event
async def on_ready():
    utils.ensure_voices_file()
    t = threading.Thread(target=run_dashboard, daemon=True)
    t.start()
    print(f"✅ Dashboard started")
    print("✅ Bot is ready!")
    await bot.change_presence(
        status=discord.Status.dnd,
        activity=discord.Activity(type=discord.ActivityType.listening, name=" everyone 💖"))


@bot.event
async def on_message(msg):
    if msg.author == bot.user:
        return
    if msg.content.lower() == "lol":
        await msg.add_reaction("🤣")
    if msg.content.lower() == ".fm":
        await msg.channel.send(f"{msg.author.mention} yhi krte krte zindagi nikal jayigi 🥲")
    if msg.content == "who is best":
        if msg.author.id == 1504390221913919528:
            await msg.reply("You my master! 🤧")
            await msg.add_reaction("😉")
        else:
            await msg.reply(f"you bad, <@1504390221913919528> is best 🤧")
    await bot.process_commands(msg)


# ── Commands ───────────────────────────────────────────────────────────────────

@bot.command()
async def p(ctx, amt: int):
    msg = await ctx.channel.purge(limit=amt)
    log = bot.get_channel(1504486990983463164)
    for msgs in reversed(msg):
        if msgs.content:
            await log.send(f"{msgs.content} **message deleted by-** {ctx.author.mention}\n")
        elif msgs.attachments:
            await log.send("Unable to send that msg :( \n")
    await log.send(f"Total msgs deleted: {len(msg)}")
    await ctx.message.delete()


@bot.command()
async def sm(ctx, amt: int, *, text: str):
    if amt > 1:
        for i in range(amt):
            await ctx.send(text)
    else:
        await ctx.send("Invalid count")


@bot.command()
async def poll(ctx, *, text: str):
    embed = discord.Embed(title="Poll", description=text, color=discord.Color.green())
    embed.set_author(name=f"{ctx.author}")
    embed.set_image(url="https://cdn.pfps.gg/banners/42932-ironjanson.gif")
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")


@bot.command()
async def noob(ctx):
    embed = discord.Embed(title="Called me?", color=discord.Color.gold())
    embed.set_author(name=f"by {ctx.author.name}")
    embed.set_image(url="https://cdn.pfps.gg/banners/58853-fkimgworkkk.gif")
    embed.set_footer(text="custom")
    await ctx.reply(embed=embed)


@bot.command()
async def video(ctx, *, prompt: str):
    user_id = ctx.author.id
    now = time.time()
    if user_id in cooldowns:
        elapsed = now - cooldowns[user_id]
        if elapsed < 60:
            remaining = int(60 - elapsed)
            await ctx.send(f"⏳ Cooldown active! Please wait **{remaining}s** before generating another video.")
            return
    if prompt in video_cache:
        await ctx.send(f"✅ Found in cache! {ctx.author.mention} — {video_cache[prompt]}")
        return
    cooldowns[user_id] = now
    start_time = time.time()
    status_msg = await ctx.send(f"⏳ Generating your video...\n`▓░░░░░░░░░` 0s elapsed\n🔄 Initializing model...")
    stop_event = asyncio.Event()
    progress_task = asyncio.create_task(progress_updater(status_msg, start_time, stop_event))
    try:
        video_url = await bot.loop.run_in_executor(None, generate_video, prompt)
        stop_event.set()
        progress_task.cancel()
        video_cache[prompt] = video_url
        elapsed = int(time.time() - start_time)
        mins = elapsed // 60
        secs = elapsed % 60
        time_str = f"{mins}m {secs}s" if mins > 0 else f"{secs}s"
        await status_msg.edit(content=f"🎬 Here's your video {ctx.author.mention}! *(done in {time_str})*\n**Prompt:** `{prompt}`\n🔗 {video_url}")
    except Exception as e:
        stop_event.set()
        progress_task.cancel()
        await status_msg.edit(content=f"❌ Error: `{e}`")
        print(f"Video generation error: {e}")


@bot.command()
async def post(ctx, platform: str, *, topic: str):
    platform = platform.lower()
    if platform not in SUPPORTED_PLATFORMS:
        platforms_list = ", ".join(f"`{p}`" for p in SUPPORTED_PLATFORMS)
        await ctx.send(f"❌ Unknown platform. Choose from: {platforms_list}\n**Usage:** `,post linkedin your topic here`")
        return
    status_msg = await ctx.send(f"✍️ Writing your **{platform.capitalize()}** post about `{topic}`...")
    try:
        text = await generate_post_text(platform, topic, ctx.author.id)
        embed = discord.Embed(title=f"📝 {platform.capitalize()} Post", description=text, color=discord.Color.blurple())
        embed.set_footer(text="Beru Bot • AI Content Agent")
        embed.timestamp = datetime.utcnow()
        await status_msg.delete()
        await ctx.send(embed=embed)
    except Exception as e:
        await status_msg.edit(content="⚠️ Something went wrong. Please try again in a moment.")
        print(f"Post generation error: {e}")


@bot.command()
async def hook(ctx, *, topic: str):
    loading = await ctx.send("🪝 Generating hooks...")
    try:
        result = await asyncio.get_event_loop().run_in_executor(None, utils.gen_hook, topic, ctx.author.id)
        embed = discord.Embed(title="🪝 5 Scroll-Stopping Hooks", description=result, color=0x9b59b6)
        embed.set_footer(text="Beru Bot • AI Content Agent")
        embed.timestamp = datetime.utcnow()
        await loading.delete()
        await ctx.send(embed=embed)
    except Exception as e:
        await loading.edit(content="⚠️ Something went wrong. Please try again in a moment.")
        print(f"Hook error: {e}")


@bot.command()
async def script(ctx, *, topic: str):
    loading = await ctx.send("🎬 Writing your script...")
    try:
        result = await asyncio.get_event_loop().run_in_executor(None, utils.gen_script, topic, ctx.author.id)
        embed = discord.Embed(title=f"🎬 Reel Script: {topic[:50]}", description=result, color=0x3498db)
        embed.set_footer(text="Beru Bot • AI Content Agent")
        embed.timestamp = datetime.utcnow()
        await loading.delete()
        await ctx.send(embed=embed)
    except Exception as e:
        await loading.edit(content="⚠️ Something went wrong. Please try again in a moment.")
        print(f"Script error: {e}")


@bot.command()
async def trendscore(ctx, *, topic: str):
    loading = await ctx.send("📊 Analyzing trend...")
    try:
        result = await _internal_trendscore(topic)
        embed = discord.Embed(title=f"📊 Trend Analysis: {topic[:50]}", description=result, color=0x2ecc71)
        embed.set_footer(text="Beru Bot • AI Content Agent")
        embed.timestamp = datetime.utcnow()
        await loading.delete()
        await ctx.send(embed=embed)
    except Exception as e:
        await loading.edit(content="⚠️ Something went wrong. Please try again in a moment.")
        print(f"Trendscore error: {e}")


@bot.command()
async def hashtags(ctx, platform: str, *, topic: str):
    platform = platform.lower()
    loading = await ctx.send("🏷️ Finding best hashtags...")
    try:
        result = await _internal_hashtags(platform, topic)
        embed = discord.Embed(title=f"🏷️ {platform.capitalize()} Hashtags", description=result, color=0xe67e22)
        embed.set_footer(text="Beru Bot • AI Content Agent")
        embed.timestamp = datetime.utcnow()
        await loading.delete()
        await ctx.send(embed=embed)
    except Exception as e:
        await loading.edit(content="⚠️ Something went wrong. Please try again in a moment.")
        print(f"Hashtags error: {e}")


@bot.command()
async def setvoice(ctx, *, description: str):
    try:
        utils.save_voice(ctx.author.id, description)
        embed = discord.Embed(
            title="✅ Brand Voice Saved!",
            description=f"All your future posts will match this style.\n\n**Your voice:** {description}",
            color=0x1abc9c
        )
        embed.set_footer(text="Beru Bot • AI Content Agent")
        embed.timestamp = datetime.utcnow()
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send("⚠️ Something went wrong. Please try again in a moment.")
        print(f"Setvoice error: {e}")


@bot.command()
async def myvoice(ctx):
    voice = utils.get_voice(ctx.author.id)
    if voice:
        embed = discord.Embed(title="🎙️ Your Brand Voice", description=voice, color=discord.Color.green())
        embed.set_footer(text="Beru Bot • AI Content Agent")
        embed.timestamp = datetime.utcnow()
    else:
        embed = discord.Embed(
            title="🎙️ No Voice Set",
            description="You haven't set a brand voice yet!\nUse `,setvoice [description]` to set your brand voice.\n\n**Example:** `,setvoice bold, witty, and direct with a Gen-Z tone`",
            color=0xe67e22
        )
        embed.set_footer(text="Beru Bot • AI Content Agent")
        embed.timestamp = datetime.utcnow()
    await ctx.send(embed=embed)


@bot.command()
async def create(ctx, platform: str, *, topic: str):
    platform = platform.lower()
    if platform not in SUPPORTED_PLATFORMS:
        platforms_list = ", ".join(f"`{p}`" for p in SUPPORTED_PLATFORMS)
        await ctx.send(f"❌ Unknown platform. Choose from: {platforms_list}")
        return

    progress_msg = await ctx.send("🔄 Working on it...\n🔍 Analyzing trends · ✍️ Writing post · 🏷️ Finding hashtags...")

    try:
        trend_result, post_result, hashtag_result = await asyncio.gather(
            _internal_trendscore(topic),
            generate_post_text(platform, topic, ctx.author.id),
            _internal_hashtags(platform, topic)
        )

        await progress_msg.edit(content="📈 Step 4/4: Predicting virality...")
        virality_result = await _internal_virality(post_result, topic)

        await progress_msg.delete()

        embed1 = discord.Embed(title="📊 Trend Analysis", description=trend_result, color=discord.Color.green())
        embed1.set_footer(text="Beru Bot • AI Content Agent")
        embed1.timestamp = datetime.utcnow()

        embed2 = discord.Embed(title=f"✍️ {platform.capitalize()} Post", description=post_result, color=0x3498db)
        embed2.set_footer(text="Beru Bot • AI Content Agent")
        embed2.timestamp = datetime.utcnow()

        embed3 = discord.Embed(title="🏷️ Hashtags", description=hashtag_result, color=0xe67e22)
        embed3.set_footer(text="Beru Bot • AI Content Agent")
        embed3.timestamp = datetime.utcnow()

        embed4 = discord.Embed(title="🚀 Virality Prediction", description=virality_result, color=discord.Color.green())
        embed4.set_footer(text="Beru Bot • AI Content Agent")
        embed4.timestamp = datetime.utcnow()

        await ctx.send(embed=embed1)
        await ctx.send(embed=embed2)
        await ctx.send(embed=embed3)
        await ctx.send(embed=embed4)
        await ctx.send(f"✅ Your content is ready, {ctx.author.name}!")

    except Exception as e:
        await progress_msg.edit(content="⚠️ Something went wrong. Please try again in a moment.")
        print(f"Create error: {e}")


@bot.command()
async def caption(ctx, platform: str, *, description: str):
    platform = platform.lower()
    if platform not in SUPPORTED_PLATFORMS:
        platforms_list = ", ".join(f"`{p}`" for p in SUPPORTED_PLATFORMS)
        await ctx.send(f"❌ Unknown platform. Choose from: {platforms_list}\n**Usage:** `,caption instagram a sunset photo at the beach`")
        return
    loading = await ctx.send(f"📸 Writing your **{platform.capitalize()}** caption...")
    try:
        result = await asyncio.get_event_loop().run_in_executor(None, utils.gen_caption, platform, description, ctx.author.id)
        embed = discord.Embed(
            title=f"📸 {platform.capitalize()} Caption",
            description=result,
            color=0xe91e8c
        )
        embed.add_field(name="📷 Photo described as", value=f"*{description[:100]}{'...' if len(description) > 100 else ''}*", inline=False)
        embed.set_footer(text="Beru Bot • AI Content Agent")
        embed.timestamp = datetime.utcnow()
        await loading.delete()
        await ctx.send(embed=embed)
    except Exception as e:
        await loading.edit(content="⚠️ Something went wrong. Please try again in a moment.")
        print(f"Caption error: {e}")


@bot.command()
async def dashboard(ctx):
    url = os.environ.get("RENDER_EXTERNAL_URL", "")
    if not url:
        url = "Dashboard URL not set"
    embed = discord.Embed(
        title="🌐 Beru Bot Dashboard",
        description=f"Use all AI tools directly in your browser — no Discord needed!\n\n🔗 **[Open Dashboard]({url})**\n\n`{url}`",
        color=0xa371f7
    )
    embed.add_field(name="✍️ Write Post", value="Generate platform-ready posts", inline=True)
    embed.add_field(name="🪝 Hook Generator", value="5 scroll-stopping hooks", inline=True)
    embed.add_field(name="⚡ Create (All-in-One)", value="Trend + post + hashtags + virality", inline=True)
    embed.set_footer(text="Beru Bot • AI Content Agent")
    embed.timestamp = datetime.utcnow()
    await ctx.send(embed=embed)


@bot.command(name="help")
async def help_command(ctx):
    embed = discord.Embed(
        title="📋 Beru Bot — All Commands",
        description="Your AI-powered social media content agent. Use `,` as the prefix.",
        color=discord.Color.gold()
    )
    embed.add_field(name="🎬 Video Generation", value="`,video <prompt>` — AI video · 60s cooldown · cached", inline=False)
    embed.add_field(
        name="✍️ Content Creation",
        value=(
            "`,post <platform> <topic>` — Ready-to-post social media text\n"
            "`,caption <platform> <photo description>` — AI caption for your photo\n"
            "`,hook <topic>` — 5 scroll-stopping opening lines\n"
            "`,script <topic>` — Full 30-60s reel script with directions\n"
            "`,create <platform> <topic>` — ⚡ Mega command: trend + post + hashtags + virality"
        ),
        inline=False
    )
    embed.add_field(
        name="📊 Analytics",
        value=(
            "`,trendscore <topic>` — Trend score, momentum & best platform\n"
            "`,hashtags <platform> <topic>` — Platform-optimised hashtag sets"
        ),
        inline=False
    )
    embed.add_field(
        name="🎙️ Brand Voice",
        value=(
            "`,setvoice <description>` — Save your personal writing style\n"
            "`,myvoice` — View your saved brand voice"
        ),
        inline=False
    )
    embed.add_field(name="🌐 Dashboard", value="`,dashboard` — Get the link to use all tools in your browser", inline=False)
    embed.add_field(name="📊 Poll", value="`,poll <question>` — Create a 👍 / 👎 poll", inline=False)
    embed.add_field(name="🗑️ Purge", value="`,p <amount>` — Delete & log messages", inline=False)
    embed.add_field(name="😄 Fun", value="`,noob` · `lol` · `.fm`", inline=False)
    embed.set_footer(text="Beru Bot • Made by Abhay with 💖")
    embed.timestamp = datetime.utcnow()
    await ctx.send(embed=embed)


bot.run(config.TOKEN)
