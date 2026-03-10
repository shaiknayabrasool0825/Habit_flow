import glob
import os

fav_tag = "    <link rel=\"icon\" href=\"{{ url_for('static', filename='favicon.svg') }}\" type=\"image/svg+xml\">\n"

for f in glob.glob('templates/*.html'):
    with open(f, 'r', encoding='utf-8') as file:
        content = file.readlines()
        
    full_text = "".join(content)
    if 'favicon.svg' in full_text:
        continue
        
    with open(f, 'w', encoding='utf-8') as file:
        for line in content:
            file.write(line)
            if '<title>' in line:
                file.write(fav_tag)
                
    print(f"Updated {f}")
