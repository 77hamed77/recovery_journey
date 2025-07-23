// static/js/dashboard.js
document.addEventListener("DOMContentLoaded", () => {
  const all_achievements_data = JSON.parse(document.getElementById("achievements-data")?.textContent || '{}');
  const progress_data = JSON.parse(document.getElementById("progress-data").textContent);

  // تسجيل البيانات للتصحيح
  console.log("Achievements Data:", all_achievements_data);
  console.log("Journal Entries:", all_achievements_data.journal_entries);
  console.log("User Achievements:", all_achievements_data.user_achievements);

  const chartData = {
    7: getPeriodData(7),
    30: getPeriodData(30),
    90: getPeriodData(90)
  };

  function getPeriodData(days) {
    const today = new Date();
    const labels = [];
    const cleanDays = [];
    const relapses = [];

    for (let i = days - 1; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(today.getDate() - i);
      const dateStr = date.toISOString().split('T')[0];
      labels.push(dateStr);

      const entry = all_achievements_data.journal_entries?.find(entry => entry.entry_date === dateStr);
      cleanDays.push(entry && !entry?.is_relapse ? 1 : 0);
      relapses.push(entry?.is_relapse ? 1 : 0);
    }

    return { labels, cleanDays, relapses };
  }

  let recoveryChart;
  let currentPeriod = 7;

  function createRecoveryChart() {
    const ctx = document.getElementById('recoveryChart')?.getContext('2d');
    if (!ctx) {
      console.error("Canvas context not found!");
      return;
    }
    const data = chartData[currentPeriod];
    if (!data || !data.labels.length) {
      console.warn("No data available for the chart!");
      return;
    }

    recoveryChart = new Chart(ctx, {
      type: 'line', // مخطط خطي بسيط
      data: {
        labels: data.labels,
        datasets: [{
          label: 'أيام نظيفة',
          data: data.cleanDays,
          borderColor: 'rgb(34, 197, 94)',
          backgroundColor: 'rgba(34, 197, 94, 0.1)',
          borderWidth: 2,
          fill: true,
          pointBackgroundColor: data.relapses.map(r => r ? 'rgb(239, 68, 68)' : 'rgb(34, 197, 94)'),
          pointRadius: 4,
          pointHoverRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: true },
          tooltip: {
            callbacks: {
              label: function(context) {
                const value = context.raw === 1 ? 'نعم' : 'لا';
                return `${context.dataset.label}: ${value}`;
              },
              afterBody: function(context) {
                const index = context[0].dataIndex;
                if (data.relapses[index]) {
                  return ['⚠️ نكسة تم تسجيلها'];
                }
                return [];
              }
            }
          }
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: { color: '#6B7280', maxTicksLimit: currentPeriod }
          },
          y: {
            beginAtZero: true,
            max: 1,
            ticks: { color: '#6B7280', callback: value => value === 1 ? 'نعم' : 'لا' }
          }
        }
      }
    });
  }

  function updateChart(period) {
    if (currentPeriod === period) return;
    currentPeriod = period;
    const data = chartData[period];
    if (recoveryChart && data && data.labels.length) {
      recoveryChart.data.labels = data.labels;
      recoveryChart.data.datasets[0].data = data.cleanDays;
      recoveryChart.data.datasets[0].pointBackgroundColor = data.relapses.map(r => r ? 'rgb(239, 68, 68)' : 'rgb(34, 197, 94)');
      recoveryChart.options.scales.x.ticks.maxTicksLimit = period;
      recoveryChart.update();
    } else {
      console.warn("Chart or data not available for update!");
    }

    document.querySelectorAll('[id^="chart-"]').forEach(btn => {
      btn.classList.remove('bg-primary', 'text-white');
      btn.classList.add('bg-gray-200', 'text-gray-700');
    });
    document.getElementById(`chart-${period}days`).classList.remove('bg-gray-200', 'text-gray-700');
    document.getElementById(`chart-${period}days`).classList.add('bg-primary', 'text-white');
  }

  // تهيئة شريط التقدم باستخدام GSAP
  const progressBar = document.getElementById("progress-bar");
  const progressText = document.getElementById("progress-text");
  const daysPassed = progress_data.days_passed;
  const targetDays = progress_data.target_days;
  let progressPercentage = 0;
  if (targetDays > 0) {
    progressPercentage = (daysPassed / targetDays) * 100;
    if (progressPercentage > 100) progressPercentage = 100;
  }
  if (progressBar && progressText) {
    gsap.to(progressBar, {
      width: progressPercentage + "%",
      duration: 2,
      ease: "power2.out",
      onUpdate: function () {
        progressText.innerText = Math.round(this.progress() * progressPercentage) + "%";
      },
      onComplete: function () {
        progressText.innerText = Math.round(progressPercentage) + "%";
      },
    });
  } else {
    console.warn("Progress bar or text element not found.");
  }

  // تهيئة المخطط والأحداث
  createRecoveryChart();
  document.getElementById('chart-7days').addEventListener('click', () => updateChart(7));
  document.getElementById('chart-30days').addEventListener('click', () => updateChart(30));
  document.getElementById('chart-90days').addEventListener('click', () => updateChart(90));
});