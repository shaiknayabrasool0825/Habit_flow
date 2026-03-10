import sys

with open(r"c:\xampp\htdocs\new_project\habit_tracker\templates\dashboard.html.bak", "r", encoding="utf-8") as f:
    html = f.read()

blocks = {}
def grab(name, start_str, end_str):
    global html
    s = html.find(start_str)
    if s == -1: raise Exception(f"Missing {name} start")
    e = html.find(end_str, s)
    if e == -1: raise Exception(f"Missing {name} end")
    e += len(end_str)
    blocks[name] = html[s:e]
    html = html[:s] + html[e:]
    print(f"Extracted {name}: {len(blocks[name])} chars")

grab("ai_coach", "        <!-- AI Coach Insights -->", "\n        </section>\n")
grab("coach_corner", '        <section id="coachCorner"', "\n        </section>\n")
grab("reports", '        <section id="reportsSection"', "\n        </section>\n")

# For habits grid, let's be careful.
s = html.find('        <div class="habits-grid">')
e = html.find('        </div> <!-- Close dashboard-grid or main container -->\n', s)
if s == -1 or e == -1: raise Exception("Missing habits_grid")
e += len('        </div> <!-- Close dashboard-grid or main container -->\n')
blocks["habits_grid"] = html[s:e]
html = html[:s] + html[e:]
print(f"Extracted habits_grid: {len(blocks['habits_grid'])} chars")

grab("charts", '        <!-- Charts Section -->', "\n        </section>\n")
grab("contribution", '        <!-- Contribution Graph Section -->', '\n        </section>\n')

# Let's fix the extra closing section tag manually
html = html.replace('\n        </section>\n    </div>', '\n    </div>')

# Extract weekly review
s = blocks["habits_grid"].find("            <!-- Weekly Review Section -->")
e = blocks["habits_grid"].find("\n            </div>\n\n", s)
if s == -1 or e == -1: raise Exception("Missing weekly_review")
e += len("\n            </div>\n\n")
blocks["weekly_review"] = blocks["habits_grid"][s:e]
blocks["habits_grid"] = blocks["habits_grid"][:s] + blocks["habits_grid"][e:]

tabs_html = """
        <!-- Tab Navigation Bar -->
        <div class="tab-bar">
            <button class="tab-button active-tab" id="tabToday" onclick="DashboardTabs.switchTab('today')">Today</button>
            <button class="tab-button" id="tabInsights" onclick="DashboardTabs.switchTab('insights')">Insights</button>
            <button class="tab-button" id="tabHistory" onclick="DashboardTabs.switchTab('history')">History</button>
        </div>

        <div id="todayContent">
"""

insights_html = """
        </div>

        <div id="insightsContent" style="display: none;">
"""

history_html = """
        </div>

        <div id="historyContent" style="display: none;">
"""

close_html = """
        </div>
"""

header_end_str = '        </header>\n'
header_end = html.find(header_end_str)
if header_end == -1: raise Exception("Missing header end")
header_end += len(header_end_str)

style_start_str = '        <style>\n            .badge-streak {'
style_start = html.find(style_start_str)
if style_start == -1: style_start = len(html)

part1 = html[:header_end]
middle = html[header_end:style_start]
part2 = html[style_start:]

final_html = (
    part1 + 
    tabs_html + 
    middle + 
    blocks["habits_grid"] + 
    insights_html + 
    blocks["ai_coach"] + 
    blocks["coach_corner"] + 
    blocks["weekly_review"] + 
    history_html + 
    blocks["charts"] + 
    blocks["contribution"] + 
    blocks["reports"] + 
    close_html + 
    part2
)

with open(r"c:\xampp\htdocs\new_project\habit_tracker\templates\dashboard.html", "w", encoding="utf-8") as f:
    f.write(final_html)

print("SUCCESS")
