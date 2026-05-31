from flask import Flask, request, jsonify, render_template_string
import utils
import threading

app = Flask(__name__)
_lock = threading.Lock()

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Beru Bot — Dashboard</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #0a0a0f;
    --surface: #111118;
    --surface2: #1a1a25;
    --border: rgba(163,113,247,0.15);
    --border2: rgba(163,113,247,0.3);
    --accent: #a371f7;
    --accent2: #7c3aed;
    --accent-glow: rgba(163,113,247,0.2);
    --text: #f0eeff;
    --muted: #8b8ba7;
    --dim: #4a4a6a;
    --success: #4ade80;
    --warn: #fbbf24;
    --err: #f87171;
    --mono: 'DM Mono', monospace;
    --sans: 'Space Grotesk', sans-serif;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html { background: var(--bg); color: var(--text); font-family: var(--sans); font-size: 15px; }
  body { min-height: 100vh; }

  /* Layout */
  .shell { display: flex; min-height: 100vh; }
  .sidebar {
    width: 240px; flex-shrink: 0;
    background: var(--surface);
    border-right: 1px solid var(--border);
    padding: 28px 0;
    display: flex; flex-direction: column;
    position: sticky; top: 0; height: 100vh; overflow-y: auto;
  }
  .main { flex: 1; padding: 40px 48px; max-width: 900px; }

  /* Sidebar */
  .logo {
    padding: 0 24px 28px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 16px;
  }
  .logo-name { font-size: 20px; font-weight: 600; letter-spacing: -0.3px; color: var(--text); }
  .logo-tag { font-size: 11px; color: var(--muted); font-family: var(--mono); margin-top: 2px; }
  .logo-dot {
    display: inline-block; width: 7px; height: 7px;
    background: var(--success); border-radius: 50%; margin-right: 6px;
    animation: pulse 2s ease-in-out infinite;
  }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }

  .nav-section { padding: 8px 24px 4px; font-size: 10px; font-family: var(--mono); color: var(--dim); letter-spacing: 1px; text-transform: uppercase; }
  .nav-item {
    display: flex; align-items: center; gap: 10px;
    padding: 10px 24px; cursor: pointer;
    font-size: 14px; color: var(--muted);
    border-left: 2px solid transparent;
    transition: all 0.15s;
  }
  .nav-item:hover { color: var(--text); background: rgba(163,113,247,0.06); }
  .nav-item.active { color: var(--accent); border-left-color: var(--accent); background: rgba(163,113,247,0.08); }
  .nav-icon { font-size: 16px; width: 18px; text-align: center; }

  .sidebar-footer { margin-top: auto; padding: 20px 24px 0; border-top: 1px solid var(--border); }
  .bot-stat { font-size: 12px; color: var(--muted); font-family: var(--mono); margin-bottom: 4px; }
  .bot-stat span { color: var(--accent); }

  /* Main */
  .page { display: none; }
  .page.active { display: block; }

  .page-header { margin-bottom: 32px; }
  .page-title { font-size: 26px; font-weight: 600; letter-spacing: -0.5px; }
  .page-sub { font-size: 14px; color: var(--muted); margin-top: 4px; }

  /* Cards */
  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 24px;
    margin-bottom: 16px;
  }
  .card-title { font-size: 13px; font-weight: 500; color: var(--muted); font-family: var(--mono); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 16px; }

  /* Stat grid */
  .stat-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 24px; }
  .stat-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 18px 20px;
  }
  .stat-label { font-size: 11px; font-family: var(--mono); color: var(--dim); text-transform: uppercase; letter-spacing: 0.5px; }
  .stat-val { font-size: 28px; font-weight: 600; color: var(--text); margin-top: 4px; }
  .stat-val.accent { color: var(--accent); }

  /* Form elements */
  .field { margin-bottom: 14px; }
  .field label { display: block; font-size: 12px; font-family: var(--mono); color: var(--muted); margin-bottom: 6px; letter-spacing: 0.3px; }
  .field input, .field select, .field textarea {
    width: 100%; background: var(--surface2);
    border: 1px solid var(--border); border-radius: 8px;
    padding: 10px 14px; color: var(--text); font-family: var(--sans); font-size: 14px;
    outline: none; transition: border 0.15s;
  }
  .field input:focus, .field select:focus, .field textarea:focus { border-color: var(--accent); }
  .field textarea { resize: vertical; min-height: 90px; }
  .field select option { background: var(--surface2); }

  .row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }

  .btn {
    display: inline-flex; align-items: center; gap: 8px;
    padding: 11px 22px; border-radius: 9px; font-family: var(--sans);
    font-size: 14px; font-weight: 500; cursor: pointer;
    border: none; transition: all 0.15s; letter-spacing: -0.1px;
  }
  .btn-primary {
    background: var(--accent); color: #fff;
  }
  .btn-primary:hover { background: var(--accent2); }
  .btn-primary:active { transform: scale(0.98); }
  .btn-primary:disabled { opacity: 0.4; cursor: not-allowed; }
  .btn-outline {
    background: transparent; color: var(--accent);
    border: 1px solid var(--border2);
  }
  .btn-outline:hover { background: var(--accent-glow); }

  /* Result box */
  .result-box {
    background: var(--surface2); border: 1px solid var(--border);
    border-radius: 10px; padding: 18px;
    font-size: 14px; line-height: 1.7; color: var(--text);
    white-space: pre-wrap; font-family: var(--mono);
    min-height: 80px; display: none;
    position: relative;
  }
  .result-box.visible { display: block; }
  .copy-btn {
    position: absolute; top: 10px; right: 10px;
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 6px; padding: 4px 10px; font-size: 11px;
    color: var(--muted); cursor: pointer; font-family: var(--mono);
  }
  .copy-btn:hover { color: var(--accent); }

  /* Loading */
  .loading {
    display: none; align-items: center; gap: 10px;
    font-size: 13px; color: var(--muted); font-family: var(--mono);
    padding: 12px 0;
  }
  .loading.visible { display: flex; }
  .spinner {
    width: 16px; height: 16px;
    border: 2px solid var(--border2);
    border-top-color: var(--accent);
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }

  /* Platform tags */
  .platform-grid { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; }
  .ptag {
    padding: 6px 14px; border-radius: 20px;
    border: 1px solid var(--border); font-size: 13px;
    color: var(--muted); cursor: pointer; transition: all 0.12s;
  }
  .ptag:hover { border-color: var(--accent); color: var(--text); }
  .ptag.sel { border-color: var(--accent); background: var(--accent-glow); color: var(--accent); font-weight: 500; }

  /* Multi-result (for ,create) */
  .multi-result { display: none; }
  .multi-result.visible { display: block; }
  .result-section { margin-bottom: 16px; }
  .result-label {
    font-size: 11px; font-family: var(--mono); color: var(--dim);
    text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;
  }

  /* Command reference */
  .cmd-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
  .cmd-card {
    background: var(--surface2); border: 1px solid var(--border);
    border-radius: 10px; padding: 14px 16px;
  }
  .cmd-name { font-family: var(--mono); font-size: 13px; color: var(--accent); margin-bottom: 4px; }
  .cmd-desc { font-size: 13px; color: var(--muted); line-height: 1.5; }
  .cmd-usage { font-family: var(--mono); font-size: 11px; color: var(--dim); margin-top: 6px; }

  /* Chat */
  .chat-window {
    background: var(--surface2); border: 1px solid var(--border);
    border-radius: 14px; padding: 20px;
    min-height: 320px; max-height: 480px; overflow-y: auto;
    margin-bottom: 14px; display: flex; flex-direction: column; gap: 12px;
  }
  .msg { display: flex; gap: 10px; align-items: flex-start; }
  .msg.user { flex-direction: row-reverse; }
  .msg-bubble {
    max-width: 75%; padding: 10px 14px; border-radius: 12px;
    font-size: 14px; line-height: 1.6;
  }
  .msg.bot .msg-bubble { background: var(--surface); border: 1px solid var(--border); color: var(--text); }
  .msg.user .msg-bubble { background: var(--accent); color: #fff; }
  .msg-avatar {
    width: 30px; height: 30px; border-radius: 50%; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; font-weight: 600;
  }
  .msg.bot .msg-avatar { background: var(--accent-glow); color: var(--accent); border: 1px solid var(--border2); }
  .msg.user .msg-avatar { background: var(--surface); color: var(--muted); border: 1px solid var(--border); }
  .chat-input-row { display: flex; gap: 10px; }
  .chat-input-row input { flex: 1; }

  /* Separator */
  .sep { height: 1px; background: var(--border); margin: 24px 0; }

  /* Responsive */
  @media (max-width: 768px) {
    .shell { flex-direction: column; }
    .sidebar { width: 100%; height: auto; position: static; padding: 16px 0; }
    .main { padding: 24px 20px; }
    .stat-grid { grid-template-columns: 1fr 1fr; }
    .cmd-grid { grid-template-columns: 1fr; }
    .row { grid-template-columns: 1fr; }
  }
</style>
</head>
<body>
<div class="shell">

  <!-- Sidebar -->
  <nav class="sidebar">
    <div class="logo">
      <div class="logo-name"><span class="logo-dot"></span>Beru Bot</div>
      <div class="logo-tag">// AI Content Agent</div>
    </div>

    <div class="nav-section">Tools</div>
    <div class="nav-item active" onclick="goto('home')">
      <span class="nav-icon">⚡</span> Create (All-in-One)
    </div>
    <div class="nav-item" onclick="goto('post')">
      <span class="nav-icon">✍️</span> Write Post
    </div>
    <div class="nav-item" onclick="goto('hook')">
      <span class="nav-icon">🪝</span> Hook Generator
    </div>
    <div class="nav-item" onclick="goto('script')">
      <span class="nav-icon">🎬</span> Script Writer
    </div>
    <div class="nav-item" onclick="goto('hashtags')">
      <span class="nav-icon">🏷️</span> Hashtags
    </div>
    <div class="nav-item" onclick="goto('caption')">
      <span class="nav-icon">📸</span> Caption
    </div>
    <div class="nav-item" onclick="goto('trendscore')">
      <span class="nav-icon">📊</span> Trend Score
    </div>

    <div class="nav-section">More</div>
    <div class="nav-item" onclick="goto('voice')">
      <span class="nav-icon">🎙️</span> Brand Voice
    </div>
    <div class="nav-item" onclick="goto('chat')">
      <span class="nav-icon">💬</span> Chat
    </div>
    <div class="nav-item" onclick="goto('commands')">
      <span class="nav-icon">📋</span> Commands
    </div>

    <div class="sidebar-footer">
      <div class="bot-stat">prefix: <span>,</span></div>
      <div class="bot-stat">platforms: <span>5</span></div>
      <div class="bot-stat">status: <span>online</span></div>
    </div>
  </nav>

  <!-- Main -->
  <main class="main">

    <!-- ── CREATE (home) ── -->
    <div id="page-home" class="page active">
      <div class="page-header">
        <div class="page-title">⚡ Create — All-in-One</div>
        <div class="page-sub">Trend analysis + post + hashtags + virality prediction in one click</div>
      </div>
      <div class="card">
        <div class="card-title">Platform</div>
        <div class="platform-grid" id="home-platforms">
          <div class="ptag sel" data-val="youtube">YouTube</div>
          <div class="ptag" data-val="instagram">Instagram</div>
          <div class="ptag" data-val="linkedin">LinkedIn</div>
          <div class="ptag" data-val="twitter">Twitter</div>
          <div class="ptag" data-val="whatsapp">WhatsApp</div>
        </div>
        <div class="field">
          <label>Topic</label>
          <input type="text" id="home-topic" placeholder="e.g. AI is replacing designers">
        </div>
        <button class="btn btn-primary" onclick="runCreate()">⚡ Generate Everything</button>
        <div class="loading" id="home-loading"><div class="spinner"></div> Running trend + post + hashtags + virality...</div>
      </div>
      <div class="multi-result" id="home-result">
        <div class="result-section">
          <div class="result-label">📊 Trend Analysis</div>
          <div class="result-box visible" id="res-trend"></div>
        </div>
        <div class="result-section">
          <div class="result-label">✍️ Post</div>
          <div class="result-box visible" id="res-post"></div>
        </div>
        <div class="result-section">
          <div class="result-label">🏷️ Hashtags</div>
          <div class="result-box visible" id="res-hashtags"></div>
        </div>
        <div class="result-section">
          <div class="result-label">🚀 Virality Prediction</div>
          <div class="result-box visible" id="res-virality"></div>
        </div>
      </div>
    </div>

    <!-- ── POST ── -->
    <div id="page-post" class="page">
      <div class="page-header">
        <div class="page-title">✍️ Write Post</div>
        <div class="page-sub">Generate platform-ready social media content</div>
      </div>
      <div class="card">
        <div class="card-title">Platform</div>
        <div class="platform-grid" id="post-platforms">
          <div class="ptag sel" data-val="youtube">YouTube</div>
          <div class="ptag" data-val="instagram">Instagram</div>
          <div class="ptag" data-val="linkedin">LinkedIn</div>
          <div class="ptag" data-val="twitter">Twitter</div>
          <div class="ptag" data-val="whatsapp">WhatsApp</div>
        </div>
        <div class="field"><label>Topic</label><input type="text" id="post-topic" placeholder="e.g. Why I quit my 9-5 job"></div>
        <button class="btn btn-primary" onclick="runPost()">✍️ Write Post</button>
        <div class="loading" id="post-loading"><div class="spinner"></div> Writing your post...</div>
      </div>
      <div class="result-box" id="post-result"><button class="copy-btn" onclick="copyResult('post-result')">copy</button></div>
    </div>

    <!-- ── HOOK ── -->
    <div id="page-hook" class="page">
      <div class="page-header">
        <div class="page-title">🪝 Hook Generator</div>
        <div class="page-sub">5 scroll-stopping opening lines for any topic</div>
      </div>
      <div class="card">
        <div class="field"><label>Topic</label><input type="text" id="hook-topic" placeholder="e.g. Morning routines that changed my life"></div>
        <button class="btn btn-primary" onclick="runHook()">🪝 Generate Hooks</button>
        <div class="loading" id="hook-loading"><div class="spinner"></div> Generating hooks...</div>
      </div>
      <div class="result-box" id="hook-result"><button class="copy-btn" onclick="copyResult('hook-result')">copy</button></div>
    </div>

    <!-- ── SCRIPT ── -->
    <div id="page-script" class="page">
      <div class="page-header">
        <div class="page-title">🎬 Script Writer</div>
        <div class="page-sub">Full 30–60s reel script with directions</div>
      </div>
      <div class="card">
        <div class="field"><label>Topic</label><input type="text" id="script-topic" placeholder="e.g. 3 habits that doubled my productivity"></div>
        <button class="btn btn-primary" onclick="runScript()">🎬 Write Script</button>
        <div class="loading" id="script-loading"><div class="spinner"></div> Writing your script...</div>
      </div>
      <div class="result-box" id="script-result"><button class="copy-btn" onclick="copyResult('script-result')">copy</button></div>
    </div>

    <!-- ── HASHTAGS ── -->
    <div id="page-hashtags" class="page">
      <div class="page-header">
        <div class="page-title">🏷️ Hashtag Finder</div>
        <div class="page-sub">Platform-optimised hashtag sets</div>
      </div>
      <div class="card">
        <div class="card-title">Platform</div>
        <div class="platform-grid" id="hashtags-platforms">
          <div class="ptag sel" data-val="instagram">Instagram</div>
          <div class="ptag" data-val="youtube">YouTube</div>
          <div class="ptag" data-val="linkedin">LinkedIn</div>
          <div class="ptag" data-val="twitter">Twitter</div>
          <div class="ptag" data-val="whatsapp">WhatsApp</div>
        </div>
        <div class="field"><label>Topic</label><input type="text" id="hashtags-topic" placeholder="e.g. fitness motivation"></div>
        <button class="btn btn-primary" onclick="runHashtags()">🏷️ Find Hashtags</button>
        <div class="loading" id="hashtags-loading"><div class="spinner"></div> Finding best hashtags...</div>
      </div>
      <div class="result-box" id="hashtags-result"><button class="copy-btn" onclick="copyResult('hashtags-result')">copy</button></div>
    </div>

    <!-- ── CAPTION ── -->
    <div id="page-caption" class="page">
      <div class="page-header">
        <div class="page-title">📸 Caption Writer</div>
        <div class="page-sub">AI caption for your photo or video</div>
      </div>
      <div class="card">
        <div class="card-title">Platform</div>
        <div class="platform-grid" id="caption-platforms">
          <div class="ptag sel" data-val="instagram">Instagram</div>
          <div class="ptag" data-val="youtube">YouTube</div>
          <div class="ptag" data-val="linkedin">LinkedIn</div>
          <div class="ptag" data-val="twitter">Twitter</div>
          <div class="ptag" data-val="whatsapp">WhatsApp</div>
        </div>
        <div class="field"><label>Photo / video description</label><textarea id="caption-desc" placeholder="e.g. A sunset photo at the beach with golden hour lighting"></textarea></div>
        <button class="btn btn-primary" onclick="runCaption()">📸 Write Caption</button>
        <div class="loading" id="caption-loading"><div class="spinner"></div> Writing caption...</div>
      </div>
      <div class="result-box" id="caption-result"><button class="copy-btn" onclick="copyResult('caption-result')">copy</button></div>
    </div>

    <!-- ── TRENDSCORE ── -->
    <div id="page-trendscore" class="page">
      <div class="page-header">
        <div class="page-title">📊 Trend Score</div>
        <div class="page-sub">Trend score, momentum and best platform for your topic</div>
      </div>
      <div class="card">
        <div class="field"><label>Topic</label><input type="text" id="trend-topic" placeholder="e.g. AI art controversy"></div>
        <button class="btn btn-primary" onclick="runTrend()">📊 Analyze Trend</button>
        <div class="loading" id="trend-loading"><div class="spinner"></div> Analyzing trend...</div>
      </div>
      <div class="result-box" id="trend-result"><button class="copy-btn" onclick="copyResult('trend-result')">copy</button></div>
    </div>

    <!-- ── VOICE ── -->
    <div id="page-voice" class="page">
      <div class="page-header">
        <div class="page-title">🎙️ Brand Voice</div>
        <div class="page-sub">Save your writing style — all future posts will match it</div>
      </div>
      <div class="card">
        <div class="field">
          <label>User ID (your Discord ID)</label>
          <input type="text" id="voice-uid" placeholder="e.g. 123456789012345678">
        </div>
        <div class="field">
          <label>Brand voice description</label>
          <textarea id="voice-desc" placeholder="e.g. bold, witty, and direct with a Gen-Z tone"></textarea>
        </div>
        <div style="display:flex;gap:10px;flex-wrap:wrap;">
          <button class="btn btn-primary" onclick="saveVoice()">💾 Save Voice</button>
          <button class="btn btn-outline" onclick="loadVoice()">👁️ View My Voice</button>
        </div>
        <div class="loading" id="voice-loading"><div class="spinner"></div> Saving...</div>
      </div>
      <div class="result-box" id="voice-result"></div>
    </div>

    <!-- ── CHAT ── -->
    <div id="page-chat" class="page">
      <div class="page-header">
        <div class="page-title">💬 Chat with Beru</div>
        <div class="page-sub">Ask anything — content ideas, strategy, feedback</div>
      </div>
      <div class="chat-window" id="chat-window">
        <div class="msg bot">
          <div class="msg-avatar">B</div>
          <div class="msg-bubble">Hey! I'm Beru Bot. Ask me anything about content creation, social media strategy, or what my commands can do for you.</div>
        </div>
      </div>
      <div class="chat-input-row">
        <div class="field" style="flex:1;margin:0;">
          <input type="text" id="chat-input" placeholder="Ask Beru something..." onkeydown="if(event.key==='Enter')sendChat()">
        </div>
        <button class="btn btn-primary" onclick="sendChat()">Send</button>
      </div>
    </div>

    <!-- ── COMMANDS ── -->
    <div id="page-commands" class="page">
      <div class="page-header">
        <div class="page-title">📋 Bot Commands</div>
        <div class="page-sub">All Beru Bot commands with the <code style="background:var(--surface2);padding:2px 6px;border-radius:4px;font-family:var(--mono);font-size:13px;">,</code> prefix</div>
      </div>
      <div class="cmd-grid">
        <div class="cmd-card">
          <div class="cmd-name">,create</div>
          <div class="cmd-desc">All-in-one: trend + post + hashtags + virality prediction</div>
          <div class="cmd-usage">,create linkedin your topic here</div>
        </div>
        <div class="cmd-card">
          <div class="cmd-name">,post</div>
          <div class="cmd-desc">Generate a platform-ready social media post</div>
          <div class="cmd-usage">,post instagram your topic</div>
        </div>
        <div class="cmd-card">
          <div class="cmd-name">,hook</div>
          <div class="cmd-desc">5 scroll-stopping opening lines</div>
          <div class="cmd-usage">,hook your topic</div>
        </div>
        <div class="cmd-card">
          <div class="cmd-name">,script</div>
          <div class="cmd-desc">Full 30–60s reel script with directions</div>
          <div class="cmd-usage">,script your topic</div>
        </div>
        <div class="cmd-card">
          <div class="cmd-name">,trendscore</div>
          <div class="cmd-desc">Trend score, momentum & best platform</div>
          <div class="cmd-usage">,trendscore your topic</div>
        </div>
        <div class="cmd-card">
          <div class="cmd-name">,hashtags</div>
          <div class="cmd-desc">Platform-optimised hashtag sets</div>
          <div class="cmd-usage">,hashtags instagram fitness</div>
        </div>
        <div class="cmd-card">
          <div class="cmd-name">,caption</div>
          <div class="cmd-desc">AI caption for your photo or video</div>
          <div class="cmd-usage">,caption instagram sunset photo</div>
        </div>
        <div class="cmd-card">
          <div class="cmd-name">,setvoice</div>
          <div class="cmd-desc">Save your personal writing style</div>
          <div class="cmd-usage">,setvoice bold and witty tone</div>
        </div>
        <div class="cmd-card">
          <div class="cmd-name">,myvoice</div>
          <div class="cmd-desc">View your saved brand voice</div>
          <div class="cmd-usage">,myvoice</div>
        </div>
        <div class="cmd-card">
          <div class="cmd-name">,video</div>
          <div class="cmd-desc">AI video generation (60s cooldown, cached)</div>
          <div class="cmd-usage">,video a robot dancing in Tokyo</div>
        </div>
        <div class="cmd-card">
          <div class="cmd-name">,poll</div>
          <div class="cmd-desc">Create a 👍 / 👎 poll in Discord</div>
          <div class="cmd-usage">,poll Is AI better than humans?</div>
        </div>
        <div class="cmd-card">
          <div class="cmd-name">,dashboard</div>
          <div class="cmd-desc">Get the link to this dashboard</div>
          <div class="cmd-usage">,dashboard</div>
        </div>
      </div>
    </div>

  </main>
</div>

<script>
  function goto(page) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.getElementById('page-' + page).classList.add('active');
    event.currentTarget.classList.add('active');
    window.scrollTo(0, 0);
  }

  function initPlatforms(groupId) {
    const group = document.getElementById(groupId);
    if (!group) return;
    group.querySelectorAll('.ptag').forEach(tag => {
      tag.addEventListener('click', () => {
        group.querySelectorAll('.ptag').forEach(t => t.classList.remove('sel'));
        tag.classList.add('sel');
      });
    });
  }
  ['home-platforms','post-platforms','hashtags-platforms','caption-platforms'].forEach(initPlatforms);

  function getPlat(groupId) {
    const sel = document.querySelector('#' + groupId + ' .ptag.sel');
    return sel ? sel.dataset.val : 'instagram';
  }

  function showLoading(id, show) {
    document.getElementById(id).classList.toggle('visible', show);
  }
  function setBtn(selector, disabled) {
    document.querySelector(selector).disabled = disabled;
  }
  function showResult(id, text) {
    const box = document.getElementById(id);
    if (!box) return;
    const btn = box.querySelector('.copy-btn');
    box.childNodes.forEach(n => { if(n.nodeType===3) n.remove(); });
    if (btn) {
      box.textContent = text;
      box.appendChild(btn);
    } else {
      box.textContent = text;
    }
    box.classList.add('visible');
  }

  async function api(endpoint, body) {
    const r = await fetch(endpoint, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify(body)
    });
    return r.json();
  }

  async function runCreate() {
    const topic = document.getElementById('home-topic').value.trim();
    const platform = getPlat('home-platforms');
    if (!topic) { alert('Enter a topic!'); return; }
    showLoading('home-loading', true);
    document.querySelector('#page-home .btn-primary').disabled = true;
    document.getElementById('home-result').classList.remove('visible');
    try {
      const d = await api('/api/create', {platform, topic});
      document.getElementById('res-trend').textContent = d.trendscore || d.error || '';
      document.getElementById('res-post').textContent = d.post || '';
      document.getElementById('res-hashtags').textContent = d.hashtags || '';
      document.getElementById('res-virality').textContent = d.virality || '';
      document.getElementById('home-result').classList.add('visible');
    } catch(e) { alert('Error: ' + e.message); }
    showLoading('home-loading', false);
    document.querySelector('#page-home .btn-primary').disabled = false;
  }

  async function runPost() {
    const topic = document.getElementById('post-topic').value.trim();
    const platform = getPlat('post-platforms');
    if (!topic) { alert('Enter a topic!'); return; }
    showLoading('post-loading', true);
    try {
      const d = await api('/api/post', {platform, topic});
      showResult('post-result', d.result || d.error);
    } catch(e) { alert('Error: ' + e.message); }
    showLoading('post-loading', false);
  }

  async function runHook() {
    const topic = document.getElementById('hook-topic').value.trim();
    if (!topic) { alert('Enter a topic!'); return; }
    showLoading('hook-loading', true);
    try {
      const d = await api('/api/hook', {topic});
      showResult('hook-result', d.result || d.error);
    } catch(e) { alert('Error: ' + e.message); }
    showLoading('hook-loading', false);
  }

  async function runScript() {
    const topic = document.getElementById('script-topic').value.trim();
    if (!topic) { alert('Enter a topic!'); return; }
    showLoading('script-loading', true);
    try {
      const d = await api('/api/script', {topic});
      showResult('script-result', d.result || d.error);
    } catch(e) { alert('Error: ' + e.message); }
    showLoading('script-loading', false);
  }

  async function runHashtags() {
    const topic = document.getElementById('hashtags-topic').value.trim();
    const platform = getPlat('hashtags-platforms');
    if (!topic) { alert('Enter a topic!'); return; }
    showLoading('hashtags-loading', true);
    try {
      const d = await api('/api/hashtags', {platform, topic});
      showResult('hashtags-result', d.result || d.error);
    } catch(e) { alert('Error: ' + e.message); }
    showLoading('hashtags-loading', false);
  }

  async function runCaption() {
    const desc = document.getElementById('caption-desc').value.trim();
    const platform = getPlat('caption-platforms');
    if (!desc) { alert('Describe your photo/video!'); return; }
    showLoading('caption-loading', true);
    try {
      const d = await api('/api/caption', {platform, description: desc});
      showResult('caption-result', d.result || d.error);
    } catch(e) { alert('Error: ' + e.message); }
    showLoading('caption-loading', false);
  }

  async function runTrend() {
    const topic = document.getElementById('trend-topic').value.trim();
    if (!topic) { alert('Enter a topic!'); return; }
    showLoading('trend-loading', true);
    try {
      const d = await api('/api/trendscore', {topic});
      showResult('trend-result', d.result || d.error);
    } catch(e) { alert('Error: ' + e.message); }
    showLoading('trend-loading', false);
  }

  async function saveVoice() {
    const uid = document.getElementById('voice-uid').value.trim();
    const desc = document.getElementById('voice-desc').value.trim();
    if (!uid || !desc) { alert('Fill in both fields!'); return; }
    showLoading('voice-loading', true);
    try {
      const d = await api('/api/setvoice', {user_id: uid, description: desc});
      showResult('voice-result', d.result || d.error);
    } catch(e) { alert('Error: ' + e.message); }
    showLoading('voice-loading', false);
  }

  async function loadVoice() {
    const uid = document.getElementById('voice-uid').value.trim();
    if (!uid) { alert('Enter your Discord user ID!'); return; }
    showLoading('voice-loading', true);
    try {
      const d = await api('/api/getvoice', {user_id: uid});
      showResult('voice-result', d.result || 'No brand voice saved yet.');
    } catch(e) { alert('Error: ' + e.message); }
    showLoading('voice-loading', false);
  }

  function copyResult(id) {
    const box = document.getElementById(id);
    const text = box.textContent.replace('copy','').trim();
    navigator.clipboard.writeText(text).then(() => {
      const btn = box.querySelector('.copy-btn');
      if (btn) { btn.textContent = 'copied!'; setTimeout(() => btn.textContent = 'copy', 1500); }
    });
  }

  const chatHistory = [];
  async function sendChat() {
    const input = document.getElementById('chat-input');
    const msg = input.value.trim();
    if (!msg) return;
    input.value = '';
    appendMsg('user', msg);
    chatHistory.push({role:'user', content: msg});
    try {
      const d = await api('/api/chat', {messages: chatHistory});
      const reply = d.result || d.error || 'Something went wrong.';
      appendMsg('bot', reply);
      chatHistory.push({role:'assistant', content: reply});
    } catch(e) {
      appendMsg('bot', 'Error: ' + e.message);
    }
  }

  function appendMsg(who, text) {
    const win = document.getElementById('chat-window');
    const div = document.createElement('div');
    div.className = 'msg ' + who;
    div.innerHTML = `<div class="msg-avatar">${who==='bot'?'B':'U'}</div><div class="msg-bubble">${text.replace(/</g,'&lt;')}</div>`;
    win.appendChild(div);
    win.scrollTop = win.scrollHeight;
  }
</script>
</body>
</html>"""


@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/api/post", methods=["POST"])
def api_post():
    data = request.json
    try:
        result = utils.gen_post(data["platform"], data["topic"])
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/hook", methods=["POST"])
def api_hook():
    data = request.json
    try:
        result = utils.gen_hook(data["topic"])
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/script", methods=["POST"])
def api_script():
    data = request.json
    try:
        result = utils.gen_script(data["topic"])
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/trendscore", methods=["POST"])
def api_trendscore():
    data = request.json
    try:
        result = utils.gen_trendscore(data["topic"])
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/hashtags", methods=["POST"])
def api_hashtags():
    data = request.json
    try:
        result = utils.gen_hashtags(data["platform"], data["topic"])
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/caption", methods=["POST"])
def api_caption():
    data = request.json
    try:
        result = utils.gen_caption(data["platform"], data["description"])
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/setvoice", methods=["POST"])
def api_setvoice():
    data = request.json
    try:
        utils.save_voice(int(data["user_id"]), data["description"])
        return jsonify({"result": f"Brand voice saved: {data['description']}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/getvoice", methods=["POST"])
def api_getvoice():
    data = request.json
    try:
        voice = utils.get_voice(int(data["user_id"]))
        return jsonify({"result": voice or "No brand voice saved yet."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/create", methods=["POST"])
def api_create():
    data = request.json
    platform = data["platform"]
    topic = data["topic"]
    try:
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as ex:
            f_trend = ex.submit(utils.gen_trendscore, topic)
            f_post = ex.submit(utils.gen_post, platform, topic)
            f_hash = ex.submit(utils.gen_hashtags, platform, topic)
            trend = f_trend.result()
            post = f_post.result()
            hashtags = f_hash.result()
            virality = utils.gen_virality(post, topic)
        return jsonify({"trendscore": trend, "post": post, "hashtags": hashtags, "virality": virality})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.json
    messages = data.get("messages", [])
    try:
        system = (
            "You are Beru Bot, an AI-powered social media content agent. "
            "You help users with content creation, social media strategy, hooks, scripts, captions, and hashtags. "
            "You are knowledgeable about YouTube, Instagram, LinkedIn, Twitter, and WhatsApp content. "
            "Be concise, energetic, and helpful. Your bot prefix is ','."
        )
        result = utils.groq_complete(messages, max_tokens=500, temperature=0.8)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def run_dashboard(port=5000):
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    run_dashboard()
