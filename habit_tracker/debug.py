import sys
with open(r"c:\xampp\htdocs\new_project\habit_tracker\templates\dashboard.html", "r", encoding="utf-8") as f:
    text = f.read()

start1 = text.find("        <!-- AI Coach Insights -->")
end1 = text.find("        </section>\n", start1)
print(f"AI Coach start: {start1}, end: {end1}")
next_text = text[end1+19:end1+50]
print(f"Text after AI coach: {repr(next_text)}")

start2 = text.find('id="coachCorner"')
print(f"coachCorner id found at: {start2}")
if start2 != -1:
    print(f"Line around it: {repr(text[start2-20:start2+50])}")

