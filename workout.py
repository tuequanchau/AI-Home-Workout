from __future__ import annotations


def get_workout_html() -> str:
    """Return the workout screen exported from Stitch."""
    return r"""<!DOCTYPE html><html class="dark" lang="vi"><head>
<meta charset="utf-8">
<meta content="width=device-width, initial-scale=1.0" name="viewport">
<title>Smurf Fitness - Giao Diện Tập Luyện AI Thời Gian Thực</title>
<!-- Tailwind CSS CDN -->
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<!-- Google Fonts: Inter / SF Pro aesthetic -->
<link href="https://fonts.googleapis.com" rel="preconnect">
<link crossorigin="" href="https://fonts.gstatic.com" rel="preconnect">
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&amp;family=JetBrains+Mono:wght@400;600;700&amp;display=swap" rel="stylesheet">
<script data-purpose="tailwind-config">
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          fontFamily: {
            sans: ['"Plus Jakarta Sans"', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
            mono: ['"JetBrains Mono"', 'monospace'],
          },
          colors: {
            brand: {
              cyan: '#00d2ff',
              blue: '#0071e3',
              dark: '#000000',
              card: '#1c1c1e',
              surface: '#141416',
              secondary: '#86868b'
            }
          }
        }
      }
    }
  </script>
<style data-purpose="custom-animations">
    @keyframes pulseGlow {
      0%, 100% { opacity: 0.4; transform: scale(1); }
      50% { opacity: 0.8; transform: scale(1.08); }
    }
    @keyframes scanline {
      0% { transform: translateY(-100%); }
      100% { transform: translateY(1000%); }
    }
    .pulse-glow {
      animation: pulseGlow 4s ease-in-out infinite;
    }
    .scanner-line {
      animation: scanline 7s linear infinite;
    }
    /* Subtle custom scrollbar */
    ::-webkit-scrollbar {
      width: 6px;
    }
    ::-webkit-scrollbar-track {
      background: #000000;
    }
    ::-webkit-scrollbar-thumb {
      background: #27272a;
      border-radius: 9999px;
    }
  </style>
</head>
<body class="bg-black text-white font-sans antialiased min-h-screen selection:bg-[#00d2ff]/30 selection:text-[#00d2ff] relative pb-28 overflow-x-hidden">
<!-- BEGIN: AmbientBackgroundGlow -->
<!-- Ambient background gradients inspired by Apple Dark UI -->
<div aria-hidden="true" class="fixed inset-0 pointer-events-none z-0 overflow-hidden">
<div class="absolute -top-40 left-1/4 w-[520px] h-[520px] bg-[#0071e3]/15 rounded-full blur-[140px] pulse-glow"></div>
<div class="absolute top-1/3 -right-20 w-[450px] h-[450px] bg-[#00d2ff]/10 rounded-full blur-[130px] pulse-glow" style="animation-delay: 2s;"></div>
<div class="absolute -bottom-20 left-1/3 w-[600px] h-[600px] bg-emerald-500/10 rounded-full blur-[160px]"></div>
</div>
<!-- END: AmbientBackgroundGlow -->
<!-- BEGIN: TopHeader -->
<header class="relative z-10 w-full border-b border-white/10 backdrop-blur-xl bg-black/60 sticky top-0" data-purpose="app-header">
<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
<!-- Brand Logo & Identity -->
<div class="flex items-center gap-4">
<a class="flex items-center gap-3.5 group focus:outline-none focus:ring-2 focus:ring-[#00d2ff] rounded-2xl p-1" href="#">
<img alt="SMURF FITNESS Logo" class="h-14 w-14 object-cover rounded-2xl shadow-[0_0_20px_rgba(0,210,255,0.3)] border border-white/20 transition-transform duration-300 group-hover:scale-105" src="https://lh3.googleusercontent.com/aida-public/AB6AXuAMq7rJI3aRSSeattprqkNFKoDR5fbMSrl5d_n7u7iO3KP7XfiSBlv7Ouffi9YAhKZDke4jvfPaaMd3NSPMszqK9BsqTe4JqWkn_79pNtLOEXzbaIDieE5SCDkZ5NbKk7QXe-hlswVd3B9aJ6cgUUwt_ugmiMSUhkxkAgNOvsFLDSU_8cnSXgJWCPZewsbr8zCCa1bzfWumSwF8t0bqWwF9i5xM7I7klLzwVE8TiRubMAPIy2zKldtGHQ">
<div class="flex flex-col">
<div class="flex items-center gap-2">
<span class="text-xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">SMURF FITNESS</span>

</div>

</div>
</a>
</div>
<!-- Live Status & Mode -->
<div class="flex items-center gap-3">
<div class="hidden sm:flex items-center gap-2.5 backdrop-blur-md bg-white/[0.04] border border-white/10 px-4 py-2 rounded-full shadow-inner">
<span class="relative flex h-2.5 w-2.5">
<span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#00d2ff] opacity-75"></span>
<span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-[#00d2ff]"></span>
</span>
<span class="text-xs font-semibold text-slate-200">Chế độ theo dõi động tác</span>
</div>
<div class="flex items-center gap-2 backdrop-blur-md bg-red-500/15 border border-red-500/30 px-3.5 py-1.5 rounded-full">
<span class="h-2 w-2 rounded-full bg-red-500 animate-pulse"></span>

</div>
</div>
</div>
</header>
<!-- END: TopHeader -->
<!-- BEGIN: MainContent -->
<main class="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6 lg:pt-8" id="workout-main" data-purpose="workout-screen">
<div class="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8 items-start">
<!-- BEGIN: LeftColumn_CameraHUD -->
<!-- Large AI Vision Camera Feed Container -->
<section aria-label="Khu vực theo dõi camera AI" class="lg:col-span-8 flex flex-col gap-4">
<div class="w-full rounded-3xl border border-white/10 relative overflow-hidden flex flex-col justify-between p-6 h-[calc(100vh-170px)] min-h-[640px] bg-gradient-to-b from-[#0b0e14] via-[#0f141c] to-[#07090d] shadow-[0_25px_60px_-15px_rgba(0,0,0,0.9)]"><div class="relative z-20 flex items-center justify-between w-full"><div class="flex items-center gap-2 backdrop-blur-md bg-black/70 px-4 py-2 rounded-full border border-white/15 shadow-lg"><span class="h-2 w-2 rounded-full bg-red-500 animate-ping"></span><span class="text-xs font-medium tracking-wide text-white">🔴 LIVE CAM</span><span class="text-[10px] text-[#86868b] border-l border-white/20 pl-2">60 FPS</span></div><div class="flex items-center gap-2 backdrop-blur-md bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 px-3.5 py-1.5 rounded-full text-xs font-semibold shadow-lg"><svg class="w-3.5 h-3.5 fill-current" viewBox="0 0 20 20"><path clip-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" fill-rule="evenodd"></path></svg><span class="">Trạng thái: Khung hình tốt</span></div></div><div class="relative z-10 w-full flex-1 flex flex-col items-center justify-center text-center select-none py-4" data-purpose="pose-skeleton-visualization"><div class="relative w-72 h-80 flex items-center justify-center"><div class="absolute w-52 h-52 bg-[#00d2ff]/10 rounded-full blur-2xl pointer-events-none"></div><svg class="w-full h-full drop-shadow-[0_0_15px_rgba(0,210,255,0.7)]" fill="none" stroke="#22c55e" stroke-linecap="round" stroke-linejoin="round" stroke-width="4.5" viewBox="0 0 240 280"><circle cx="120" cy="40" fill="#22c55e" fill-opacity="0.25" r="14" stroke="#22c55e" stroke-width="3"></circle><line stroke="#22c55e" x1="120" x2="120" y1="54" y2="82"></line><line stroke="#22c55e" x1="120" x2="116" y1="82" y2="135"></line><line stroke="#22c55e" x1="90" x2="150" y1="88" y2="88"></line><line stroke="#22c55e" x1="90" x2="70" y1="88" y2="122"></line><line stroke="#22c55e" x1="70" x2="98" y1="122" y2="138"></line><line stroke="#22c55e" x1="150" x2="170" y1="88" y2="122"></line><line stroke="#22c55e" x1="170" x2="142" y1="122" y2="138"></line><line stroke="#22c55e" x1="96" x2="136" y1="135" y2="135"></line><line stroke="#00d2ff" stroke-width="5" x1="96" x2="72" y1="135" y2="188"></line><line stroke="#00d2ff" stroke-width="5" x1="136" x2="162" y1="135" y2="188"></line><line stroke="#22c55e" x1="72" x2="78" y1="188" y2="245"></line><line stroke="#22c55e" x1="162" x2="156" y1="188" y2="245"></line><line stroke="#22c55e" stroke-width="4" x1="78" x2="62" y1="245" y2="252"></line><line stroke="#22c55e" stroke-width="4" x1="156" x2="172" y1="245" y2="252"></line><circle cx="120" cy="82" fill="#ffffff" r="5" stroke="#22c55e" stroke-width="2"></circle><circle cx="90" cy="88" fill="#ffffff" r="4.5" stroke="#22c55e" stroke-width="2"></circle><circle cx="150" cy="88" fill="#ffffff" r="4.5" stroke="#22c55e" stroke-width="2"></circle><circle cx="70" cy="122" fill="#ffffff" r="4" stroke="#22c55e" stroke-width="2"></circle><circle cx="170" cy="122" fill="#ffffff" r="4" stroke="#22c55e" stroke-width="2"></circle><circle cx="116" cy="135" fill="#ffffff" r="5" stroke="#00d2ff" stroke-width="2"></circle><circle cx="72" cy="188" fill="#00d2ff" r="6" stroke="#ffffff" stroke-width="2"></circle><circle cx="162" cy="188" fill="#00d2ff" r="6" stroke="#ffffff" stroke-width="2"></circle><circle cx="78" cy="245" fill="#ffffff" r="4.5" stroke="#22c55e" stroke-width="2"></circle><circle cx="156" cy="245" fill="#ffffff" r="4.5" stroke="#22c55e" stroke-width="2"></circle></svg></div><div class="mt-3 space-y-1"><h2 class="text-base font-semibold text-white tracking-wide">Khu vực nhận diện chuyển động AI</h2><p class="text-xs text-[#86868b] max-w-xs">Hệ thống đang đối chiếu 17 điểm khớp xương với tiêu chuẩn squat thi đấu.</p></div></div><div class="relative z-20 flex items-end justify-between w-full"><div class="backdrop-blur-md bg-black/50 border border-white/10 px-4 py-2 rounded-2xl flex items-center gap-2 shadow-lg" data-purpose="rep-counter"><span class="text-xs text-white/60 font-medium">Số lần đúng:</span><span id="workout-reps" class="text-xl font-bold text-[#00d2ff] font-mono drop-shadow-[0_0_10px_rgba(0,210,255,0.4)]">0</span></div><div class="backdrop-blur-md bg-black/60 px-5 py-3 rounded-2xl border border-white/15 shadow-2xl text-right" data-purpose="workout-timer"><span class="text-xs text-[#86868b] font-medium block">Thời gian: <span class="font-mono font-bold text-white text-base tracking-tight">00:00</span></span></div></div></div>
<!-- Camera Control Bar / Settings Shortcut -->
<div class="flex items-center justify-between px-4 py-3 rounded-2xl bg-[#141416] border border-white/10 text-xs text-[#86868b]">
<div class="flex items-center gap-3">
<span class="inline-flex items-center gap-1.5 text-slate-300 font-medium">
<svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
<path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round" stroke-linejoin="round"></path>
</svg>
              Góc máy: Rõ toàn thân
            </span>
<span class="hidden sm:inline text-white/20">|</span>
<span class="hidden sm:inline">Khoảng cách khuyến nghị: 2.0m - 2.5m</span>
</div>

</div>
</section>
<!-- END: LeftColumn_CameraHUD -->
<!-- BEGIN: RightColumn_GuideAndControls -->
<!-- Exercise Guide & AI Feedback Center -->
<aside class="lg:col-span-4 bg-[#1c1c1e] p-6 sm:p-7 rounded-3xl border border-white/10 shadow-2xl flex flex-col space-y-6" data-purpose="exercise-guide-panel"><div class="border-b border-white/10 pb-5"><div class="flex items-center justify-between mb-2"><span class="text-xs font-bold uppercase tracking-wider text-[#00d2ff] bg-[#00d2ff]/10 px-2.5 py-1 rounded-md border border-[#00d2ff]/20">Bài tập hiện tại</span><span class="text-xs text-[#86868b] font-medium">Hiệp 2 / 4</span></div><h1 id="exercise-title" class="text-2xl font-extrabold text-white tracking-tight">SQUAT</h1><p id="exercise-muscles" class="text-xs text-[#86868b] mt-1 font-medium">Nhóm cơ: Đùi trước, cơ mông &amp; cơ lõi</p></div><div class="rounded-2xl p-4 bg-gradient-to-r from-emerald-950/40 to-[#141416] border border-emerald-500/30 relative overflow-hidden" data-purpose="ai-live-verdict"><div class="flex items-start gap-3"><div class="h-8 w-8 rounded-full bg-emerald-500/20 flex items-center justify-center shrink-0 border border-emerald-500/40 text-emerald-400"><svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M5 13l4 4L19 7" stroke-linecap="round" stroke-linejoin="round"></path></svg></div><div><div class="flex items-center gap-2"><h3 id="exercise-feedback-title" class="text-sm font-bold text-emerald-400">Phản hồi: Bắt đầu khi bạn sẵn sàng</h3></div><p id="exercise-feedback" class="text-xs text-slate-300 mt-1 leading-relaxed">Đặt toàn bộ cơ thể trong khung hình để bắt đầu.</p></div></div></div><div class="w-full rounded-2xl bg-[#141416] border border-white/10 p-4 relative overflow-hidden flex flex-col justify-between" data-purpose="motion-demonstration"><div class="flex items-center justify-between mb-2"><span id="motion-title" class="text-xs font-semibold text-white flex items-center gap-1.5"><svg class="w-4 h-4 text-[#00d2ff]" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" stroke-linecap="round" stroke-linejoin="round"></path><path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round" stroke-linejoin="round"></path></svg>Mô phỏng động tác chuẩn&nbsp;</span></div><div class="h-80 md:h-96 rounded-2xl bg-white border border-white/10 relative flex items-center justify-center overflow-hidden"><img id="exercise-demo-gif" src="/static/Squats.gif" alt="Minh họa động tác Squat" class="h-full w-full object-contain"><span id="motion-tip" class="sr-only">Góc hạ hông lý tưởng: 90° - 100°</span><span id="motion-subtip" class="sr-only">Trọng tâm dồn đều vào gót chân</span></div></div><div class="rounded-2xl bg-black/60 border border-white/10 px-4 py-3 flex items-center justify-between shadow-inner"><span class="text-xs text-slate-300 font-medium flex items-center gap-2">🔥 Calo tiêu thụ ước tính:</span><span class="text-xs font-bold text-[#00d2ff] font-mono drop-shadow-[0_0_10px_rgba(0,210,255,0.4)]">~45 kcal</span></div><div class="pt-2 flex items-center gap-3" data-purpose="action-buttons"><button id="start-workout-button" aria-label="Bắt đầu buổi tập" class="flex-1 bg-[#00d2ff] hover:bg-cyan-300 active:scale-95 text-black font-bold rounded-full py-3.5 px-4 flex items-center justify-center gap-2 transition-all text-sm" type="button"><svg class="w-4 h-4 fill-current" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"></path></svg><span>Bắt đầu</span></button><button aria-label="Tạm dừng buổi tập" style="display:none" class="flex-1 bg-white/10 hover:bg-white/20 active:scale-95 text-white font-semibold rounded-full py-3.5 px-4 flex items-center justify-center gap-2 border border-white/10 transition-all text-sm shadow-md" type="button"><svg class="w-4 h-4 fill-current" viewBox="0 0 24 24"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"></path></svg><span class="">Tạm dừng</span></button><a href="/summary" aria-label="Kết thúc buổi tập" style="display:none" class="flex-1 bg-red-600 hover:bg-red-500 active:scale-95 text-white font-semibold rounded-full py-3.5 px-4 flex items-center justify-center gap-2 shadow-[0_0_25px_rgba(239,68,68,0.45)] transition-all text-sm" role="button"><svg class="w-4 h-4 fill-current" viewBox="0 0 24 24"><path d="M6 6h12v12H6z"></path></svg><span class="">Kết thúc</span></a></div></aside>
<!-- END: RightColumn_GuideAndControls -->
</div>
</main><div class="fixed bottom-5 inset-x-0 z-30 flex justify-center px-4 pointer-events-none"></div>
<!-- END: MainContent -->
<!-- BEGIN: FloatingBottomNavigationDock -->
<!-- Apple style floating navigation dock -->

<!-- END: FloatingBottomNavigationDock -->
<!-- BEGIN: InteractiveScripts -->
<script data-purpose="workout-timer-simulation">
(() => {
  let elapsed=0, startedAt=0, running=false, paused=false, timerId=null;
  const display=document.querySelector('[data-purpose="workout-timer"] .font-mono');
  const startButton=document.getElementById('start-workout-button');
  const pauseButton=document.querySelector('[aria-label="Tạm dừng buổi tập"]');
  const finishLink=document.querySelector('[aria-label="Kết thúc buổi tập"]');
  const format=(seconds)=>String(Math.floor(seconds/60)).padStart(2,'0')+':'+String(seconds%60).padStart(2,'0');
  const shownSeconds=()=>{const parts=(display?.textContent||'00:00').trim().split(':').map(Number);return (parts[0]||0)*60+(parts[1]||0);};
  const render=()=>{if(display&&running)display.textContent=format(elapsed+Math.floor((Date.now()-startedAt)/1000));};
  const startClock=()=>{running=true;paused=false;startedAt=Date.now();timerId=window.setInterval(render,100);render();};
  const freezeClock=()=>{if(running){elapsed=shownSeconds();running=false;window.clearInterval(timerId);timerId=null;}paused=true;};
  if(!display||!startButton||!pauseButton||!finishLink)return;
  display.textContent='00:00';
  startButton.addEventListener('click',()=>{if(running)return;startButton.style.display='none';pauseButton.style.display='flex';finishLink.style.display='flex';startClock();});
  pauseButton.addEventListener('click',()=>{
    if(running){freezeClock();pauseButton.setAttribute('aria-label','Tiếp tục buổi tập');pauseButton.querySelector('span').textContent='Tiếp tục';pauseButton.querySelector('svg').innerHTML='<path d="M8 5v14l11-7z"></path>';}
    else if(paused){pauseButton.setAttribute('aria-label','Tạm dừng buổi tập');pauseButton.querySelector('span').textContent='Tạm dừng';pauseButton.querySelector('svg').innerHTML='<path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"></path>';startClock();}
  });
  finishLink.addEventListener('click',(event)=>{
    event.preventDefault();if(running)freezeClock();
    const duration=paused?elapsed:shownSeconds();
    const reps=Number(document.getElementById('workout-reps')?.textContent||0);
    const result={exercise:sessionStorage.getItem('smurfExercise')||'squat',durationSeconds:duration,duration:format(duration),reps};
    sessionStorage.setItem('smurfLastWorkout',JSON.stringify(result));window.location.assign(finishLink.href);
  });
})();
</script>
<!-- END: InteractiveScripts -->








<style data-purpose="workout-fit-screen">
@media (min-width: 1024px) and (min-height: 680px) {
  body { height:100vh; min-height:0 !important; overflow:hidden; padding-bottom:0 !important; }
  #workout-main { height:calc(100vh - 76px); padding-top:.65rem !important; padding-bottom:.5rem !important; overflow:hidden; }
  #workout-main > .grid { height:100%; min-height:0; align-items:stretch !important; gap:.8rem !important; }
  #workout-main section[aria-label="Khu vực theo dõi camera AI"] { min-height:0; gap:.55rem !important; }
  #workout-main section[aria-label="Khu vực theo dõi camera AI"] > div:first-child { height:calc(100vh - 150px) !important; min-height:0 !important; padding:1rem !important; }
  #workout-main section[aria-label="Khu vực theo dõi camera AI"] > div:nth-child(2) { padding:.55rem .8rem !important; }
  #workout-main aside[data-purpose="exercise-guide-panel"] { min-height:0; overflow:hidden; padding:1rem !important; gap:.65rem !important; }
  #workout-main aside [data-purpose="motion-demonstration"] { padding:.65rem !important; }
  #workout-main aside [data-purpose="motion-demonstration"] .h-80 { height:10rem !important; }
  #workout-main aside [data-purpose="motion-demonstration"] .md\:h-96 { height:10rem !important; }
  #workout-main aside .pb-5 { padding-bottom:.6rem !important; }
}
@media (min-width: 1024px) and (max-height:679px) { #workout-main { padding-top:.5rem !important; } }
</style>
<script data-purpose="selected-exercise">
(() => {
 const exercise=sessionStorage.getItem('smurfExercise')||'squat';
 const jumping=exercise==='jumping_jack';
 document.body.dataset.exercise=exercise;
 const set=(id,text)=>{const el=document.getElementById(id);if(el)el.textContent=text;};
 set('exercise-title',jumping?'JUMPING JACK':'SQUAT');
 set('exercise-muscles',jumping?'Nhóm cơ: Toàn thân, vai, chân và hệ tim mạch':'Nhóm cơ: Đùi trước, cơ mông & cơ lõi');
 set('exercise-feedback-title',jumping?'Phản hồi: Giữ nhịp ổn định':'Phản hồi: Bắt đầu khi bạn sẵn sàng');
 set('exercise-feedback',jumping?'Bật nhẹ, tiếp đất êm và đưa hai tay qua đầu theo nhịp.':'Đặt toàn bộ cơ thể trong khung hình. Hạ hông có kiểm soát và giữ lưng thẳng.');
 set('motion-tip',jumping?'Jumping Jack: dang chân và đưa tay qua đầu':'Góc hạ hông lý tưởng: 90° - 100°');
 set('motion-subtip',jumping?'Tiếp đất nhẹ bằng mũi bàn chân, giữ nhịp thở đều.':'Trọng tâm dồn đều vào gót chân');
 set('workout-reps','0');
 const demo=document.getElementById('exercise-demo-gif');if(demo){demo.src=jumping?'/static/Jumpingjacks.gif':'/static/Squats.gif';demo.alt=jumping?'Minh họa động tác Jumping Jack':'Minh họa động tác Squat';}
 const pose=document.querySelector('[data-purpose="pose-skeleton-visualization"] svg');
 if(jumping&&pose){pose.innerHTML='<circle cx="120" cy="40" r="14" fill="#22c55e" fill-opacity=".25" stroke="#22c55e" stroke-width="3"/><g stroke="#00d2ff" stroke-width="5" stroke-linecap="round" fill="none"><path d="M120 54v55m0-38L75 35 45 10m75 61 45-36 30-25M120 109l-43 43-25 75m68-118 43 43 25 75"/></g><g fill="#fff" stroke="#22c55e" stroke-width="2"><circle cx="120" cy="71" r="5"/><circle cx="75" cy="35" r="5"/><circle cx="165" cy="35" r="5"/><circle cx="77" cy="152" r="5"/><circle cx="163" cy="152" r="5"/><circle cx="52" cy="227" r="5"/><circle cx="188" cy="227" r="5"/></g>';}
})();
</script>
</body></html>"""
