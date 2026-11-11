from __future__ import annotations


def get_home_html() -> str:
    """Return the home screen exported from Stitch."""
    return r"""<!DOCTYPE html><html class="dark" lang="vi"><head>
<meta charset="utf-8">
<meta content="width=device-width, initial-scale=1.0" name="viewport">
<title>Smurf Fitness - Trợ Lý Tập Luyện AI</title>
<!-- Tailwind CSS CDN v3 -->
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            appleBg: '#050507',
            appleCard: '#121216',
            appleCardHover: '#18181f',
            appleBorder: 'rgba(255, 255, 255, 0.08)',
            appleBlue: '#0071e3',
            appleNeon: '#a3e635',
            applePurple: '#af52de',
          },
          fontFamily: {
            sans: ['-apple-system', 'BlinkMacSystemFont', '"SF Pro Display"', '"SF Pro Text"', 'Inter', 'Segoe UI', 'Roboto', 'sans-serif'],
          },
          boxShadow: {
            'glow-blue': '0 0 35px -5px rgba(0, 113, 227, 0.35)',
            'glow-neon': '0 0 30px -5px rgba(163, 230, 53, 0.3)',
            'glow-purple': '0 0 35px -5px rgba(175, 82, 222, 0.35)',
            'apple-card': '0 10px 30px -10px rgba(0, 0, 0, 0.7)',
          }
        }
      }
    }
  </script>
<!-- BEGIN: Custom Styles -->
<style data-purpose="apple-glass-styling">
    /* Hiệu ứng kính mờ chuẩn Apple macOS/iOS */
    .glass-nav {
      background: rgba(10, 10, 12, 0.75);
      backdrop-filter: blur(24px);
      -webkit-backdrop-filter: blur(24px);
    }
    .glass-card {
      background: rgba(18, 18, 22, 0.7);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .glass-dock {
      background: rgba(22, 22, 28, 0.75);
      backdrop-filter: blur(30px);
      -webkit-backdrop-filter: blur(30px);
      border: 1px solid rgba(255, 255, 255, 0.14);
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
    }
  </style>
<style data-purpose="ambient-gradients">
    /* Gradient nền ambient huyền ảo */
    .ambient-glow-top {
      position: absolute;
      top: -150px;
      left: 20%;
      width: 600px;
      height: 450px;
      background: radial-gradient(circle, rgba(0, 113, 227, 0.12) 0%, rgba(175, 82, 222, 0.08) 50%, rgba(0, 0, 0, 0) 70%);
      pointer-events: none;
      z-index: 0;
    }
    .ambient-glow-right {
      position: absolute;
      top: 15%;
      right: -100px;
      width: 500px;
      height: 500px;
      background: radial-gradient(circle, rgba(163, 230, 53, 0.08) 0%, rgba(0, 113, 227, 0.05) 50%, rgba(0, 0, 0, 0) 70%);
      pointer-events: none;
      z-index: 0;
    }
  </style>
<!-- END: Custom Styles -->
</head>
<body class="bg-black text-zinc-100 font-sans antialiased min-h-screen relative selection:bg-appleBlue selection:text-white pb-32 overflow-x-hidden">
<!-- Ánh sáng nền Ambient Apple -->
<div class="ambient-glow-top"></div>
<div class="ambient-glow-right"></div>
<!-- BEGIN: TopNavigation -->
<header class="sticky top-0 z-50 glass-nav border-b border-white/10 transition-all duration-300">
<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-18 flex items-center justify-between">
<!-- Nhận diện thương hiệu & Trợ lý -->
<div class="flex items-center gap-2 py-2">
  <a class="flex items-center gap-3 group" href="#">
    <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuAMq7rJI3aRSSeattprqkNFKoDR5fbMSrl5d_n7u7iO3KP7XfiSBlv7Ouffi9YAhKZDke4jvfPaaMd3NSPMszqK9BsqTe4JqWkn_79pNtLOEXzbaIDieE5SCDkZ5NbKk7QXe-hlswVd3B9aJ6cgUUwt_ugmiMSUhkxkAgNOvsFLDSU_8cnSXgJWCPZewsbr8zCCa1bzfWumSwF8t0bqWwF9i5xM7I7klLzwVE8TiRubMAPIy2zKldtGHQ" alt="SMURF FITNESS Logo" class="h-14 w-14 object-cover rounded-2xl shadow-[0_0_20px_rgba(0,210,255,0.3)] border border-white/20 transition-transform duration-300 group-hover:scale-105">
    <span class="text-xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">SMURF FITNESS</span>
  </a>
  <div class="h-12 w-px bg-white/15 mx-4"></div>
  <div class="flex flex-col justify-center">
    <div class="flex items-center gap-2">
      <span id="home-greeting" class="text-lg font-bold text-white tracking-tight">Xin chào</span>
      <span class="w-2 h-2 rounded-full bg-appleNeon animate-pulse shadow-glow-neon"></span>
    </div>
    <span class="text-xs text-zinc-400 font-medium">Sẵn sàng tập luyện hôm nay</span>
  </div>
</div>
<!-- Điều hướng trung tâm -->
<nav class="hidden md:flex items-center gap-1 bg-white/5 p-1 rounded-full border border-white/10">



</nav>
<!-- Chỉ số cá nhân & Hồ sơ người dùng -->
<div class="flex items-center gap-3">
<!-- Ngày tháng hiện tại -->
<div class="flex items-center gap-2 bg-white/5 border border-white/10 px-3 py-2 rounded-full">
<svg class="h-4 w-4 text-appleNeon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path d="M8 2v4m8-4v4M3 10h18M5 4h14a2 2 0 012 2v14H3V6a2 2 0 012-2z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg>
<span id="real-date" class="text-xs font-semibold text-zinc-200 whitespace-nowrap" aria-live="polite"></span>
</div>
<!-- Chuông thông báo kính mờ -->
<button class="relative w-12 h-12 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 flex items-center justify-center text-zinc-300 hover:text-white transition-all">
<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
<path d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
</svg>
<span class="absolute top-2 right-2 w-1.5 h-1.5 bg-appleNeon rounded-full"></span>
</button>
<!-- Mở hồ sơ và ảnh đại diện -->
<button id="profile-avatar-button" type="button" aria-label="Mở thông tin cá nhân" class="w-14 h-14 rounded-full p-[2px] bg-gradient-to-tr from-appleBlue via-applePurple to-appleNeon shadow-md overflow-hidden">
  <span class="w-full h-full rounded-full bg-zinc-900 flex items-center justify-center overflow-hidden">
    <img id="profile-avatar" class="hidden w-full h-full object-cover" alt="Ảnh đại diện">
    <span id="profile-initials" class="text-xs font-bold text-white">?</span>
  </span>
</button>
</div>
</div>
</header>
<!-- END: TopNavigation -->
<!-- BEGIN: MainContent -->
<main id="home-main" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 space-y-12 relative z-10">
<!-- BEGIN: HeroSection -->
<section id="home-layout" class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
<div class="lg:col-span-5 space-y-6 pt-4">
<div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-appleNeon/10 border border-appleNeon/30"><span class="w-2 h-2 rounded-full bg-appleNeon animate-pulse"></span><span class="text-xs font-semibold text-appleNeon">SẴN SÀNG TẬP LUYỆN</span></div>
<h1 class="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white tracking-tight leading-tight">Tập khỏe hơn,<br><span class="bg-clip-text text-transparent bg-gradient-to-r from-white via-zinc-200 to-zinc-400">mỗi ngày một chút.</span></h1>
<p class="mt-3 text-base text-zinc-400 max-w-xl font-normal leading-relaxed">Chọn bài tập phù hợp, định hình chuẩn form qua camera trí tuệ nhân tạo và chinh phục thể lực cùng Smurf Fitness.</p>

<div id="muscle-preview" class="hidden rounded-2xl border border-white/10 bg-white/[0.04] p-4 shadow-xl" aria-live="polite"><h2 id="muscle-preview-title" class="text-sm font-bold tracking-wide text-[#00d2ff]">VÙNG TẬP TRUNG</h2><div class="mt-3 grid grid-cols-[minmax(0,1fr)_minmax(120px,42%)] items-center gap-3"><div id="muscle-preview-tags" class="flex flex-col items-start gap-2"></div><img id="muscle-preview-image" class="h-48 w-full rounded-xl bg-white object-contain" alt="Sơ đồ vùng cơ tập trung"></div></div>
</div>
<div class="lg:col-span-7 space-y-4">
<div class="flex items-center justify-between"><h2 class="text-xs font-semibold uppercase tracking-wider text-zinc-400">Chọn bài tập</h2><span class="text-xs text-zinc-500">4 bài tập</span></div>
<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
<div class="glass-card rounded-2xl p-5 border border-white/10 hover:border-appleNeon/50 transition-all"><div class="text-2xl mb-3">🏋️</div><h3 data-exercise-heading="squat" class="text-lg font-bold text-white">Squat</h3><p class="text-xs text-zinc-400 mt-1 min-h-8">Tăng cường cơ đùi và cơ mông.</p><a href="/workout" onclick="sessionStorage.setItem('smurfExercise','squat')" class="mt-4 w-full px-4 py-2.5 rounded-full bg-appleNeon text-black font-bold text-sm flex justify-center">Bắt đầu ngay</a></div>
<div class="glass-card rounded-2xl p-5 border border-white/10 hover:border-appleBlue/50 transition-all"><div class="text-2xl mb-3">🤸</div><h3 data-exercise-heading="jumping_jack" class="text-lg font-bold text-white">Jumping Jack</h3><p class="text-xs text-zinc-400 mt-1 min-h-8">Vận động toàn thân, cải thiện sức bền.</p><a href="/workout" onclick="sessionStorage.setItem('smurfExercise','jumping_jack')" class="mt-4 w-full px-4 py-2.5 rounded-full bg-appleBlue text-white font-bold text-sm flex justify-center">Bắt đầu ngay</a></div>
<div class="glass-card rounded-2xl p-5 border border-white/10 hover:border-purple-400/50 transition-all"><div class="text-2xl mb-3">🧘</div><h3 data-exercise-heading="plank" class="text-lg font-bold text-white">Plank</h3><p class="text-xs text-zinc-400 mt-1 min-h-8">Rèn luyện cơ lõi và sức bền.</p><a href="/workout" onclick="sessionStorage.setItem('smurfExercise','plank')" class="mt-4 w-full px-4 py-2.5 rounded-full bg-purple-500 text-white font-bold text-sm flex justify-center">Bắt đầu ngay</a></div>
<div class="glass-card rounded-2xl p-5 border border-white/10 hover:border-orange-400/50 transition-all"><div class="text-2xl mb-3">🏃</div><h3 data-exercise-heading="high_knees" class="text-lg font-bold text-white">High Knees</h3><p class="text-xs text-zinc-400 mt-1 min-h-8">Chạy tại chỗ, nâng cao gối theo nhịp.</p><a href="/workout" onclick="sessionStorage.setItem('smurfExercise','high_knees')" class="mt-4 w-full px-4 py-2.5 rounded-full bg-orange-500 text-white font-bold text-sm flex justify-center">Bắt đầu ngay</a></div>
</div></div></section>
<!-- END: HeroSection -->
<!-- BEGIN: DailyQuestsSection -->
<section class="pt-4 space-y-6" id="nhiem-vu">
<div class="flex flex-col sm:flex-row sm:items-end justify-between gap-4">

<!-- Bộ chuyển đổi cấp độ nhiệm vụ -->

</div>
<!-- Thẻ danh sách 2 nhiệm vụ tương ứng -->
<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
<!-- Thẻ Nhiệm vụ 1: Bình Thường -->

<!-- Thẻ Nhiệm vụ 2: Thử Thách Khó -->

</div>
</section>
<!-- END: DailyQuestsSection -->
</main>
<!-- END: MainContent -->
<!-- BEGIN: BottomFloatingDock -->
<!-- macOS/iOS Floating Dock thanh thoát cố định góc đáy màn hình -->
<aside aria-label="Thanh điều hướng nổi" class="fixed bottom-6 inset-x-0 z-50 flex justify-center px-4 pointer-events-none">

</aside>
<!-- END: BottomFloatingDock -->
<!-- BEGIN: InteractiveScripts -->
<script data-purpose="simple-interactions">
    // Khởi tạo các thao tác tương tác tối thiểu không phụ thuộc thư viện ngoài
    document.addEventListener('DOMContentLoaded', () => {
      // Phản hồi khi nhấn các nút CTA
      const actionButtons = document.querySelectorAll('button');
      actionButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
          // Hiệu ứng phản hồi nhẹ
          btn.classList.add('opacity-90');
          setTimeout(() => btn.classList.remove('opacity-90'), 150);
        });
      });
    });
  </script>
<!-- END: InteractiveScripts -->






<div id="snapdom-sandbox" data-snapdom-sandbox="true" aria-hidden="true" style="position: absolute; left: -9999px; top: -9999px; width: 0px; height: 0px; overflow: hidden;"></div>
<style data-purpose="profile-onboarding-styles">
  body.profile-locked { overflow: hidden; }
  #profile-onboarding[hidden], #bmi-modal[hidden] { display: none !important; }
</style>
<div id="profile-onboarding" hidden class="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-md p-4" role="dialog" aria-modal="true" aria-labelledby="profile-title">
  <form id="profile-form" class="w-full max-w-md rounded-3xl border border-white/10 bg-[#111216] p-6 sm:p-8 shadow-2xl text-white">
    <div class="text-center mb-6">
      <div class="mx-auto mb-3 h-12 w-12 rounded-2xl bg-appleNeon/15 text-appleNeon flex items-center justify-center text-2xl">●</div>
      <h2 id="profile-title" class="text-2xl font-bold">Thông tin của bạn</h2>
      <p class="mt-2 text-sm text-zinc-400">Điền thông tin để bắt đầu sử dụng Smurf Fitness.</p>
    </div>
    <div class="flex flex-col items-center mb-6">
      <label for="profile-photo-input" class="group cursor-pointer">
        <span class="flex h-24 w-24 items-center justify-center overflow-hidden rounded-full border-2 border-dashed border-white/25 bg-white/5 text-zinc-300 group-hover:border-sky-400">
          <img id="profile-photo-preview" class="hidden h-full w-full object-cover" alt="Xem trước ảnh đại diện">
          <span id="profile-photo-placeholder" class="text-3xl">📷</span>
        </span>
        <span class="mt-2 block text-center text-sm font-semibold text-sky-400">Chọn ảnh đại diện</span>
      </label>
      <input id="profile-photo-input" class="sr-only" type="file" accept="image/png,image/jpeg,image/webp" required>
    </div>
    <label class="mb-2 block text-sm font-semibold text-zinc-300" for="profile-name">Tên hiển thị</label>
    <input id="profile-name" class="mb-4 w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-white placeholder:text-zinc-500 focus:border-sky-400 focus:outline-none" type="text" minlength="2" maxlength="40" autocomplete="name" placeholder="Tên của bạn" required>
    <label class="mb-2 block text-sm font-semibold text-zinc-300" for="profile-birthday">Ngày tháng năm sinh</label>
    <input id="profile-birthday" class="mb-4 w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-white focus:border-sky-400 focus:outline-none" type="date" required>
    <label class="mb-2 block text-sm font-semibold text-zinc-300" for="profile-gender">Giới tính</label>
    <select id="profile-gender" class="w-full rounded-xl border border-white/10 bg-[#1c1c1e] px-4 py-3 text-white focus:border-sky-400 focus:outline-none" required>
      <option value="">Chọn giới tính</option><option value="female">Nữ</option><option value="male">Nam</option><option value="other">Khác</option><option value="prefer-not-to-say">Không muốn chia sẻ</option>
    </select>
    <p id="profile-error" class="mt-3 min-h-5 text-sm text-red-400" role="alert"></p>
    <button id="profile-save" class="mt-2 w-full rounded-xl bg-appleNeon px-4 py-3 font-bold text-black hover:bg-[#bbf048]" type="submit">Lưu thông tin và tiếp tục</button>
    <button id="profile-cancel" class="mt-3 hidden w-full rounded-xl border border-white/10 px-4 py-3 text-sm text-zinc-300 hover:bg-white/5" type="button">Đóng</button>
  </form>
</div>
<script data-purpose="profile-onboarding">
(() => {
  const KEY = 'smurfProfileV1';
  const modal = document.getElementById('profile-onboarding');
  const form = document.getElementById('profile-form');
  const nameInput = document.getElementById('profile-name');
  const birthdayInput = document.getElementById('profile-birthday');
  const genderInput = document.getElementById('profile-gender');
  const photoInput = document.getElementById('profile-photo-input');
  const preview = document.getElementById('profile-photo-preview');
  const error = document.getElementById('profile-error');
  const cancel = document.getElementById('profile-cancel');
  let photoData = '';
  const today = new Date();
  const todayIso = new Date(today.getTime() - today.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
  birthdayInput.max = todayIso;
  const open = (required = false) => {
    cancel.classList.toggle('hidden', required);
    modal.hidden = false;
    document.body.classList.add('profile-locked');
    try {
      const saved = JSON.parse(localStorage.getItem(KEY) || 'null');
      if (saved) {
        nameInput.value = saved.name || '';
        birthdayInput.value = saved.birthday || '';
        genderInput.value = saved.gender || '';
        photoData = saved.photo || '';
        if (photoData) { preview.src = photoData; preview.classList.remove('hidden'); document.getElementById('profile-photo-placeholder').classList.add('hidden'); }
      }
    } catch (_) {}
    nameInput.focus();
  };
  const close = () => { modal.hidden = true; document.body.classList.remove('profile-locked'); };
  const updateHeader = (profile) => {
    document.getElementById('home-greeting').textContent = 'Xin chào, ' + profile.name;
    const avatar = document.getElementById('profile-avatar');
    const initials = document.getElementById('profile-initials');
    if (profile.photo) { avatar.src = profile.photo; avatar.classList.remove('hidden'); initials.classList.add('hidden'); }
    else { initials.textContent = profile.name.trim().split(/\s+/).map(x => x[0]).join('').slice(0, 2).toUpperCase(); }
  };
  document.getElementById('profile-avatar-button').addEventListener('click', () => open(false));
  cancel.addEventListener('click', close);
  photoInput.addEventListener('change', () => {
    const file = photoInput.files && photoInput.files[0];
    if (!file) return;
    if (!/^image\/(png|jpeg|webp)$/.test(file.type) || file.size > 5 * 1024 * 1024) {
      error.textContent = 'Chọn ảnh PNG, JPG hoặc WebP nhỏ hơn 5 MB.'; photoInput.value = ''; return;
    }
    const reader = new FileReader();
    reader.onload = () => { photoData = String(reader.result || ''); preview.src = photoData; preview.classList.remove('hidden'); document.getElementById('profile-photo-placeholder').classList.add('hidden'); error.textContent = ''; };
    reader.readAsDataURL(file);
  });
  const validBirthday = (value) => {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
    const [y, m, d] = value.split('-').map(Number);
    const date = new Date(Date.UTC(y, m - 1, d));
    if (date.getUTCFullYear() !== y || date.getUTCMonth() !== m - 1 || date.getUTCDate() !== d) return false;
    const selected = new Date(y, m - 1, d); const now = new Date(); now.setHours(0,0,0,0);
    if (selected > now) return false;
    const earliest = new Date(); earliest.setFullYear(earliest.getFullYear() - 120); earliest.setHours(0,0,0,0);
    return selected >= earliest;
  };
  form.addEventListener('submit', (event) => {
    event.preventDefault(); error.textContent = '';
    const name = nameInput.value.trim().replace(/\s+/g, ' ');
    if (name.length < 2) { error.textContent = 'Tên hiển thị cần có ít nhất 2 ký tự.'; return; }
    if (!validBirthday(birthdayInput.value)) { error.textContent = 'Ngày sinh không hợp lệ. Hãy kiểm tra ngày, tháng, năm và chọn ngày không ở tương lai.'; return; }
    if (!genderInput.value) { error.textContent = 'Vui lòng chọn giới tính.'; return; }
    if (!photoData) { error.textContent = 'Vui lòng chọn ảnh đại diện trước khi tiếp tục.'; return; }
    const profile = {name, birthday:birthdayInput.value, gender:genderInput.value, photo:photoData};
    try { localStorage.setItem(KEY, JSON.stringify(profile)); }
    catch (_) { error.textContent = 'Không lưu được ảnh. Hãy chọn ảnh có dung lượng nhỏ hơn.'; return; }
    updateHeader(profile); close();
  });
  try {
    const profile = JSON.parse(localStorage.getItem(KEY) || 'null');
    if (!profile || !profile.name || !profile.birthday || !profile.gender || !profile.photo) open(true);
    else updateHeader(profile);
  } catch (_) { open(true); }
})();
</script>

<div id="bmi-modal" hidden class="fixed inset-0 z-[110] flex items-center justify-center bg-black/80 backdrop-blur-md p-4" role="dialog" aria-modal="true" aria-labelledby="bmi-title"><form id="bmi-form" class="w-full max-w-md rounded-3xl border border-white/10 bg-[#111216] p-6 text-white shadow-2xl"><h2 id="bmi-title" class="text-2xl font-bold">Cập nhật chỉ số BMI</h2><p class="mt-2 text-sm text-zinc-400">Nhập số đo của bạn. BMI = cân nặng (kg) / chiều cao² (m). <a class="text-sky-400 underline" href="https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight" target="_blank" rel="noopener">Nguồn WHO</a>.</p><label class="mt-5 block text-sm text-zinc-300" for="bmi-height">Chiều cao (cm)</label><input id="bmi-height" type="number" min="80" max="250" step="0.1" required class="mt-2 w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-white"><label class="mt-4 block text-sm text-zinc-300" for="bmi-weight">Cân nặng (kg)</label><input id="bmi-weight" type="number" min="20" max="350" step="0.1" required class="mt-2 w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-white"><p id="bmi-error" class="mt-3 min-h-5 text-sm text-red-400" role="alert"></p><div class="mt-4 flex gap-3"><button id="bmi-cancel" type="button" class="flex-1 rounded-xl border border-white/10 px-4 py-3 text-zinc-300">Đóng</button><button type="submit" class="flex-1 rounded-xl bg-appleNeon px-4 py-3 font-bold text-black">Tính BMI</button></div><p class="mt-4 text-xs text-zinc-500">Phân loại theo ngưỡng BMI người trưởng thành của WHO; BMI không thay thế tư vấn y tế.</p></form></div>
<style data-purpose="home-compact-layout">
@media (min-width: 1024px) and (min-height: 680px) {
  body { height: 100vh; min-height: 0 !important; overflow: hidden; padding-bottom: 0 !important; }
  #home-main { height: calc(100vh - 86px); padding-top: .65rem !important; padding-bottom: .5rem !important; display: flex; flex-direction: column; gap: .25rem; overflow: hidden; }
  #home-layout { flex: 1; min-height: 0; gap: .8rem !important; align-items: stretch !important; }
  #home-layout > div { min-height: 0; }
  #home-layout .glass-card { padding: .85rem !important; }
  #home-layout .space-y-4 > :not([hidden]) ~ :not([hidden]) { margin-top: .55rem !important; }
  #home-layout .mt-5 { margin-top: .7rem !important; }
  #home-layout .mt-6 { margin-top: .8rem !important; }
  #home-layout .p-6 { padding: .9rem !important; }
  #nhiem-vu, #home-main > aside { display: none !important; }
}
@media (min-width: 1024px) and (max-height: 679px) { #nhiem-vu { display:none !important; } #home-main { padding-top:.75rem !important; } }
</style>
<script data-purpose="actual-date">
(() => { const el=document.getElementById('real-date'); if(!el)return; const render=()=>{el.textContent=new Intl.DateTimeFormat('vi-VN',{weekday:'long',day:'numeric',month:'long',year:'numeric'}).format(new Date());};render();setInterval(render,60000); })();
</script>

<script data-purpose="exercise-muscle-preview">
(() => {
 const data={plank:{title:'Plank',tags:['Bụng','Vai','Cơ mông'],image:'/static/muscle-plank.png'},jumping_jack:{title:'Jumping Jack',tags:['Vai','Cơ đùi trước','Cơ đùi trong','Ngực','Cơ mông','Cơ bắp chân'],image:'/static/muscle-jumping-jack.png'},squat:{title:'Squat',tags:['Cơ mông','Cơ đùi trước','Cơ đùi sau','Cơ bắp chân'],image:'/static/muscle-squat.png'},high_knees:{title:'High Knees',tags:['Cơ mông','Cơ đùi trước','Cơ đùi sau','Cơ bắp chân','Lưng','Ngực','Vai'],image:'/static/muscle-high-knees.png'}};
 const panel=document.getElementById('muscle-preview'),title=document.getElementById('muscle-preview-title'),tags=document.getElementById('muscle-preview-tags'),image=document.getElementById('muscle-preview-image'); if(!panel)return;
 const show=(key)=>{const item=data[key];if(!item)return;title.textContent='VÙNG TẬP TRUNG · '+item.title;tags.innerHTML=item.tags.map(tag=>`<span class="rounded-full bg-white/10 px-3 py-1.5 text-xs text-slate-200"><span class="mr-1.5 text-blue-400">●</span>${tag}</span>`).join('');image.src=item.image;image.alt='Các vùng cơ tập trung khi tập '+item.title;panel.classList.remove('hidden');};
 const hide=()=>panel.classList.add('hidden'); document.querySelectorAll('[data-exercise-heading]').forEach(heading=>{const card=heading.closest('.glass-card');if(!card)return;const key=heading.dataset.exerciseHeading;card.addEventListener('mouseenter',()=>show(key));card.addEventListener('mouseleave',hide);card.addEventListener('focusin',()=>show(key));card.addEventListener('focusout',e=>{if(!card.contains(e.relatedTarget))hide();});});
})();
</script>
<script data-purpose="bmi-and-attendance">
(() => {
 const bmiKey='smurfBmiV1', attendanceKey='smurfAttendanceDatesV1';
 const bmiCard=[...document.querySelectorAll('h3')].find(x=>x.textContent.includes('Máy Tính BMI'))?.closest('.glass-card');
 if(!bmiCard)return;
 const value=bmiCard.querySelector('.text-5xl'); const result=value?.parentElement; const chart=bmiCard.querySelector('.space-y-2');
 const measurements=bmiCard.querySelector('.mt-6.pt-4 span'); const updateButton=[...bmiCard.querySelectorAll('button')].find(x=>x.textContent.includes('Cập nhật chỉ số'));
 const modal=document.getElementById('bmi-modal'), form=document.getElementById('bmi-form'), height=document.getElementById('bmi-height'), weight=document.getElementById('bmi-weight'), error=document.getElementById('bmi-error');
 const status=bmiCard.querySelector('.flex.items-start.justify-between > span');
 const detail=result?.querySelector('div'); const detailTop=detail?.children[0]; const detailAdvice=detail?.children[1];
 const open=()=>{try{const d=JSON.parse(localStorage.getItem(bmiKey)||'null');if(d){height.value=d.height;weight.value=d.weight;}}catch(_){} modal.hidden=false;};
 updateButton?.addEventListener('click',e=>{e.preventDefault();open();});
 document.getElementById('bmi-cancel').addEventListener('click',()=>modal.hidden=true);
 const show=(d)=>{const bmi=d.weight/((d.height/100)**2);const rounded=bmi.toFixed(1);value.textContent=rounded;result.hidden=false;chart.hidden=false;status.hidden=false;let label,advice,color;
   if(bmi<18.5){label='Thiếu cân';advice='Tham khảo chuyên gia dinh dưỡng.';color='text-sky-400';}
   else if(bmi<25){label='Trong ngưỡng tham khảo';advice='Duy trì vận động và ăn uống cân bằng.';color='text-emerald-400';}
   else if(bmi<30){label='Thừa cân';advice='Có thể trao đổi với chuyên gia y tế.';color='text-amber-400';}
   else{label='Béo phì theo ngưỡng BMI';advice='Nên trao đổi với chuyên gia y tế.';color='text-red-400';}
   status.textContent=label;status.className='px-3 py-1 rounded-full text-xs font-bold border '+color+' bg-white/5';detailTop.textContent=label;detailAdvice.textContent=advice;detailAdvice.className=color;measurements.textContent='Chiều cao: '+d.height+' cm · Cân nặng: '+d.weight+' kg';measurements.classList.remove('hidden');
   const indicator=bmiCard.querySelector('#bmi-indicator');if(indicator)indicator.style.left=Math.max(1,Math.min(99,((bmi-10)/30)*100))+'%';
   const profile=JSON.parse(localStorage.getItem('smurfProfileV1')||'null');if(profile?.birthday){const age=Math.floor((Date.now()-new Date(profile.birthday+'T00:00:00').getTime())/31557600000);if(age<18){detailTop.textContent='Đã tính BMI';detailAdvice.textContent='Người dưới 18 tuổi cần biểu đồ BMI theo tuổi.';}}
 };
 try{const d=JSON.parse(localStorage.getItem(bmiKey)||'null');if(d&&d.height&&d.weight)show(d);else{value.textContent='--';result.hidden=false;chart.hidden=true;status.hidden=true;detailTop.textContent='';detailAdvice.textContent='Nhập chiều cao và cân nặng sau khi nhấn Cập nhật chỉ số.';measurements.textContent='Chiều cao: -- · Cân nặng: --';}}catch(_){value.textContent='--';result.hidden=false;chart.hidden=true;status.hidden=true;detailTop.textContent='';detailAdvice.textContent='Nhập chiều cao và cân nặng sau khi nhấn Cập nhật chỉ số.';measurements.textContent='Chiều cao: -- · Cân nặng: --';}
 form.addEventListener('submit',e=>{e.preventDefault();error.textContent='';const h=Number(height.value),w=Number(weight.value);if(!Number.isFinite(h)||!Number.isFinite(w)||h<80||h>250||w<20||w>350){error.textContent='Chiều cao 80–250 cm và cân nặng 20–350 kg.';return;}const d={height:h,weight:w};localStorage.setItem(bmiKey,JSON.stringify(d));show(d);modal.hidden=true;});
 const attendanceCard=[...document.querySelectorAll('.glass-card')].find(x=>x.textContent.includes('Mục Tiêu Tuần Này'));
 if(!attendanceCard)return;
 const streakLabel=document.getElementById('attendance-streak');const weekGrid=attendanceCard.querySelector('.mt-5.grid.grid-cols-7');if(!weekGrid)return;
 const countText=attendanceCard.querySelector('.mt-6.space-y-2 strong');const weekRemain=attendanceCard.querySelector('.mt-6.space-y-2 .text-amber-400');const progress=attendanceCard.querySelector('.h-2.w-full > div');
 const button=document.createElement('button');button.type='button';button.id='attendance-button';button.className='mt-4 w-full rounded-xl bg-appleNeon px-4 py-2.5 text-sm font-bold text-black hover:bg-[#bbf048]';button.textContent='Điểm danh hôm nay';weekGrid.parentElement.insertBefore(button,weekGrid);
 const message=document.createElement('p');message.className='mt-2 min-h-4 text-xs text-zinc-400';button.after(message);
 const iso=(d)=>{const x=new Date(d.getTime()-d.getTimezoneOffset()*60000);return x.toISOString().slice(0,10);};
 const read=()=>{try{const v=JSON.parse(localStorage.getItem(attendanceKey)||'[]');return Array.isArray(v)?[...new Set(v.filter(x=>/^\d{4}-\d{2}-\d{2}$/.test(x)))].sort():[];}catch(_){return[];}};
 const render=()=>{const dates=read(),today=new Date(),todayKey=iso(today),marked=new Set(dates);let streak=0;const cursor=new Date(today);if(!marked.has(todayKey))cursor.setDate(cursor.getDate()-1);while(marked.has(iso(cursor))){streak++;cursor.setDate(cursor.getDate()-1);}streakLabel.textContent='Chuỗi '+streak+' ngày';
   const monday=new Date(today);monday.setHours(0,0,0,0);monday.setDate(monday.getDate()-(monday.getDay()+6)%7);const names=['T2','T3','T4','T5','T6','T7','CN'];
   [...weekGrid.children].forEach((item,i)=>{const day=new Date(monday);day.setDate(monday.getDate()+i);const key=iso(day),label=item.querySelector('span'),circle=item.querySelector('div');if(label)label.textContent=names[i];if(circle){circle.textContent=marked.has(key)?'✓':(key===todayKey?'·':'');circle.className='w-9 h-9 rounded-full flex items-center justify-center text-xs font-bold '+(marked.has(key)?'bg-emerald-500/20 border border-emerald-500/40 text-emerald-400':key===todayKey?'bg-appleNeon text-black shadow-glow-neon':'bg-zinc-800/80 border border-white/5 text-zinc-500');}});
   const start=new Date(monday);const end=new Date(monday);end.setDate(end.getDate()+6);const weekCount=dates.filter(x=>{const d=new Date(x+'T00:00:00');return d>=start&&d<=end;}).length;if(countText)countText.textContent=weekCount+'/7 ngày ('+Math.round(weekCount/7*100)+'%)';if(weekRemain)weekRemain.textContent='Còn '+(7-weekCount)+' ngày';if(progress)progress.style.width=(weekCount/7*100)+'%';
   const done=marked.has(todayKey);button.disabled=done;button.textContent=done?'Đã điểm danh hôm nay':'Điểm danh hôm nay';button.classList.toggle('opacity-60',done);message.textContent=done?'Hôm nay đã được ghi nhận trên thiết bị này.':'';
 };
 button.addEventListener('click',()=>{const dates=read(),todayKey=iso(new Date());if(!dates.includes(todayKey)){dates.push(todayKey);localStorage.setItem(attendanceKey,JSON.stringify(dates));}render();});render();
})();
</script>

</body></html>"""
