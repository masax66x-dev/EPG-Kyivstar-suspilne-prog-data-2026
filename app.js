// State variables
let programs = [];
let localPrograms = [];
let sortedChannels = [];
let groupedPrograms = {}; // Channel -> Date -> [Program]
let groupedLocalPrograms = {}; // Date -> [Program]
let activeChannel = "";
let isEnglish = false;
let activeTab = "all"; // 'all' or 'local'
let translations = {};
let lastVisibleStartTime = "";

// DOM Elements
const contentArea = document.getElementById("content-area");
const channelSelect = document.getElementById("channel-select");
const channelPickerWrapper = document.getElementById("channel-picker-wrapper");
const langToggleBtn = document.getElementById("lang-toggle");
const langText = document.getElementById("lang-text");
const tabBtns = document.querySelectorAll(".tab-btn");
const loadingEl = document.getElementById("loading");

// Constants
const regions = ["Київ", "Львів", "Одеса", "Дніпро", "Харків", "Вінниця", "Волинь", "Донбас", "Житомир", "Закарпаття", "Запоріжжя", "Івано-Франківськ", "Кропивницький", "Миколаїв", "Полтава", "Рівне", "Суми", "Тернопіль", "Херсон", "Хмельницький", "Черкаси", "Чернівці", "Чернігів", "Крим", "Луцьк", "Ужгород"];

// Transliterate function fallback
const cyrillicToLatin = {
    'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'H', 'Ґ': 'G', 'Д': 'D', 'Е': 'E', 'Є': 'Ye', 'Ж': 'Zh', 'З': 'Z',
    'И': 'Y', 'І': 'I', 'Ї': 'Yi', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O', 'П': 'P',
    'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch',
    'Ь': "'", 'Ю': 'Yu', 'Я': 'Ya',
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'h', 'ґ': 'g', 'д': 'd', 'е': 'e', 'є': 'ye', 'ж': 'zh', 'з': 'z',
    'и': 'y', 'і': 'i', 'ї': 'yi', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p',
    'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
    'ь': "'", 'ю': 'yu', 'я': 'ya'
};

function transliterate(text) {
    if (!text) return text;
    return text.split('').map(char => cyrillicToLatin[char] || char).join('');
}

// Translate function
function t(text) {
    if (!isEnglish || !text) return text;
    // Fast lookup
    if (translations[text]) return translations[text];
    return transliterate(text); // Fallback
}

// Format Date string: "YYYY-MM-DD" -> "YYYY/MM/DD (Day)"
function formatDateString(dateStr) {
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return dateStr;
    const daysEn = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
    const daysUa = ["Нд", "Пн", "Вв", "Ср", "Чт", "Пт", "Сб"];
    const day = isEnglish ? daysEn[d.getDay()] : daysUa[d.getDay()];
    return `${dateStr.replace(/-/g, '/')} (${day})`;
}

// Initializer
async function init() {
    try {
        // Load translations
        const transRes = await fetch("translations.json");
        translations = await transRes.json();

        // Load CSV with PapaParse
        Papa.parse("multichannel_max_epg.csv", {
            download: true,
            header: true,
            complete: function(results) {
                processData(results.data);
            }
        });
    } catch (e) {
        document.getElementById("loading-text").innerText = "Error loading data.";
        console.error("Init error:", e);
    }
}

function processData(data) {
    // Filter invalid rows
    programs = data.filter(row => row['Start Time'] && row['Channel Name']);
    
    // Build channels
    const channelsSet = new Set(programs.map(p => p['Channel Name']));
    sortedChannels = Array.from(channelsSet).sort();
    
    if (sortedChannels.length > 0) {
        activeChannel = sortedChannels[0];
    }
    
    // Group All Channels
    sortedChannels.forEach(c => groupedPrograms[c] = {});
    programs.forEach(p => {
        const c = p['Channel Name'];
        const dateStr = p['Start Time'].split(" ")[0];
        if (!groupedPrograms[c][dateStr]) groupedPrograms[c][dateStr] = [];
        groupedPrograms[c][dateStr].push(p);
    });
    
    // Extract & Group Local Programs
    programs.forEach(p => {
        const title = p['Program Title'];
        const channel = p['Channel Name'];
        let isLocal = false;
        
        const isRegionalChannel = regions.some(r => channel.includes(r)) || channel.includes("Suspilne");
        const isNationalFeed = title === "Суспільне Новини" || title.includes("Єдині новини") || channel.includes("Перший") || channel.includes("Спорт") || channel.includes("Культура") || channel.includes("First HD");
        
        if (isRegionalChannel && !isNationalFeed) {
            if (regions.some(r => title.includes(r))) {
                isLocal = true;
            } else if (["Тиждень", "Головне", "Студія", "Ранок", "Наживо"].some(kw => title.includes(kw))) {
                isLocal = true;
            }
        }
        
        if (isLocal) {
            localPrograms.push(p);
            const dateStr = p['Start Time'].split(" ")[0];
            if (!groupedLocalPrograms[dateStr]) groupedLocalPrograms[dateStr] = [];
            groupedLocalPrograms[dateStr].push(p);
        }
    });
    
    // Sort items within dates
    Object.values(groupedPrograms).forEach(dateGroups => {
        Object.values(dateGroups).forEach(list => list.sort((a,b) => a['Start Time'].localeCompare(b['Start Time'])));
    });
    Object.values(groupedLocalPrograms).forEach(list => list.sort((a,b) => a['Start Time'].localeCompare(b['Start Time'])));

    // Setup UI
    populateChannelSelect();
    loadingEl.style.display = "none";
    renderUI();
}

function populateChannelSelect() {
    channelSelect.innerHTML = "";
    sortedChannels.forEach(c => {
        const opt = document.createElement("option");
        opt.value = c;
        opt.innerText = t(c);
        if (c === activeChannel) opt.selected = true;
        channelSelect.appendChild(opt);
    });
}

// Generate single row HTML
function generateRowHTML(p, showChannelBadge) {
    const startTimeParts = p['Start Time'].split(" ")[1].split(":");
    const endTimeParts = p['End Time'].split(" ")[1].split(":");
    const startStr = `${startTimeParts[0]}:${startTimeParts[1]}`;
    const endStr = `${endTimeParts[0]}:${endTimeParts[1]}`;
    
    const badgeHTML = showChannelBadge ? `<div class="channel-badge">${t(p['Channel Name'])}</div>` : '';
    
    // ID used for scrolling
    const id = `prog-${p['Start Time'].replace(/[: ]/g, '-')}-${p['Channel Name'].replace(/[^a-zA-Z]/g, '')}`;

    return `
        <div class="program-row" id="${id}" data-time="${p['Start Time']}">
            <div class="time-col">
                <div class="time-start">${startStr}</div>
                <div class="time-end">${endStr}</div>
            </div>
            <div class="separator"></div>
            <div class="details-col">
                ${badgeHTML}
                <div class="prog-title">${t(p['Program Title'])}</div>
                <div class="duration-badge">${p['Duration (mins)']} mins</div>
                <div class="prog-desc">${t(p['Description'])}</div>
            </div>
        </div>
    `;
}

// Intersection Observer for scroll tracking
let observer;
function setupIntersectionObserver() {
    if (observer) observer.disconnect();
    observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                lastVisibleStartTime = entry.target.getAttribute('data-time');
            }
        });
    }, { root: contentArea, rootMargin: "-10% 0px -80% 0px" });
    
    document.querySelectorAll('.program-row').forEach(row => observer.observe(row));
}

function scrollToClosest() {
    if (!lastVisibleStartTime) return;
    const targetTime = new Date(lastVisibleStartTime).getTime();
    if (isNaN(targetTime)) return;

    let closestEl = null;
    let minDiff = Infinity;

    document.querySelectorAll('.program-row').forEach(row => {
        const t = new Date(row.getAttribute('data-time')).getTime();
        const diff = Math.abs(t - targetTime);
        if (diff < minDiff) {
            minDiff = diff;
            closestEl = row;
        }
    });

    if (closestEl) {
        // Scroll slightly above center
        closestEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

function renderUI() {
    contentArea.innerHTML = "";
    document.getElementById("tab-all-text").innerText = isEnglish ? "All Channels" : "Всі канали";
    document.getElementById("tab-local-text").innerText = isEnglish ? "Local Regions" : "Місцеві";
    document.getElementById("channel-label").innerText = isEnglish ? "Select Channel" : "Оберіть канал";
    
    populateChannelSelect(); // Re-populate for translation

    if (activeTab === "all") {
        document.getElementById("app-title").innerText = isEnglish ? `Suspilne EPG (${sortedChannels.length} Channels)` : `Суспільне EPG (${sortedChannels.length} канали)`;
        channelPickerWrapper.style.display = "flex";
        
        const dateGroups = groupedPrograms[activeChannel];
        if (dateGroups) {
            Object.keys(dateGroups).sort().forEach(date => {
                const header = `<div class="date-header">${formatDateString(date)}</div>`;
                const rows = dateGroups[date].map(p => generateRowHTML(p, false)).join('');
                contentArea.insertAdjacentHTML('beforeend', header + rows);
            });
        }
    } else {
        document.getElementById("app-title").innerText = isEnglish ? "Local Broadcasts" : "Місцеві трансляції";
        channelPickerWrapper.style.display = "none";
        
        Object.keys(groupedLocalPrograms).sort().forEach(date => {
            const header = `<div class="date-header">${formatDateString(date)}</div>`;
            const rows = groupedLocalPrograms[date].map(p => generateRowHTML(p, true)).join('');
            contentArea.insertAdjacentHTML('beforeend', header + rows);
        });
    }
    
    setupIntersectionObserver();
}

// Events
langToggleBtn.addEventListener("click", () => {
    isEnglish = !isEnglish;
    langText.innerText = isEnglish ? "EN" : "UA";
    renderUI();
});

channelSelect.addEventListener("change", (e) => {
    activeChannel = e.target.value;
    renderUI();
    // Use setTimeout to allow DOM to layout before scrolling
    setTimeout(scrollToClosest, 100);
});

tabBtns.forEach(btn => {
    btn.addEventListener("click", (e) => {
        tabBtns.forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        
        activeTab = btn.getAttribute("data-tab");
        renderUI();
        setTimeout(scrollToClosest, 100);
    });
});

// Boot
init();
