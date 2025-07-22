document.addEventListener("DOMContentLoaded", () => {
  // قراءة البيانات من القالب مرة واحدة عند تحميل الصفحة
  let all_achievements_data = {};
  const achievementsDataElement = document.getElementById("achievements-data");
  if (achievementsDataElement && achievementsDataElement.textContent) {
    try {
      all_achievements_data = JSON.parse(achievementsDataElement.textContent);
    } catch (e) {
      console.error("Error parsing achievements-data JSON:", e);
    }
  } else {
    console.warn(
      "Element with ID 'achievements-data' not found or empty. Achievements popups might not work."
    );
  }

  const progressDataElement = document.getElementById("progress-data");
  let progress_data = { days_passed: 0, target_days: 0 };
  if (progressDataElement && progressDataElement.textContent) {
    try {
      progress_data = JSON.parse(progressDataElement.textContent);
    } catch (e) {
      console.error("Error parsing progress-data JSON:", e);
    }
  } else {
    console.warn("Element with ID 'progress-data' not found or empty.");
  }

  // --- 1. تهيئة شريط التقدم (GSAP) ---
  const progressBar = document.getElementById("progress-bar");
  const progressText = document.getElementById("progress-text");

  const daysPassed = progress_data.days_passed;
  const targetDays = progress_data.target_days;

  let progressPercentage = 0;
  if (targetDays > 0) {
    progressPercentage = (daysPassed / targetDays) * 100;
    if (progressPercentage > 100) progressPercentage = 100; // لا تتجاوز 100%
  }
  const targetWidth = progressPercentage;

  if (progressBar && progressText) {
    gsap.to(progressBar, {
      width: targetWidth + "%",
      duration: 2,
      ease: "power2.out",
      onUpdate: function () {
        // تحديث النص ليعكس النسبة المئوية المتحركة
        progressText.innerText =
          Math.round(this.progress() * targetWidth) + "%";
      },
      onComplete: function () {
        // التأكد من أن النص يعرض القيمة النهائية الدقيقة
        progressText.innerText = Math.round(targetWidth) + "%";
      },
    });
  } else {
    console.warn(
      "Progress bar or text element not found. Progress animation will not initialize."
    );
  }

  // --- 2. تهيئة الشخصية التفاعلية (Lottie) ---
  const lottieContainer = document.getElementById("lottie-character");
  if (lottieContainer) {
    const currentLevel = parseInt(lottieContainer.dataset.level, 10);

    // مسار ملف Lottie JSON. تأكد من وجوده في static/lottie/
    const lottiePath = "{% static 'lottie/plant_character.json' %}";

    const animation = lottie.loadAnimation({
      container: lottieContainer,
      renderer: "svg",
      loop: true,
      autoplay: true,
      path: lottiePath,
    });

    // تعديل سرعة وحجم الرسوم المتحركة بناءً على مستوى الشخصية
    const animationSpeed = 1 + currentLevel * 0.15; // كل مستوى يزيد السرعة بـ 15%
    const animationScale = 1 + currentLevel * 0.05; // كل مستوى يزيد الحجم بـ 5%

    animation.setSpeed(animationSpeed);
    lottieContainer.style.transform = `scale(${animationScale})`;

    // إضافة تفاعل عند النقر
    lottieContainer.addEventListener("click", () => {
      animation.setSpeed(animationSpeed * 2); // تسريع مؤقت عند النقر
      setTimeout(() => {
        animation.setSpeed(animationSpeed); // العودة للسرعة الأصلية بعد ثانية
      }, 1000);
    });
  } else {
    console.warn(
      "Lottie character container not found. Lottie animation will not initialize."
    );
  }

  // --- 3. تهيئة عرض الاقتباسات (Swiper) ---
  const swiperContainer = document.querySelector(".daily-quote-slider");
  if (swiperContainer && typeof Swiper !== "undefined") {
    // التأكد من تحميل Swiper
    const swiper = new Swiper(swiperContainer, {
      loop: true, // تدوير لا نهائي للاقتباسات
      autoplay: {
        delay: 8000, // تغيير الاقتباس كل 8 ثوانٍ
        disableOnInteraction: false, // لا يتوقف التشغيل التلقائي عند تفاعل المستخدم
      },
      effect: "fade", // تأثير التلاشي بين الاقتباسات
      fadeEffect: {
        crossFade: true, // تلاشي متقاطع
      },
      pagination: {
        // إضافة ترقيم للصفحات (نقاط التنقل)
        el: ".swiper-pagination",
        clickable: true,
      },
    });
  } else if (!swiperContainer) {
    console.warn(
      "Swiper container not found. Quote slider will not initialize."
    );
  } else {
    console.warn(
      "Swiper library not loaded. Quote slider will not initialize."
    );
  }
});

// هذا السكربت يستمع لحدث 'achievementsUnlocked' الذي يتم إطلاقه من views.py
// ويقوم بتشغيل النافذة المنبثقة للإنجازات في dashboard.html
document.body.addEventListener("achievementsUnlocked", function (evt) {
  // التأكد من أن all_achievements_data تم تهيئتها
  if (
    !all_achievements_data ||
    !all_achievements_data.confetti_types ||
    !all_achievements_data.sounds
  ) {
    console.error(
      "all_achievements_data is not properly initialized in main.js."
    );
    return;
  }

  const newlyUnlockedAchievements = evt.detail.newly_unlocked_for_popup; // تم التعديل هنا

  if (newlyUnlockedAchievements && newlyUnlockedAchievements.length > 0) {
    // Loop through each newly unlocked achievement and trigger the Alpine.js popup
    newlyUnlockedAchievements.forEach((ach, index) => {
      setTimeout(() => {
        // Dispatch a custom event that Alpine.js in dashboard.html listens to
        // This ensures the popup is shown for each achievement sequentially
        const popupEvent = new CustomEvent("achievementsUnlocked", {
          detail: { achievementsUnlocked: [ach] }, // Pass a single achievement for each popup
        });
        window.dispatchEvent(popupEvent);
      }, index * 3000); // 3-second delay between each achievement popup
    });
  } else {
    console.warn(
      "No newly unlocked achievements provided in the event detail."
    );
  }
});
