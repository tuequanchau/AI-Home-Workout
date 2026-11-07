from __future__ import annotations


def get_summary_html() -> str:
    """Return the summary screen exported from Stitch."""
    return r"""<!DOCTYPE html><html class="dark h-full" lang="vi"><head>
<meta charset="utf-8">
<meta content="width=device-width, initial-scale=1.0" name="viewport">
<title>Tổng Kết Buổi Tập | Smurf Fitness AI</title>
<!-- Tailwind CSS v3 with Forms and Container Queries -->
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            brand: {
              cyan: '#00d2ff',
              neon: '#a3e635',
              appleGreen: '#34c759',
              darkBg: '#08080a',
              cardBg: '#131316',
              surface: '#1c1c1e'
            }
          },
          fontFamily: {
            sans: ['-apple-system', 'BlinkMacSystemFont', 'SF Pro Display', 'SF Pro Text', 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', 'sans-serif'],
            mono: ['SF Mono', 'Menlo', 'Monaco', 'Courier New', 'monospace']
          },
          boxShadow: {
            'glow-neon': '0 0 30px rgba(163, 230, 53, 0.28)',
            'glow-cyan': '0 0 35px rgba(0, 210, 255, 0.22)',
            'glow-apple': '0 0 25px rgba(52, 199, 89, 0.35)'
          }
        }
      }
    }
  </script>
<!-- Google Fonts: Inter -->
<link href="https://fonts.googleapis.com" rel="preconnect">
<link crossorigin="" href="https://fonts.gstatic.com" rel="preconnect">
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&amp;display=swap" rel="stylesheet">
<style data-purpose="base-styling">
    body {
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
      background-color: #060608;
      color: #f5f5f7;
      overflow-x: hidden;
    }
    
    /* Apple Smooth Backdrop Blur */
    .glass-panel {
      background: rgba(22, 22, 26, 0.78);
      backdrop-filter: blur(28px);
      -webkit-backdrop-filter: blur(28px);
      border: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    .glass-card {
      background: rgba(30, 30, 34, 0.55);
      backdrop-filter: blur(18px);
      -webkit-backdrop-filter: blur(18px);
      border: 1px solid rgba(255, 255, 255, 0.06);
    }

    /* Ambient Background Glow */
    .ambient-glow {
      position: fixed;
      width: 650px;
      height: 650px;
      border-radius: 50%;
      filter: blur(140px);
      pointer-events: none;
      z-index: 0;
      opacity: 0.15;
    }
  </style>
</head>
<body class="min-h-full flex flex-col justify-between selection:bg-brand-neon selection:text-black relative">
<!-- Ambient Light Circles -->
<div class="ambient-glow bg-[#34c759] top-[-150px] left-1/2 -translate-x-1/2"></div>
<div class="ambient-glow bg-[#00d2ff] bottom-[-100px] right-[-100px]"></div>
<!-- BEGIN: TopHeader -->
<header class="w-full relative z-20 px-6 lg:px-12 py-5 flex items-center justify-between border-b border-white/[0.06] bg-[#060608]/80 backdrop-blur-xl">
<!-- Brand Logo and App Tagline -->
<div class="flex items-center gap-3.5" data-purpose="brand-container">
<img alt="Smurf Fitness Logo" class="h-16 w-16 md:h-20 md:w-20 rounded-2xl object-cover shadow-lg border border-white/20 transition-all duration-300" src="https://lh3.googleusercontent.com/aida-public/AB6AXuAIVtQWvcwkOyjtD4jMYzFFXu1-hWb73ctyu5sl7Ksax6g9cPtQlMw7e5EtsYuHH7Xf20SHWibNaUPt3WZHG65UR_QopmZ8ec2C9YIBTrXows57iabSBCrx_8AGy_vFphePxps3bw7vtdw-EH1NGeiZgSx4d3q9zz3cjsSTbqAJjkMdVRY-5pjTAN7lUdfV1kwAbe6o4PwMrJVPcU9PlSZJzuiGJUT6n63XIvogOSODHJYHgwc3wdsBxQ">
<div class="flex flex-col">
<div class="flex items-center gap-2">
<span class="text-white font-extrabold tracking-tight text-xl md:text-2xl leading-none">SMURF FITNESS</span>

</div>

</div>
</div>
<!-- Status Badge -->
<div class="flex items-center gap-2.5 px-4 py-2 rounded-full glass-card border border-white/10 shadow-sm" data-purpose="completion-badge">
<span class="flex h-2.5 w-2.5 relative">
<span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-appleGreen opacity-75"></span>
<span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-brand-appleGreen"></span>
</span>
<span class="text-xs uppercase tracking-wider font-semibold text-white/90">Buổi tập hoàn tất</span>
</div>
</header>
<!-- END: TopHeader -->
<!-- BEGIN: MainContent -->
<main id="summary-main" class="relative z-10 flex-1 flex items-center justify-center px-4 py-8 md:py-12">
<div class="w-full max-w-4xl mx-auto">
<!-- Central Summary Glass Container -->
<section id="summary-card" class="glass-panel rounded-[32px] md:rounded-[40px] p-6 sm:p-10 md:p-12 relative overflow-hidden shadow-2xl border border-white/10">
<!-- Top Visual Indicator & Header Titles -->
<div class="text-center flex flex-col items-center mb-10" data-purpose="summary-header">
<!-- Animated Checkmark Icon Glow -->
<div class="relative mb-4 flex items-center justify-center">
<div class="absolute inset-0 rounded-full bg-brand-appleGreen/20 blur-xl"></div>
<div class="relative w-16 h-16 rounded-full bg-gradient-to-b from-[#34c759]/20 to-[#34c759]/5 border border-[#34c759]/40 flex items-center justify-center text-[#34c759] shadow-glow-apple">
<svg class="w-8 h-8 stroke-[2.5]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
<path d="M5 13l4 4L19 7" stroke-linecap="round" stroke-linejoin="round"></path>
</svg>
</div>
</div>
<!-- Finished Subtitle Badge -->
<span class="text-xs md:text-sm uppercase tracking-[0.2em] font-bold text-brand-neon mb-2">
            BẠN ĐÃ HOÀN THÀNH
          </span>
<!-- Main Greeting Title -->
<h1 class="text-4xl sm:text-5xl md:text-6xl font-extrabold text-white tracking-tight mb-3">
            Làm tốt lắm!
          </h1>
<p id="summary-exercise" class="text-base text-white/60">Squat</p>
<!-- Exercise Meta Details -->

</div>
<!-- 3 Performance Metric Cards -->
<div class="grid grid-cols-1 md:grid-cols-3 gap-4 lg:gap-5 mb-8" data-purpose="metrics-grid">
<!-- Metric Card 1: Số lần hoàn thành -->
<article class="glass-card rounded-2xl p-6 flex flex-col justify-between hover:border-brand-cyan/40 transition-all duration-300">
<div>
<p class="text-[11px] font-bold uppercase tracking-wider text-white/50 mb-3">
                Số lần hoàn thành
              </p>
<div class="flex items-baseline gap-2">
<span id="summary-reps" class="text-4xl sm:text-5xl font-black text-brand-cyan tracking-tight">0</span>
<span id="summary-reps-unit" class="text-sm font-semibold text-white/60">reps</span>
</div>
</div>
<div class="mt-4 pt-3 border-t border-white/5 flex items-center text-xs text-white/50">

</div>
</article>
<!-- Metric Card 2: Thời gian tập -->
<article class="glass-card rounded-2xl p-6 flex flex-col justify-between hover:border-white/30 transition-all duration-300">
<div>
<p class="text-[11px] font-bold uppercase tracking-wider text-white/50 mb-3">
                Thời gian tập
              </p>
<div class="flex items-baseline gap-2">
<span id="summary-duration" class="text-4xl sm:text-5xl font-mono font-extrabold text-white tracking-tight">00:00</span>
</div>
</div>
<div class="mt-4 pt-3 border-t border-white/5 flex items-center text-xs text-white/50">

</div>
</article>
<!-- Metric Card 3: Lượng calo tiêu thụ -->
<article class="glass-card rounded-2xl p-6 flex flex-col justify-between hover:border-amber-400/40 transition-all duration-300">
<div>
<div class="flex items-center justify-between mb-3">
<p class="text-[11px] font-bold uppercase tracking-wider text-white/50">
                  Lượng Calo Tiêu Thụ
                </p>

</div>
<div class="flex items-baseline gap-2">
<span class="text-4xl sm:text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-amber-400 via-orange-400 to-amber-200 tracking-tight">
                  ~68
                </span>
<span class="text-base font-bold text-amber-300/80">kcal</span>
</div>
</div>
<div class="mt-4 pt-3 border-t border-white/5 flex items-center text-xs text-white/50">

</div>
</article>
</div>
<!-- Motivational Quote & AI Pose Accuracy Feedback Banner -->
<aside class="w-full glass-card rounded-2xl p-5 mb-10 border border-white/10 bg-white/[0.02]" data-purpose="ai-feedback-banner">
<div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
<div class="flex items-center gap-3">
<span class="text-brand-neon text-lg select-none">✦</span>
<p class="text-sm text-white/80 leading-relaxed font-medium">
                Mỗi buổi tập là một bước tiến vững chắc. Cơ thể bạn đang thích nghi và trở nên khỏe mạnh hơn mỗi ngày.
              </p>
</div>

</div>
</aside>
<!-- Action CTA Buttons -->
<div class="flex flex-col sm:flex-row items-center justify-center gap-4" data-purpose="action-buttons">
<!-- Secondary Action: Tập lại -->
<a href="/workout" class="w-full sm:w-auto inline-flex items-center justify-center gap-2.5 px-8 py-3.5 rounded-full bg-white/[0.08] hover:bg-white/[0.14] text-white font-semibold text-sm tracking-wide border border-white/15 transition-all duration-200 active:scale-95" role="button">
<svg class="w-4 h-4 text-white/80" fill="none" stroke="currentColor" viewBox="0 0 24 24">
<path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
</svg>
<span class="">Tập lại</span>
</a>
<!-- Primary Action: Về trang chủ -->
<a class="w-full sm:w-auto inline-flex items-center justify-center gap-2.5 px-9 py-3.5 rounded-full bg-brand-neon hover:bg-[#bbf758] text-black font-bold text-sm tracking-wide shadow-glow-neon hover:scale-105 active:scale-95 transition-all duration-200" href="/">
<span class="">Về trang chủ</span>
<svg class="w-4 h-4 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
<path d="M14 5l7 7m0 0l-7 7m7-7H3" stroke-linecap="round" stroke-linejoin="round" stroke-width="2.2"></path>
</svg>
</a>
</div>
<!-- Footnote Info -->
<p class="text-center text-[11px] text-white/40 mt-8 font-normal">
          Dữ liệu bài tập đã được đồng bộ tự động vào hồ sơ cá nhân và bảng thành tích tuần của bạn.
        </p>
</section>
</div>
</main>
<!-- END: MainContent -->
<!-- BEGIN: BottomDockNavigation -->
<footer class="relative z-20 pb-6 pt-2 px-4 flex justify-center w-full" data-purpose="bottom-navigation">

</footer>
<!-- END: BottomDockNavigation -->


<script data-purpose="workout-result">
(() => { try { const result=JSON.parse(sessionStorage.getItem('smurfLastWorkout')||'null'); if(!result)return; const name=result.exercise==='jumping_jack'?'Jumping Jack':'Squat'; const exercise=document.getElementById('summary-exercise'); const duration=document.getElementById('summary-duration'); const reps=document.getElementById('summary-reps'); if(exercise)exercise.textContent=name; if(duration)duration.textContent=result.duration||'00:00'; if(reps)reps.textContent=String(result.reps||0); } catch (_) {} })();
</script>
<style data-purpose="summary-fit-screen">
@media (min-width: 768px) and (min-height: 680px) {
 body {height:100vh;min-height:0 !important;overflow:hidden;}
 body > header {padding-top:.5rem !important;padding-bottom:.5rem !important;backdrop-filter:none !important;-webkit-backdrop-filter:none !important;}
 #summary-main {min-height:0;padding-top:.35rem !important;padding-bottom:.35rem !important;overflow:hidden;}
 #summary-card {max-height:100%;width:min(100%,1050px);padding:.8rem 1.35rem !important;overflow:hidden;backdrop-filter:none !important;-webkit-backdrop-filter:none !important;box-shadow:0 12px 36px rgba(0,0,0,.22) !important;}
 #summary-card .glass-card {backdrop-filter:none !important;-webkit-backdrop-filter:none !important;}
 .ambient-glow {display:none !important;}
 .animate-ping {animation:none !important;}
 #summary-card [data-purpose="summary-header"] {margin-bottom:.55rem !important;}
 #summary-card [data-purpose="metrics-grid"] {margin-bottom:.6rem !important;gap:.65rem !important;}
 #summary-card [data-purpose="metrics-grid"] article {padding:.7rem !important;}
 #summary-card [data-purpose="metrics-grid"] article .mt-4 {margin-top:.4rem !important;padding-top:.4rem !important;}
 #summary-card [data-purpose="ai-feedback-banner"] {margin-bottom:.55rem !important;padding:.65rem !important;}
 #summary-card [data-purpose="action-buttons"] {gap:.65rem !important;}
 #summary-card .shadow-glow-neon {box-shadow:none !important;}
 #summary-card a {transition:none !important;}
 footer[data-purpose="bottom-navigation"] {padding-top:.25rem !important;padding-bottom:.4rem !important;}
}
@media (min-width: 768px) and (max-height: 760px) {
 #summary-card {padding:.65rem 1.2rem !important;}
 #summary-card [data-purpose="summary-header"] {margin-bottom:.4rem !important;}
 #summary-card [data-purpose="metrics-grid"] article {padding:.6rem !important;}
 #summary-card [data-purpose="summary-header"] .mb-4 {margin-bottom:.3rem !important;}
}
@media (prefers-reduced-motion: reduce) {
 *, *::before, *::after {scroll-behavior:auto !important;animation-duration:.01ms !important;animation-iteration-count:1 !important;transition-duration:.01ms !important;}
}
</style>
</body></html>"""
