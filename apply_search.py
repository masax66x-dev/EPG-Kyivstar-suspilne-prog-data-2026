import sys
import re

app_js_path = '/Users/MS-MBP14/Antigravity/APPM005/ProgramTableWeb/app.js'

with open(app_js_path, 'r', encoding='utf-8') as f:
    js_code = f.read()

# 1. Add Search DOM Elements & State
dom_old = """const downloadBtn = document.getElementById("download-csv");
const tabBtns = document.querySelectorAll(".tab-btn");"""
dom_new = """const downloadBtn = document.getElementById("download-csv");
const searchInput = document.getElementById("search-input");
const clearSearchBtn = document.getElementById("clear-search");
const tabBtns = document.querySelectorAll(".tab-btn");

let searchQuery = "";
let searchTerms = { and: [], or: [] };"""
js_code = js_code.replace(dom_old, dom_new)


# 2. Add search parsing and filtering logic
filter_code = """
// Search Logic
function parseSearchQuery(query) {
    query = query.toLowerCase().trim();
    if (!query) {
        searchTerms = { and: [], or: [] };
        return;
    }
    
    // Split by ' and ' or ' or '
    // Note: A simple implementation that prioritizes 'or' splits, then 'and' splits
    const orParts = query.split(/\s+or\s+/);
    searchTerms = { and: [], or: [] };
    
    if (orParts.length > 1) {
        searchTerms.or = orParts.map(p => p.trim()).filter(p => p);
    } else {
        const andParts = query.split(/\s+and\s+/);
        searchTerms.and = andParts.map(p => p.trim()).filter(p => p);
    }
}

function rowMatchesSearch(p) {
    if (!searchQuery) return true;
    
    const textToSearch = `${p['Program Title']} ${t(p['Program Title'])} ${p['Description']} ${t(p['Description'])} ${p['Channel Name']} ${t(p['Channel Name'])}`.toLowerCase();
    
    if (searchTerms.or.length > 0) {
        return searchTerms.or.some(term => textToSearch.includes(term));
    }
    
    if (searchTerms.and.length > 0) {
        return searchTerms.and.every(term => textToSearch.includes(term));
    }
    
    return textToSearch.includes(searchQuery.toLowerCase());
}
"""

# Inject before renderUI
js_code = js_code.replace("function renderUI() {", filter_code + "\nfunction renderUI() {")


# 3. Apply search filtering in renderUI loop
render_old_all = """            Object.keys(dateGroups).sort().forEach(date => {
                const header = `<div class="date-header">${formatDateString(date)}</div>`;
                const rows = dateGroups[date].map(p => generateRowHTML(p, false)).join('');
                contentArea.insertAdjacentHTML('beforeend', header + rows);
            });"""
render_new_all = """            Object.keys(dateGroups).sort().forEach(date => {
                const filtered = dateGroups[date].filter(rowMatchesSearch);
                if (filtered.length > 0) {
                    const header = `<div class="date-header">${formatDateString(date)}</div>`;
                    const rows = filtered.map(p => generateRowHTML(p, false)).join('');
                    contentArea.insertAdjacentHTML('beforeend', header + rows);
                }
            });"""
js_code = js_code.replace(render_old_all, render_new_all)

render_old_local = """        Object.keys(groupedLocalPrograms).sort().forEach(date => {
            const header = `<div class="date-header">${formatDateString(date)}</div>`;
            const rows = groupedLocalPrograms[date].map(p => generateRowHTML(p, true)).join('');
            contentArea.insertAdjacentHTML('beforeend', header + rows);
        });"""
render_new_local = """        Object.keys(groupedLocalPrograms).sort().forEach(date => {
            const filtered = groupedLocalPrograms[date].filter(rowMatchesSearch);
            if (filtered.length > 0) {
                const header = `<div class="date-header">${formatDateString(date)}</div>`;
                const rows = filtered.map(p => generateRowHTML(p, true)).join('');
                contentArea.insertAdjacentHTML('beforeend', header + rows);
            }
        });"""
js_code = js_code.replace(render_old_local, render_new_local)


# 4. Bind Search UI events
search_events = """
searchInput.addEventListener("input", (e) => {
    searchQuery = e.target.value;
    clearSearchBtn.style.display = searchQuery ? "flex" : "none";
    parseSearchQuery(searchQuery);
    renderUI();
});

clearSearchBtn.addEventListener("click", () => {
    searchInput.value = "";
    searchQuery = "";
    clearSearchBtn.style.display = "none";
    parseSearchQuery("");
    renderUI();
});
"""
# Inject into Events section
js_code = js_code.replace("// Events\n", "// Events\n" + search_events)


# 5. Fix Download CSV logic (Translate if English is selected)
dl_old = """downloadBtn.addEventListener("click", () => {
    const link = document.createElement("a");
    link.href = "multichannel_max_epg.csv";
    link.download = "multichannel_max_epg.csv";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
});"""

dl_new = """downloadBtn.addEventListener("click", () => {
    let csvContent = "";
    
    // Header
    csvContent += "Channel Name,Date,Start Time,End Time,Duration (mins),Program Title,Description\\n";
    
    // Use the actual data array based on active tab
    const dataToExport = activeTab === "all" ? programs : localPrograms;
    const filteredToExport = dataToExport.filter(rowMatchesSearch);
    
    // Rows
    filteredToExport.forEach(p => {
        const c = isEnglish ? t(p['Channel Name']) : p['Channel Name'];
        const d = p['Start Time'].split(" ")[0];
        const st = p['Start Time'];
        const et = p['End Time'];
        const dur = p['Duration (mins)'];
        // escape quotes
        let pt = isEnglish ? t(p['Program Title']) : p['Program Title'];
        pt = pt.replace(/"/g, '""');
        let desc = isEnglish ? t(p['Description']) : p['Description'];
        desc = desc.replace(/"/g, '""');
        
        csvContent += `"${c}",${d},${st},${et},${dur},"${pt}","${desc}"\\n`;
    });
    
    // Create Blob and Download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    
    const prefix = isEnglish ? "EN_" : "UA_";
    const tabName = activeTab === "all" ? "All_Channels" : "Local_Broadcasts";
    link.setAttribute("download", `${prefix}EPG_${tabName}.csv`);
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
});"""
js_code = js_code.replace(dl_old, dl_new)

with open(app_js_path, 'w', encoding='utf-8') as f:
    f.write(js_code)
    
print("Search logic and dynamic translate-on-download logic applied to app.js")
