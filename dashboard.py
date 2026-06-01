from flask import Flask, request, jsonify, render_template_string
import utils
import threading
import concurrent.futures

app = Flask(__name__)

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Beru — AI Content Studio</title>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/tabler-icons.min.css">
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --ink:#0c0c10;--ink2:#3a3a4a;--ink3:#7a7a90;
  --paper:#f7f6f2;--paper2:#eeecea;--paper3:#e4e2de;
  --accent:#1a1a2e;--gold:#c9a84c;--gold2:#e8c96a;
  --white:#ffffff;
  --r:10px;--r2:16px;--r3:24px;
  --mono:'DM Mono',monospace;
  --sans:'DM Sans',sans-serif;
  --display:'Syne',sans-serif;
  --shadow:0 1px 3px rgba(0,0,0,0.06),0 4px 16px rgba(0,0,0,0.04);
  --shadow2:0 2px 8px rgba(0,0,0,0.08),0 8px 32px rgba(0,0,0,0.06);
}
html{background:var(--paper);color:var(--ink);font-family:var(--sans);font-size:15px;-webkit-font-smoothing:antialiased}
body{min-height:100vh;display:flex}

/* ── Sidebar ── */
.sidebar{
  width:256px;flex-shrink:0;background:var(--accent);
  display:flex;flex-direction:column;
  min-height:100vh;position:sticky;top:0;height:100vh;overflow-y:auto;
}
.brand{padding:28px 24px 20px;border-bottom:1px solid rgba(255,255,255,0.06)}
.brand-logo{display:flex;align-items:center;gap:10px;margin-bottom:6px}
.brand-gem{
  width:34px;height:34px;background:var(--gold);border-radius:8px;
  display:flex;align-items:center;justify-content:center;flex-shrink:0;
}
.brand-gem i{font-size:18px;color:var(--accent)}
.brand-name{font-family:var(--display);font-size:19px;font-weight:700;color:#fff;letter-spacing:-0.2px}
.brand-tagline{font-size:11px;color:rgba(255,255,255,0.35);font-family:var(--mono);letter-spacing:0.5px}

.nav-group{padding:20px 0 4px}
.nav-label{
  padding:0 20px 8px;font-size:10px;font-family:var(--mono);
  color:rgba(255,255,255,0.25);letter-spacing:1.5px;text-transform:uppercase
}
.nav-item{
  display:flex;align-items:center;gap:10px;
  padding:10px 20px;cursor:pointer;
  font-size:13.5px;font-weight:400;color:rgba(255,255,255,0.5);
  border-left:2px solid transparent;transition:all 0.15s;position:relative;
}
.nav-item i{font-size:17px;width:20px;text-align:center;flex-shrink:0}
.nav-item:hover{color:rgba(255,255,255,0.85);background:rgba(255,255,255,0.04)}
.nav-item.active{color:#fff;border-left-color:var(--gold);background:rgba(255,255,255,0.06);font-weight:500}
.nav-item .badge{
  margin-left:auto;font-size:9px;font-family:var(--mono);
  background:var(--gold);color:var(--accent);
  padding:2px 6px;border-radius:4px;font-weight:700;letter-spacing:0.5px;
}

.sidebar-footer{
  margin-top:auto;padding:20px 20px 24px;
  border-top:1px solid rgba(255,255,255,0.06);
}
.status-row{display:flex;align-items:center;gap:8px;margin-bottom:10px}
.status-dot{width:6px;height:6px;background:#4ade80;border-radius:50%;animation:blink 2s ease-in-out infinite;flex-shrink:0}
@keyframes blink{0%,100%{opacity:1}50%{opacity:0.3}}
.status-text{font-size:12px;color:rgba(255,255,255,0.4);font-family:var(--mono)}
.status-text span{color:rgba(255,255,255,0.7)}
.version-tag{font-size:10px;color:rgba(255,255,255,0.2);font-family:var(--mono)}

/* ── Main ── */
.main{flex:1;padding:0;overflow-x:hidden}
.page{display:none;min-height:100vh}
.page.active{display:flex;flex-direction:column}

/* Page header */
.page-head{
  padding:36px 44px 28px;
  border-bottom:1px solid var(--paper3);
  background:var(--white);
}
.page-head-inner{display:flex;align-items:flex-start;justify-content:space-between;gap:20px}
.page-eyebrow{
  font-size:10px;font-family:var(--mono);color:var(--ink3);
  letter-spacing:1.5px;text-transform:uppercase;margin-bottom:6px;
}
.page-title{font-family:var(--display);font-size:28px;font-weight:700;color:var(--ink);letter-spacing:-0.5px;line-height:1.1}
.page-sub{font-size:14px;color:var(--ink3);margin-top:5px;font-weight:300;line-height:1.5}
.page-icon{
  width:52px;height:52px;border-radius:14px;background:var(--accent);
  display:flex;align-items:center;justify-content:center;flex-shrink:0;
}
.page-icon i{font-size:24px;color:var(--gold)}

/* Content area */
.page-body{padding:32px 44px;flex:1;background:var(--paper)}

/* Cards */
.card{
  background:var(--white);border:1px solid var(--paper3);
  border-radius:var(--r2);padding:24px;margin-bottom:20px;
  box-shadow:var(--shadow);
}
.card-label{
  font-size:11px;font-family:var(--mono);color:var(--ink3);
  text-transform:uppercase;letter-spacing:1px;margin-bottom:16px;
  display:flex;align-items:center;gap:6px;
}
.card-label i{font-size:14px}

/* Platform selector */
.platform-row{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:20px}
.ptag{
  display:flex;align-items:center;gap:6px;
  padding:7px 14px;border-radius:8px;
  border:1.5px solid var(--paper3);background:var(--paper);
  font-size:13px;color:var(--ink3);cursor:pointer;
  transition:all 0.12s;font-family:var(--sans);font-weight:400;
}
.ptag i{font-size:15px}
.ptag:hover{border-color:var(--ink2);color:var(--ink);background:var(--paper2)}
.ptag.sel{border-color:var(--accent);background:var(--accent);color:#fff}
.ptag.sel i{color:var(--gold)}

/* Form */
.field{margin-bottom:16px}
.field label{
  display:flex;align-items:center;gap:6px;
  font-size:12px;font-family:var(--mono);color:var(--ink3);
  margin-bottom:7px;letter-spacing:0.3px;text-transform:uppercase;
}
.field label i{font-size:14px}
.field input,.field textarea,.field select{
  width:100%;background:var(--paper);
  border:1.5px solid var(--paper3);border-radius:var(--r);
  padding:11px 14px;color:var(--ink);font-family:var(--sans);
  font-size:14px;outline:none;transition:all 0.15s;
}
.field input:focus,.field textarea:focus{border-color:var(--accent);background:var(--white);box-shadow:0 0 0 3px rgba(26,26,46,0.06)}
.field textarea{resize:vertical;min-height:100px;line-height:1.6}

/* Buttons */
.btn{
  display:inline-flex;align-items:center;gap:8px;
  padding:11px 22px;border-radius:var(--r);
  font-family:var(--sans);font-size:14px;font-weight:500;
  cursor:pointer;border:none;transition:all 0.15s;letter-spacing:-0.1px;
}
.btn-primary{background:var(--accent);color:#fff}
.btn-primary:hover{background:#2d2d4a;transform:translateY(-1px);box-shadow:0 4px 12px rgba(26,26,46,0.25)}
.btn-primary:active{transform:translateY(0)}
.btn-primary:disabled{opacity:0.4;cursor:not-allowed;transform:none;box-shadow:none}
.btn-ghost{background:transparent;color:var(--ink2);border:1.5px solid var(--paper3)}
.btn-ghost:hover{background:var(--paper);border-color:var(--ink3)}
.btn i{font-size:16px}

/* Result */
.result-wrap{display:none;margin-top:20px}
.result-wrap.visible{display:block}
.result-header{
  display:flex;align-items:center;justify-content:space-between;
  margin-bottom:8px;
}
.result-label-sm{font-size:11px;font-family:var(--mono);color:var(--ink3);text-transform:uppercase;letter-spacing:1px;display:flex;align-items:center;gap:5px}
.result-label-sm i{font-size:13px}
.copy-btn{
  display:flex;align-items:center;gap:5px;
  background:var(--paper);border:1.5px solid var(--paper3);
  border-radius:6px;padding:5px 10px;font-size:11px;
  color:var(--ink3);cursor:pointer;font-family:var(--mono);
  transition:all 0.12s;
}
.copy-btn:hover{border-color:var(--ink3);color:var(--ink)}
.copy-btn i{font-size:13px}
.result-box{
  background:var(--paper);border:1.5px solid var(--paper3);
  border-radius:var(--r);padding:18px;
  font-size:13.5px;line-height:1.75;color:var(--ink2);
  white-space:pre-wrap;font-family:var(--mono);min-height:60px;
}

/* Loading */
.loader{display:none;align-items:center;gap:10px;padding:14px 0;font-size:13px;color:var(--ink3);font-family:var(--mono)}
.loader.visible{display:flex}
.spin{width:15px;height:15px;border:2px solid var(--paper3);border-top-color:var(--accent);border-radius:50%;animation:spin 0.65s linear infinite;flex-shrink:0}
@keyframes spin{to{transform:rotate(360deg)}}

/* Multi-result (create) */
.multi-wrap{display:none;margin-top:20px}
.multi-wrap.visible{display:block}
.result-section{margin-bottom:16px}
.result-section-head{
  display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;
}

/* Stat grid */
.stat-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:24px}
.stat{
  background:var(--white);border:1px solid var(--paper3);
  border-radius:var(--r2);padding:18px 20px;
  box-shadow:var(--shadow);
}
.stat-label{font-size:11px;font-family:var(--mono);color:var(--ink3);text-transform:uppercase;letter-spacing:0.8px;margin-bottom:4px;display:flex;align-items:center;gap:5px}
.stat-label i{font-size:13px}
.stat-val{font-family:var(--display);font-size:26px;font-weight:700;color:var(--ink)}
.stat-val.gold{color:var(--gold)}

/* Chat */
.chat-area{
  background:var(--white);border:1px solid var(--paper3);
  border-radius:var(--r2);padding:20px;min-height:340px;max-height:460px;
  overflow-y:auto;margin-bottom:14px;
  display:flex;flex-direction:column;gap:14px;
  box-shadow:var(--shadow);
}
.msg{display:flex;gap:10px;align-items:flex-start}
.msg.user{flex-direction:row-reverse}
.avatar{
  width:32px;height:32px;border-radius:50%;flex-shrink:0;
  display:flex;align-items:center;justify-content:center;font-size:13px;
}
.msg.bot .avatar{background:var(--accent);color:var(--gold)}
.msg.user .avatar{background:var(--paper2);color:var(--ink3);border:1px solid var(--paper3)}
.bubble{
  max-width:76%;padding:11px 15px;border-radius:12px;
  font-size:13.5px;line-height:1.65;
}
.msg.bot .bubble{background:var(--paper);border:1px solid var(--paper3);color:var(--ink);border-bottom-left-radius:4px}
.msg.user .bubble{background:var(--accent);color:#fff;border-bottom-right-radius:4px}
.chat-row{display:flex;gap:10px}
.chat-row .field{flex:1;margin:0}

/* Commands grid */
.cmd-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.cmd{
  background:var(--white);border:1px solid var(--paper3);
  border-radius:var(--r2);padding:16px 18px;
  box-shadow:var(--shadow);
}
.cmd-top{display:flex;align-items:center;gap:8px;margin-bottom:6px}
.cmd-icon{
  width:30px;height:30px;border-radius:8px;background:var(--paper);
  border:1px solid var(--paper3);display:flex;align-items:center;justify-content:center;flex-shrink:0;
}
.cmd-icon i{font-size:15px;color:var(--ink2)}
.cmd-name{font-family:var(--mono);font-size:13px;color:var(--accent);font-weight:500}
.cmd-desc{font-size:13px;color:var(--ink3);line-height:1.5;margin-bottom:6px}
.cmd-usage{font-family:var(--mono);font-size:11px;color:var(--paper3);background:var(--accent);display:inline-block;padding:3px 8px;border-radius:5px}

/* Voice page */
.voice-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}

/* Divider */
.sep{height:1px;background:var(--paper3);margin:24px 0}

/* Row layout */
.row2{display:grid;grid-template-columns:1fr 1fr;gap:14px}

/* Responsive */
@media(max-width:900px){
  body{flex-direction:column}
  .sidebar{width:100%;height:auto;min-height:unset;position:static;flex-direction:row;flex-wrap:wrap;padding:12px 0}
  .brand{border:none;padding:12px 16px}
  .nav-group{padding:4px 0;display:flex;flex-wrap:wrap}
  .nav-label{display:none}
  .nav-item{padding:8px 12px;border-left:none;border-bottom:2px solid transparent;font-size:12px}
  .nav-item.active{border-bottom-color:var(--gold);border-left:none}
  .sidebar-footer{display:none}
  .page-head{padding:20px 20px 16px}
  .page-body{padding:20px}
  .stat-grid{grid-template-columns:1fr 1fr}
  .cmd-grid{grid-template-columns:1fr}
  .voice-grid{grid-template-columns:1fr}
  .row2{grid-template-columns:1fr}
}
</style>
</head>
<body>

<!-- ── Sidebar ── -->
<nav class="sidebar">
  <div class="brand">
    <div class="brand-logo">
      <div class="brand-gem"><i class="ti ti-sparkles"></i></div>
      <div class="brand-name">Beru</div>
    </div>
    <div class="brand-tagline">// AI Content Studio</div>
  </div>

  <div class="nav-group">
    <div class="nav-label">Create</div>
    <div class="nav-item active" onclick="goto('create',this)">
      <i class="ti ti-bolt"></i> All-in-One
      <span class="badge">PRO</span>
    </div>
    <div class="nav-item" onclick="goto('post',this)">
      <i class="ti ti-pencil"></i> Write Post
    </div>
    <div class="nav-item" onclick="goto('hook',this)">
      <i class="ti ti-fish-hook"></i> Hook Generator
    </div>
    <div class="nav-item" onclick="goto('script',this)">
      <i class="ti ti-movie"></i> Script Writer
    </div>
    <div class="nav-item" onclick="goto('caption',this)">
      <i class="ti ti-camera"></i> Caption
    </div>
  </div>

  <div class="nav-group">
    <div class="nav-label">Analyse</div>
    <div class="nav-item" onclick="goto('trendscore',this)">
      <i class="ti ti-trending-up"></i> Trend Score
    </div>
    <div class="nav-item" onclick="goto('hashtags',this)">
      <i class="ti ti-hash"></i> Hashtags
    </div>
  </div>

  <div class="nav-group">
    <div class="nav-label">Personalise</div>
    <div class="nav-item" onclick="goto('voice',this)">
      <i class="ti ti-microphone"></i> Brand Voice
    </div>
    <div class="nav-item" onclick="goto('chat',this)">
      <i class="ti ti-message-chatbot"></i> Chat
    </div>
    <div class="nav-item" onclick="goto('commands',this)">
      <i class="ti ti-terminal-2"></i> Commands
    </div>
  </div>

  <div class="sidebar-footer">
    <div class="status-row">
      <div class="status-dot"></div>
      <div class="status-text">Bot <span>online</span></div>
    </div>
    <div class="status-text" style="margin-bottom:6px">Prefix <span>,</span> &nbsp;·&nbsp; Platforms <span>5</span></div>
    <div class="version-tag">Beru Bot v2.0</div>
  </div>
</nav>

<!-- ── Pages ── -->
<main class="main">

  <!-- CREATE -->
  <div id="page-create" class="page active">
    <div class="page-head">
      <div class="page-head-inner">
        <div>
          <div class="page-eyebrow">All-in-One</div>
          <div class="page-title">Content Suite</div>
          <div class="page-sub">Trend analysis · post · hashtags · virality — in one click</div>
        </div>
        <div class="page-icon"><i class="ti ti-bolt"></i></div>
      </div>
    </div>
    <div class="page-body">
      <div class="card">
        <div class="card-label"><i class="ti ti-device-mobile"></i> Select Platform</div>
        <div class="platform-row" id="create-plat">
          <div class="ptag sel" data-val="youtube"><i class="ti ti-brand-youtube"></i> YouTube</div>
          <div class="ptag" data-val="instagram"><i class="ti ti-brand-instagram"></i> Instagram</div>
          <div class="ptag" data-val="linkedin"><i class="ti ti-brand-linkedin"></i> LinkedIn</div>
          <div class="ptag" data-val="twitter"><i class="ti ti-brand-x"></i> Twitter</div>
          <div class="ptag" data-val="whatsapp"><i class="ti ti-brand-whatsapp"></i> WhatsApp</div>
        </div>
        <div class="field">
          <label><i class="ti ti-bulb"></i> Topic or Idea</label>
          <input type="text" id="create-topic" placeholder="e.g. AI is replacing designers in 2025">
        </div>
        <button class="btn btn-primary" id="create-btn" onclick="runCreate()">
          <i class="ti ti-bolt"></i> Generate Everything
        </button>
        <div class="loader" id="create-loader"><div class="spin"></div> Analysing trends · Writing post · Finding hashtags · Predicting virality...</div>
      </div>

      <div class="multi-wrap" id="create-result">
        <div class="result-section">
          <div class="result-section-head">
            <div class="result-label-sm"><i class="ti ti-chart-bar"></i> Trend Analysis</div>
            <button class="copy-btn" onclick="copyBox('res-trend')"><i class="ti ti-copy"></i> Copy</button>
          </div>
          <div class="result-box" id="res-trend"></div>
        </div>
        <div class="result-section">
          <div class="result-section-head">
            <div class="result-label-sm"><i class="ti ti-pencil"></i> Post</div>
            <button class="copy-btn" onclick="copyBox('res-post')"><i class="ti ti-copy"></i> Copy</button>
          </div>
          <div class="result-box" id="res-post"></div>
        </div>
        <div class="result-section">
          <div class="result-section-head">
            <div class="result-label-sm"><i class="ti ti-hash"></i> Hashtags</div>
            <button class="copy-btn" onclick="copyBox('res-hashtags')"><i class="ti ti-copy"></i> Copy</button>
          </div>
          <div class="result-box" id="res-hashtags"></div>
        </div>
        <div class="result-section">
          <div class="result-section-head">
            <div class="result-label-sm"><i class="ti ti-rocket"></i> Virality Prediction</div>
            <button class="copy-btn" onclick="copyBox('res-virality')"><i class="ti ti-copy"></i> Copy</button>
          </div>
          <div class="result-box" id="res-virality"></div>
        </div>
      </div>
    </div>
  </div>

  <!-- POST -->
  <div id="page-post" class="page">
    <div class="page-head">
      <div class="page-head-inner">
        <div>
          <div class="page-eyebrow">Content Creation</div>
          <div class="page-title">Write Post</div>
          <div class="page-sub">Platform-optimised social media copy</div>
        </div>
        <div class="page-icon"><i class="ti ti-pencil"></i></div>
      </div>
    </div>
    <div class="page-body">
      <div class="card">
        <div class="card-label"><i class="ti ti-device-mobile"></i> Platform</div>
        <div class="platform-row" id="post-plat">
          <div class="ptag sel" data-val="youtube"><i class="ti ti-brand-youtube"></i> YouTube</div>
          <div class="ptag" data-val="instagram"><i class="ti ti-brand-instagram"></i> Instagram</div>
          <div class="ptag" data-val="linkedin"><i class="ti ti-brand-linkedin"></i> LinkedIn</div>
          <div class="ptag" data-val="twitter"><i class="ti ti-brand-x"></i> Twitter</div>
          <div class="ptag" data-val="whatsapp"><i class="ti ti-brand-whatsapp"></i> WhatsApp</div>
        </div>
        <div class="field">
          <label><i class="ti ti-bulb"></i> Topic</label>
          <input type="text" id="post-topic" placeholder="e.g. Why I quit my 9-5 job">
        </div>
        <button class="btn btn-primary" id="post-btn" onclick="runPost()">
          <i class="ti ti-pencil"></i> Write Post
        </button>
        <div class="loader" id="post-loader"><div class="spin"></div> Writing your post...</div>
      </div>
      <div class="result-wrap" id="post-result">
        <div class="result-header">
          <div class="result-label-sm"><i class="ti ti-file-text"></i> Result</div>
          <button class="copy-btn" onclick="copyBox('post-box')"><i class="ti ti-copy"></i> Copy</button>
        </div>
        <div class="result-box" id="post-box"></div>
      </div>
    </div>
  </div>

  <!-- HOOK -->
  <div id="page-hook" class="page">
    <div class="page-head">
      <div class="page-head-inner">
        <div>
          <div class="page-eyebrow">Content Creation</div>
          <div class="page-title">Hook Generator</div>
          <div class="page-sub">5 scroll-stopping opening lines for any topic</div>
        </div>
        <div class="page-icon"><i class="ti ti-fish-hook"></i></div>
      </div>
    </div>
    <div class="page-body">
      <div class="card">
        <div class="field">
          <label><i class="ti ti-bulb"></i> Topic</label>
          <input type="text" id="hook-topic" placeholder="e.g. Morning routines that changed my life">
        </div>
        <button class="btn btn-primary" id="hook-btn" onclick="runHook()">
          <i class="ti ti-fish-hook"></i> Generate Hooks
        </button>
        <div class="loader" id="hook-loader"><div class="spin"></div> Crafting scroll-stopping hooks...</div>
      </div>
      <div class="result-wrap" id="hook-result">
        <div class="result-header">
          <div class="result-label-sm"><i class="ti ti-list-numbers"></i> 5 Hooks</div>
          <button class="copy-btn" onclick="copyBox('hook-box')"><i class="ti ti-copy"></i> Copy</button>
        </div>
        <div class="result-box" id="hook-box"></div>
      </div>
    </div>
  </div>

  <!-- SCRIPT -->
  <div id="page-script" class="page">
    <div class="page-head">
      <div class="page-head-inner">
        <div>
          <div class="page-eyebrow">Content Creation</div>
          <div class="page-title">Script Writer</div>
          <div class="page-sub">Full 30–60 second reel script with stage directions</div>
        </div>
        <div class="page-icon"><i class="ti ti-movie"></i></div>
      </div>
    </div>
    <div class="page-body">
      <div class="card">
        <div class="field">
          <label><i class="ti ti-bulb"></i> Topic</label>
          <input type="text" id="script-topic" placeholder="e.g. 3 habits that doubled my productivity">
        </div>
        <button class="btn btn-primary" id="script-btn" onclick="runScript()">
          <i class="ti ti-movie"></i> Write Script
        </button>
        <div class="loader" id="script-loader"><div class="spin"></div> Writing your script...</div>
      </div>
      <div class="result-wrap" id="script-result">
        <div class="result-header">
          <div class="result-label-sm"><i class="ti ti-script"></i> Script</div>
          <button class="copy-btn" onclick="copyBox('script-box')"><i class="ti ti-copy"></i> Copy</button>
        </div>
        <div class="result-box" id="script-box"></div>
      </div>
    </div>
  </div>

  <!-- CAPTION -->
  <div id="page-caption" class="page">
    <div class="page-head">
      <div class="page-head-inner">
        <div>
          <div class="page-eyebrow">Content Creation</div>
          <div class="page-title">Caption Writer</div>
          <div class="page-sub">AI caption for any photo or video</div>
        </div>
        <div class="page-icon"><i class="ti ti-camera"></i></div>
      </div>
    </div>
    <div class="page-body">
      <div class="card">
        <div class="card-label"><i class="ti ti-device-mobile"></i> Platform</div>
        <div class="platform-row" id="caption-plat">
          <div class="ptag sel" data-val="instagram"><i class="ti ti-brand-instagram"></i> Instagram</div>
          <div class="ptag" data-val="youtube"><i class="ti ti-brand-youtube"></i> YouTube</div>
          <div class="ptag" data-val="linkedin"><i class="ti ti-brand-linkedin"></i> LinkedIn</div>
          <div class="ptag" data-val="twitter"><i class="ti ti-brand-x"></i> Twitter</div>
          <div class="ptag" data-val="whatsapp"><i class="ti ti-brand-whatsapp"></i> WhatsApp</div>
        </div>
        <div class="field">
          <label><i class="ti ti-photo"></i> Describe your photo or video</label>
          <textarea id="caption-desc" placeholder="e.g. A sunset photo at the beach with golden hour lighting, standing on rocks"></textarea>
        </div>
        <button class="btn btn-primary" id="caption-btn" onclick="runCaption()">
          <i class="ti ti-camera"></i> Write Caption
        </button>
        <div class="loader" id="caption-loader"><div class="spin"></div> Writing caption...</div>
      </div>
      <div class="result-wrap" id="caption-result">
        <div class="result-header">
          <div class="result-label-sm"><i class="ti ti-file-text"></i> Caption</div>
          <button class="copy-btn" onclick="copyBox('caption-box')"><i class="ti ti-copy"></i> Copy</button>
        </div>
        <div class="result-box" id="caption-box"></div>
      </div>
    </div>
  </div>

  <!-- TRENDSCORE -->
  <div id="page-trendscore" class="page">
    <div class="page-head">
      <div class="page-head-inner">
        <div>
          <div class="page-eyebrow">Analytics</div>
          <div class="page-title">Trend Score</div>
          <div class="page-sub">Score, momentum and best platform for your topic</div>
        </div>
        <div class="page-icon"><i class="ti ti-trending-up"></i></div>
      </div>
    </div>
    <div class="page-body">
      <div class="card">
        <div class="field">
          <label><i class="ti ti-search"></i> Topic to analyse</label>
          <input type="text" id="trend-topic" placeholder="e.g. AI art controversy">
        </div>
        <button class="btn btn-primary" id="trend-btn" onclick="runTrend()">
          <i class="ti ti-chart-bar"></i> Analyse Trend
        </button>
        <div class="loader" id="trend-loader"><div class="spin"></div> Analysing trend signals...</div>
      </div>
      <div class="result-wrap" id="trend-result">
        <div class="result-header">
          <div class="result-label-sm"><i class="ti ti-report-analytics"></i> Analysis</div>
          <button class="copy-btn" onclick="copyBox('trend-box')"><i class="ti ti-copy"></i> Copy</button>
        </div>
        <div class="result-box" id="trend-box"></div>
      </div>
    </div>
  </div>

  <!-- HASHTAGS -->
  <div id="page-hashtags" class="page">
    <div class="page-head">
      <div class="page-head-inner">
        <div>
          <div class="page-eyebrow">Analytics</div>
          <div class="page-title">Hashtag Finder</div>
          <div class="page-sub">Platform-optimised hashtag sets grouped by reach</div>
        </div>
        <div class="page-icon"><i class="ti ti-hash"></i></div>
      </div>
    </div>
    <div class="page-body">
      <div class="card">
        <div class="card-label"><i class="ti ti-device-mobile"></i> Platform</div>
        <div class="platform-row" id="hashtags-plat">
          <div class="ptag sel" data-val="instagram"><i class="ti ti-brand-instagram"></i> Instagram</div>
          <div class="ptag" data-val="youtube"><i class="ti ti-brand-youtube"></i> YouTube</div>
          <div class="ptag" data-val="linkedin"><i class="ti ti-brand-linkedin"></i> LinkedIn</div>
          <div class="ptag" data-val="twitter"><i class="ti ti-brand-x"></i> Twitter</div>
        </div>
        <div class="field">
          <label><i class="ti ti-bulb"></i> Topic</label>
          <input type="text" id="hashtags-topic" placeholder="e.g. fitness motivation">
        </div>
        <button class="btn btn-primary" id="hashtags-btn" onclick="runHashtags()">
          <i class="ti ti-hash"></i> Find Hashtags
        </button>
        <div class="loader" id="hashtags-loader"><div class="spin"></div> Finding optimal hashtags...</div>
      </div>
      <div class="result-wrap" id="hashtags-result">
        <div class="result-header">
          <div class="result-label-sm"><i class="ti ti-tags"></i> Hashtags</div>
          <button class="copy-btn" onclick="copyBox('hashtags-box')"><i class="ti ti-copy"></i> Copy</button>
        </div>
        <div class="result-box" id="hashtags-box"></div>
      </div>
    </div>
  </div>

  <!-- VOICE -->
  <div id="page-voice" class="page">
    <div class="page-head">
      <div class="page-head-inner">
        <div>
          <div class="page-eyebrow">Personalise</div>
          <div class="page-title">Brand Voice</div>
          <div class="page-sub">Set your writing style — all future content will match it</div>
        </div>
        <div class="page-icon"><i class="ti ti-microphone"></i></div>
      </div>
    </div>
    <div class="page-body">
      <div class="voice-grid">
        <div class="card">
          <div class="card-label"><i class="ti ti-device-floppy"></i> Save Voice</div>
          <div class="field">
            <label><i class="ti ti-id-badge"></i> Your Discord User ID</label>
            <input type="text" id="voice-uid" placeholder="e.g. 123456789012345678">
          </div>
          <div class="field">
            <label><i class="ti ti-writing"></i> Voice Description</label>
            <textarea id="voice-desc" placeholder="e.g. Bold, witty, and direct with a Gen-Z tone. Never corporate-speak."></textarea>
          </div>
          <button class="btn btn-primary" id="voice-save-btn" onclick="saveVoice()">
            <i class="ti ti-device-floppy"></i> Save Voice
          </button>
          <div class="loader" id="voice-loader"><div class="spin"></div> Saving...</div>
        </div>
        <div class="card">
          <div class="card-label"><i class="ti ti-eye"></i> View Saved Voice</div>
          <div class="field">
            <label><i class="ti ti-id-badge"></i> Discord User ID</label>
            <input type="text" id="voice-uid2" placeholder="Enter your user ID">
          </div>
          <button class="btn btn-ghost" style="margin-bottom:16px" id="voice-load-btn" onclick="loadVoice()">
            <i class="ti ti-eye"></i> Load My Voice
          </button>
          <div class="result-wrap" id="voice-result">
            <div class="result-box" id="voice-box"></div>
          </div>
          <div style="margin-top:16px;padding-top:16px;border-top:1px solid var(--paper3)">
            <div style="font-size:12px;color:var(--ink3);font-family:var(--mono);margin-bottom:6px;text-transform:uppercase;letter-spacing:0.5px">How to find your ID</div>
            <div style="font-size:13px;color:var(--ink3);line-height:1.6">Enable Developer Mode in Discord Settings → Advanced, then right-click your name and select Copy User ID.</div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- CHAT -->
  <div id="page-chat" class="page">
    <div class="page-head">
      <div class="page-head-inner">
        <div>
          <div class="page-eyebrow">Assistant</div>
          <div class="page-title">Chat with Beru</div>
          <div class="page-sub">Ask for content ideas, strategy advice, or command help</div>
        </div>
        <div class="page-icon"><i class="ti ti-message-chatbot"></i></div>
      </div>
    </div>
    <div class="page-body">
      <div class="chat-area" id="chat-window">
        <div class="msg bot">
          <div class="avatar"><i class="ti ti-sparkles" style="font-size:15px"></i></div>
          <div class="bubble">Hey! I'm Beru. Ask me anything about content creation, social media strategy, or what I can do for you.</div>
        </div>
      </div>
      <div class="chat-row">
        <div class="field">
          <input type="text" id="chat-input" placeholder="Ask Beru something..." onkeydown="if(event.key==='Enter')sendChat()">
        </div>
        <button class="btn btn-primary" style="flex-shrink:0" onclick="sendChat()">
          <i class="ti ti-send"></i>
        </button>
      </div>
    </div>
  </div>

  <!-- COMMANDS -->
  <div id="page-commands" class="page">
    <div class="page-head">
      <div class="page-head-inner">
        <div>
          <div class="page-eyebrow">Reference</div>
          <div class="page-title">Bot Commands</div>
          <div class="page-sub">All commands use the <code style="font-family:var(--mono);background:var(--paper2);padding:2px 7px;border-radius:5px;font-size:13px">,</code> prefix in Discord</div>
        </div>
        <div class="page-icon"><i class="ti ti-terminal-2"></i></div>
      </div>
    </div>
    <div class="page-body">
      <div class="cmd-grid">
        <div class="cmd">
          <div class="cmd-top">
            <div class="cmd-icon"><i class="ti ti-bolt"></i></div>
            <div class="cmd-name">,create</div>
          </div>
          <div class="cmd-desc">All-in-one: trend + post + hashtags + virality in one command</div>
          <div class="cmd-usage">,create linkedin your topic here</div>
        </div>
        <div class="cmd">
          <div class="cmd-top">
            <div class="cmd-icon"><i class="ti ti-pencil"></i></div>
            <div class="cmd-name">,post</div>
          </div>
          <div class="cmd-desc">Generate a platform-ready social media post</div>
          <div class="cmd-usage">,post instagram your topic</div>
        </div>
        <div class="cmd">
          <div class="cmd-top">
            <div class="cmd-icon"><i class="ti ti-fish-hook"></i></div>
            <div class="cmd-name">,hook</div>
          </div>
          <div class="cmd-desc">5 scroll-stopping opening lines for your topic</div>
          <div class="cmd-usage">,hook your topic here</div>
        </div>
        <div class="cmd">
          <div class="cmd-top">
            <div class="cmd-icon"><i class="ti ti-movie"></i></div>
            <div class="cmd-name">,script</div>
          </div>
          <div class="cmd-desc">Full 30–60s reel script with stage directions</div>
          <div class="cmd-usage">,script your topic here</div>
        </div>
        <div class="cmd">
          <div class="cmd-top">
            <div class="cmd-icon"><i class="ti ti-trending-up"></i></div>
            <div class="cmd-name">,trendscore</div>
          </div>
          <div class="cmd-desc">Trend score, momentum and best platform</div>
          <div class="cmd-usage">,trendscore your topic</div>
        </div>
        <div class="cmd">
          <div class="cmd-top">
            <div class="cmd-icon"><i class="ti ti-hash"></i></div>
            <div class="cmd-name">,hashtags</div>
          </div>
          <div class="cmd-desc">Platform-optimised hashtag sets grouped by reach</div>
          <div class="cmd-usage">,hashtags instagram fitness</div>
        </div>
        <div class="cmd">
          <div class="cmd-top">
            <div class="cmd-icon"><i class="ti ti-camera"></i></div>
            <div class="cmd-name">,caption</div>
          </div>
          <div class="cmd-desc">AI caption for any photo or video</div>
          <div class="cmd-usage">,caption instagram sunset beach photo</div>
        </div>
        <div class="cmd">
          <div class="cmd-top">
            <div class="cmd-icon"><i class="ti ti-microphone"></i></div>
            <div class="cmd-name">,setvoice</div>
          </div>
          <div class="cmd-desc">Save your personal writing style for all future posts</div>
          <div class="cmd-usage">,setvoice bold and witty tone</div>
        </div>
        <div class="cmd">
          <div class="cmd-top">
            <div class="cmd-icon"><i class="ti ti-eye"></i></div>
            <div class="cmd-name">,myvoice</div>
          </div>
          <div class="cmd-desc">View your currently saved brand voice</div>
          <div class="cmd-usage">,myvoice</div>
        </div>
        <div class="cmd">
          <div class="cmd-top">
            <div class="cmd-icon"><i class="ti ti-video"></i></div>
            <div class="cmd-name">,video</div>
          </div>
          <div class="cmd-desc">AI video generation with 60s cooldown and caching</div>
          <div class="cmd-usage">,video a robot dancing in Tokyo</div>
        </div>
        <div class="cmd">
          <div class="cmd-top">
            <div class="cmd-icon"><i class="ti ti-chart-bar"></i></div>
            <div class="cmd-name">,poll</div>
          </div>
          <div class="cmd-desc">Create a thumbs up / thumbs down poll in Discord</div>
          <div class="cmd-usage">,poll Is AI better than humans?</div>
        </div>
        <div class="cmd">
          <div class="cmd-top">
            <div class="cmd-icon"><i class="ti ti-help"></i></div>
            <div class="cmd-name">,help</div>
          </div>
          <div class="cmd-desc">Show all available commands with usage examples</div>
          <div class="cmd-usage">,help</div>
        </div>
      </div>
    </div>
  </div>

</main>

<script>
function goto(page, el) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.getElementById('page-' + page).classList.add('active');
  if (el) el.classList.add('active');
  window.scrollTo(0, 0);
}

document.querySelectorAll('.platform-row').forEach(row => {
  row.querySelectorAll('.ptag').forEach(tag => {
    tag.addEventListener('click', () => {
      row.querySelectorAll('.ptag').forEach(t => t.classList.remove('sel'));
      tag.classList.add('sel');
    });
  });
});

function getPlat(id) {
  const sel = document.querySelector('#' + id + ' .ptag.sel');
  return sel ? sel.dataset.val : 'instagram';
}

function loading(id, on) { document.getElementById(id).classList.toggle('visible', on); }
function setDisabled(id, v) { document.getElementById(id).disabled = v; }

function showResult(wrapId, boxId, text) {
  document.getElementById(boxId).textContent = text;
  document.getElementById(wrapId).classList.add('visible');
}

function copyBox(id) {
  const text = document.getElementById(id).textContent;
  navigator.clipboard.writeText(text).then(() => {
    const btns = document.querySelectorAll('.copy-btn');
    btns.forEach(b => { if (b.getAttribute('onclick') && b.getAttribute('onclick').includes(id)) {
      const orig = b.innerHTML;
      b.innerHTML = '<i class="ti ti-check"></i> Copied';
      setTimeout(() => b.innerHTML = orig, 1500);
    }});
  });
}

async function api(endpoint, body) {
  const r = await fetch(endpoint, {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(body)
  });
  return r.json();
}

async function runCreate() {
  const topic = document.getElementById('create-topic').value.trim();
  const platform = getPlat('create-plat');
  if (!topic) { alert('Please enter a topic.'); return; }
  loading('create-loader', true); setDisabled('create-btn', true);
  document.getElementById('create-result').classList.remove('visible');
  try {
    const d = await api('/api/create', {platform, topic});
    document.getElementById('res-trend').textContent = d.trendscore || d.error || '';
    document.getElementById('res-post').textContent = d.post || '';
    document.getElementById('res-hashtags').textContent = d.hashtags || '';
    document.getElementById('res-virality').textContent = d.virality || '';
    document.getElementById('create-result').classList.add('visible');
  } catch(e) { alert('Error: ' + e.message); }
  loading('create-loader', false); setDisabled('create-btn', false);
}

async function runPost() {
  const topic = document.getElementById('post-topic').value.trim();
  const platform = getPlat('post-plat');
  if (!topic) { alert('Please enter a topic.'); return; }
  loading('post-loader', true); setDisabled('post-btn', true);
  try {
    const d = await api('/api/post', {platform, topic});
    showResult('post-result', 'post-box', d.result || d.error);
  } catch(e) { alert('Error: ' + e.message); }
  loading('post-loader', false); setDisabled('post-btn', false);
}

async function runHook() {
  const topic = document.getElementById('hook-topic').value.trim();
  if (!topic) { alert('Please enter a topic.'); return; }
  loading('hook-loader', true); setDisabled('hook-btn', true);
  try {
    const d = await api('/api/hook', {topic});
    showResult('hook-result', 'hook-box', d.result || d.error);
  } catch(e) { alert('Error: ' + e.message); }
  loading('hook-loader', false); setDisabled('hook-btn', false);
}

async function runScript() {
  const topic = document.getElementById('script-topic').value.trim();
  if (!topic) { alert('Please enter a topic.'); return; }
  loading('script-loader', true); setDisabled('script-btn', true);
  try {
    const d = await api('/api/script', {topic});
    showResult('script-result', 'script-box', d.result || d.error);
  } catch(e) { alert('Error: ' + e.message); }
  loading('script-loader', false); setDisabled('script-btn', false);
}

async function runCaption() {
  const desc = document.getElementById('caption-desc').value.trim();
  const platform = getPlat('caption-plat');
  if (!desc) { alert('Please describe your photo or video.'); return; }
  loading('caption-loader', true); setDisabled('caption-btn', true);
  try {
    const d = await api('/api/caption', {platform, description: desc});
    showResult('caption-result', 'caption-box', d.result || d.error);
  } catch(e) { alert('Error: ' + e.message); }
  loading('caption-loader', false); setDisabled('caption-btn', false);
}

async function runTrend() {
  const topic = document.getElementById('trend-topic').value.trim();
  if (!topic) { alert('Please enter a topic.'); return; }
  loading('trend-loader', true); setDisabled('trend-btn', true);
  try {
    const d = await api('/api/trendscore', {topic});
    showResult('trend-result', 'trend-box', d.result || d.error);
  } catch(e) { alert('Error: ' + e.message); }
  loading('trend-loader', false); setDisabled('trend-btn', false);
}

async function runHashtags() {
  const topic = document.getElementById('hashtags-topic').value.trim();
  const platform = getPlat('hashtags-plat');
  if (!topic) { alert('Please enter a topic.'); return; }
  loading('hashtags-loader', true); setDisabled('hashtags-btn', true);
  try {
    const d = await api('/api/hashtags', {platform, topic});
    showResult('hashtags-result', 'hashtags-box', d.result || d.error);
  } catch(e) { alert('Error: ' + e.message); }
  loading('hashtags-loader', false); setDisabled('hashtags-btn', false);
}

async function saveVoice() {
  const uid = document.getElementById('voice-uid').value.trim();
  const desc = document.getElementById('voice-desc').value.trim();
  if (!uid || !desc) { alert('Please fill in both fields.'); return; }
  loading('voice-loader', true); setDisabled('voice-save-btn', true);
  try {
    const d = await api('/api/setvoice', {user_id: uid, description: desc});
    alert(d.result || d.error);
  } catch(e) { alert('Error: ' + e.message); }
  loading('voice-loader', false); setDisabled('voice-save-btn', false);
}

async function loadVoice() {
  const uid = document.getElementById('voice-uid2').value.trim();
  if (!uid) { alert('Please enter your Discord user ID.'); return; }
  setDisabled('voice-load-btn', true);
  try {
    const d = await api('/api/getvoice', {user_id: uid});
    showResult('voice-result', 'voice-box', d.result || 'No brand voice saved yet.');
  } catch(e) { alert('Error: ' + e.message); }
  setDisabled('voice-load-btn', false);
}

const chatHistory = [];
async function sendChat() {
  const input = document.getElementById('chat-input');
  const msg = input.value.trim();
  if (!msg) return;
  input.value = '';
  appendMsg('user', msg);
  chatHistory.push({role: 'user', content: msg});
  try {
    const d = await api('/api/chat', {messages: chatHistory});
    const reply = d.result || d.error || 'Something went wrong.';
    appendMsg('bot', reply);
    chatHistory.push({role: 'assistant', content: reply});
  } catch(e) { appendMsg('bot', 'Error: ' + e.message); }
}

function appendMsg(who, text) {
  const win = document.getElementById('chat-window');
  const div = document.createElement('div');
  div.className = 'msg ' + who;
  const icon = who === 'bot' ? '<i class="ti ti-sparkles" style="font-size:15px"></i>' : '<i class="ti ti-user" style="font-size:15px"></i>';
  div.innerHTML = `<div class="avatar">${icon}</div><div class="bubble">${text.replace(/</g,'&lt;')}</div>`;
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
        return jsonify({"result": f"Brand voice saved successfully."})
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
    system_msg = {
        "role": "system",
        "content": (
            "You are Beru, an AI-powered social media content assistant. "
            "You help with content creation, social media strategy, hooks, scripts, captions, and hashtags. "
            "You are knowledgeable about YouTube, Instagram, LinkedIn, Twitter, and WhatsApp. "
            "Be concise, sharp, and genuinely helpful. Your Discord bot prefix is ','."
        )
    }
    try:
        result = utils.groq_complete([system_msg] + messages, max_tokens=500, temperature=0.8)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def run_dashboard(port=5000):
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
