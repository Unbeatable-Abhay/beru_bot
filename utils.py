import os
import json
import config
from groq import Groq

VOICES_FILE = "voices.json"
SUPPORTED_PLATFORMS = ["youtube", "linkedin", "instagram", "twitter", "whatsapp"]


# ── Voice helpers ──────────────────────────────────────────────────────────────

def ensure_voices_file():
    if not os.path.exists(VOICES_FILE):
        with open(VOICES_FILE, "w") as f:
            json.dump({}, f)


def load_voices():
    ensure_voices_file()
    with open(VOICES_FILE, "r") as f:
        return json.load(f)


def save_voice(user_id, voice):
    voices = load_voices()
    voices[str(user_id)] = voice
    with open(VOICES_FILE, "w") as f:
        json.dump(voices, f, indent=2)


def get_voice(user_id):
    voices = load_voices()
    return voices.get(str(user_id), None)


def voice_injection(user_id):
    voice = get_voice(user_id)
    if voice:
        return f"Write in this brand voice: {voice}."
    return "Use a neutral professional tone."


# ── Groq sync helper ───────────────────────────────────────────────────────────

def groq_complete(messages, max_tokens=500, temperature=0.5):
    import httpx
    http_client = httpx.Client()
    client = Groq(api_key=config.GROQ_API_KEY, http_client=http_client)
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()


# ── Content generators ─────────────────────────────────────────────────────────

def gen_post(platform, topic, user_id=None):
    platform_instructions = {
        "youtube": "Write an engaging YouTube community post. Include emojis, a strong hook, 3 key points, and a call to action (like & subscribe, comment below). End with 5 relevant hashtags. Max 250 words.",
        "linkedin": "Write a professional LinkedIn post. Use a thought-provoking opening line, share insights with bullet points using →, end with an engaging question for the audience. Include 5 professional hashtags. Max 220 words.",
        "instagram": "Write an Instagram caption. Start with a catchy one-liner, use emojis throughout, add a relatable story or insight, end with a CTA (save/share/comment). Add 15 relevant hashtags at the end separated by a line. Max 150 words.",
        "twitter": "Write a Twitter/X thread of exactly 5 tweets. Number each tweet (1/, 2/, 3/, 4/, 5/). Each tweet must be under 280 characters. Use emojis sparingly. Make it punchy and shareable.",
        "whatsapp": "Write a short WhatsApp broadcast message or status. Keep it casual, warm, and friendly. Use emojis. Max 80 words.",
    }
    instruction = platform_instructions.get(platform, platform_instructions["linkedin"])
    voice = voice_injection(user_id) if user_id else "Use a neutral professional tone."
    return groq_complete([
        {"role": "system", "content": f"You are an expert social media content creator specializing in {platform} content. {instruction} {voice} Only output the post itself, no explanations or meta-commentary."},
        {"role": "user", "content": f"Write a {platform} post about: {topic}"}
    ], max_tokens=500, temperature=0.5)


def gen_hook(topic, user_id=None):
    voice = voice_injection(user_id) if user_id else "Use a neutral professional tone."
    return groq_complete([
        {"role": "system", "content": f"You are a viral content strategist. {voice} Generate exactly 5 scroll-stopping opening lines (hooks) for the given topic. Each hook must be under 15 words. Use a different psychological trigger for each: 1) Curiosity gap, 2) Controversial statement, 3) Bold claim, 4) Relatable pain point, 5) Surprising statistic (realistic). Number them with 🔥 emoji. Output only the numbered hooks, nothing else."},
        {"role": "user", "content": f"Topic: {topic}"}
    ], max_tokens=300, temperature=0.5)


def gen_script(topic, user_id=None):
    voice = voice_injection(user_id) if user_id else "Use a neutral professional tone."
    return groq_complete([
        {"role": "system", "content": (
            f"You are a professional short-form video scriptwriter. {voice} "
            "Write a complete 30-60 second reel script in conversational, spoken-word style with simple language. "
            "Use this exact structure:\n"
            "🎬 HOOK (0-3s): one punchy spoken line\n"
            "📖 STORY (3-20s): 2-3 sentences of context\n"
            "💡 KEY INSIGHT (20-40s): the main value point\n"
            "📣 CTA (40-60s): call to action\n"
            "Add [PAUSE], [EMPHASIS], or [FAST] stage directions inline where appropriate. Output only the script."
        )},
        {"role": "user", "content": f"Write a reel script about: {topic}"}
    ], max_tokens=400, temperature=0.5)


def gen_trendscore(topic):
    return groq_complete([
        {"role": "system", "content": "You are a social media trend analyst. Return ONLY the structured analysis, no extra text."},
        {"role": "user", "content": (
            f"Analyze this topic for social media trend potential: {topic}\n\n"
            "Return exactly in this format:\n"
            "📊 Trend Score: XX/100\n"
            "🔥 Momentum: Rising / Stable / Declining\n"
            "🎯 Best Platform: [platform name]\n"
            "💡 Best Angle: one sentence recommendation\n"
            "⚡ Urgency: Post Now / Can Wait / Evergreen"
        )}
    ], max_tokens=150, temperature=0.4)


def gen_hashtags(platform, topic):
    if platform == "whatsapp":
        return "Hashtags don't apply to WhatsApp. Focus on a clear, engaging message instead!"
    prompts = {
        "linkedin": f"Generate 5-8 professional LinkedIn hashtags for the topic: {topic}. Return only the hashtags.",
        "instagram": (
            f"Generate Instagram hashtags for: {topic}\n\n"
            "Group them exactly like this:\n"
            "🌍 Broad (1M+ posts): ...\n"
            "🎯 Medium (100K-1M): ...\n"
            "💎 Niche (under 100K): ..."
        ),
        "twitter": f"Generate 2-3 trending-style Twitter/X hashtags for: {topic}. Return only the hashtags.",
        "youtube": f"Generate 5 relevant YouTube hashtags for: {topic}. Return only the hashtags.",
    }
    prompt = prompts.get(platform, f"Generate hashtags for {platform} about: {topic}")
    return groq_complete([
        {"role": "system", "content": "You are a hashtag strategist. Return only the hashtags in the requested format, nothing else."},
        {"role": "user", "content": prompt}
    ], max_tokens=200, temperature=0.6)


def gen_caption(platform, image_description, user_id=None):
    platform_style = {
        "instagram": "Write an Instagram photo caption. Hook in the first line (shown before 'more'). Use plain text only. Conversational and relatable tone. End with a question or CTA. Do not use emojis, markdown, asterisks, or decorative symbols. Max 150 words.",

        "linkedin": "Write a LinkedIn photo caption. Professional and insightful. Start with an observation about the image. Share a brief takeaway or story. End with a question for engagement. Use plain text only. Do not use emojis, markdown, asterisks, or decorative symbols. Max 100 words.",

        "twitter": "Write a Twitter/X photo caption. Punchy, under 240 characters. Witty or insightful. Use plain text only. Do not use emojis, markdown, asterisks, or decorative symbols.",

        "youtube": "Write a YouTube community post caption for a photo. Warm and engaging. Invite comments. Add 3 relevant hashtags. Use plain text only. Do not use emojis, markdown, asterisks, or decorative symbols. Max 100 words.",

        "whatsapp": "Write a WhatsApp status caption. Short, casual, warm. Use plain text only. Do not use emojis, markdown, asterisks, or decorative symbols. Max 50 words."
    }
    style = platform_style.get(platform, platform_style["instagram"])
    voice = voice_injection(user_id) if user_id else "Use a neutral professional tone."
    return groq_complete([
        {"role": "system", "content": f"You are an expert social media caption writer. {style} {voice} Output only the caption, no extra commentary."},
        {"role": "user", "content": f"Write a {platform} caption for this photo: {image_description}"}
    ], max_tokens=250, temperature=0.5)


def gen_virality(post_content, topic):
    return groq_complete([
        {"role": "system", "content": "You are a viral content analyst. Return ONLY the structured analysis, no extra text."},
        {"role": "user", "content": (
            f"Analyze the virality potential of this post about '{topic}':\n\n{post_content}\n\n"
            "Return exactly in this format:\n"
            "🪝 Hook Strength: X/10\n"
            "📣 Estimated Reach: [range]\n"
            "🕐 Best Time to Post: [day + time]\n"
            "🚀 Viral Potential: XX/100"
        )}
    ], max_tokens=150, temperature=0.4)
