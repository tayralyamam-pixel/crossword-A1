import streamlit as st
import re

# ==========================================
# قاموس اللغات (Translation Dictionary)
# ==========================================
translations = {
    "العربية 🇸🇦": {
        "title": "🧩 مولّد الألغاز المتقاطعة الاحترافي",
        "settings": "⚙️ إعدادات اللغز",
        "lang_select": "🌐 اختر لغة الواجهة:",
        "mode_select": "اختر نوع اللغز:",
        "mode_lang": "لغات (أحرف)",
        "mode_math": "رياضيات (أرقام وعمليات)",
        "grid_size": "حجم الشبكة (درجة الصعوبة):",
        "colors_header": "🎨 تخصيص الألوان (للفيكتور)",
        "color_bg": "لون المربعات (الخلفية):",
        "color_stroke": "لون الحدود (الخطوط):",
        "color_text": "لون الأحرف/الأرقام:",
        "current_mode_text": "الوضع الحالي:",
        "current_size_text": "حجم الشبكة:",
        "input_label": "أدخل البيانات (الصيغة: الكلمة/المعادلة = الدليل/السؤال):",
        "btn_generate": "توليد اللغز 🚀",
        "err_format": "الرجاء إدخال البيانات بالصيغة الصحيحة.",
        "success_msg": "تم توليد اللغز بنجاح!",
        "btn_download": "📥 تحميل اللغز كملف (SVG) لبرامج التصميم",
        "clues_title": "الأدلة والأسئلة (Clues):",
        "clues_across": "أفقي (Across):",
        "clues_down": "عمودي (Down):"
    },
    "English 🇬🇧": {
        "title": "🧩 Pro Crossword Puzzle Generator",
        "settings": "⚙️ Puzzle Settings",
        "lang_select": "🌐 Choose UI Language:",
        "mode_select": "Choose puzzle type:",
        "mode_lang": "Languages (Letters)",
        "mode_math": "Math (Numbers & Operations)",
        "grid_size": "Grid Size (Difficulty):",
        "colors_header": "🎨 Color Customization (for Vector)",
        "color_bg": "Cell Background Color:",
        "color_stroke": "Cell Border Color:",
        "color_text": "Text/Token Color:",
        "current_mode_text": "Current Mode:",
        "current_size_text": "Grid Size:",
        "input_label": "Enter data (Format: Word/Equation = Clue/Question):",
        "btn_generate": "Generate Puzzle 🚀",
        "err_format": "Please enter data in the correct format.",
        "success_msg": "Puzzle generated successfully!",
        "btn_download": "📥 Download Puzzle (SVG)",
        "clues_title": "Clues:",
        "clues_across": "Across:",
        "clues_down": "Down:"
    },
    "Français 🇫🇷": {
        "title": "🧩 Générateur de Mots Croisés Pro",
        "settings": "⚙️ Paramètres du Puzzle",
        "lang_select": "🌐 Choisir la langue:",
        "mode_select": "Choisissez le type de puzzle :",
        "mode_lang": "Langues (Lettres)",
        "mode_math": "Maths (Nombres & Opérations)",
        "grid_size": "Taille de la grille (Difficulté) :",
        "colors_header": "🎨 Personnalisation des couleurs",
        "color_bg": "Couleur d'arrière-plan des cellules:",
        "color_stroke": "Couleur de bordure des cellules:",
        "color_text": "Couleur du texte/jeton:",
        "current_mode_text": "Mode actuel :",
        "current_size_text": "Taille de la grille :",
        "input_label": "Entrez les données (Format : Mot/Équation = Indice/Question) :",
        "btn_generate": "Générer le Puzzle 🚀",
        "err_format": "Veuillez entrer les données au bon format.",
        "success_msg": "Puzzle généré avec succès !",
        "btn_download": "📥 Télécharger le Puzzle (SVG)",
        "clues_title": "Indices :",
        "clues_across": "Horizontal :",
        "clues_down": "Vertical :"
    }
}

EMPTY = "."

def create_grid(size):
    return [[EMPTY for _ in range(size)] for _ in range(size)]

def can_place_tokens(grid, tokens, row, col, direction, grid_size):
    if direction == "H" and col + len(tokens) > grid_size: return False
    if direction == "V" and row + len(tokens) > grid_size: return False
    for i in range(len(tokens)):
        r = row if direction == "H" else row + i
        c = col + i if direction == "H" else col
        if grid[r][c] != EMPTY and grid[r][c] != tokens[i]: return False
    return True

def place_tokens(grid, tokens, row, col, direction):
    for i in range(len(tokens)):
        r = row if direction == "H" else row + i
        c = col + i if direction == "H" else col
        grid[r][c] = tokens[i]

def generate_crossword(data_dict, mode_is_math, grid_size):
    grid = create_grid(grid_size)
    processed_data = []
    
    for word, clue in data_dict.items():
        if mode_is_math:
            tokens = re.findall(r'\d+|[+\-*/=]', word) 
        else:
            tokens = list(word.upper().replace(" ", ""))
            
        if tokens:
            processed_data.append({'original': word, 'tokens': tokens, 'clue': clue})
            
    processed_data.sort(key=lambda x: len(x['tokens']), reverse=True)
    placed_words = []
    
    for item in processed_data:
        tokens = item['tokens']
        placed = False
        
        if not placed_words:
            row = grid_size // 2
            col = (grid_size - len(tokens)) // 2
            place_tokens(grid, tokens, row, col, "H")
            placed_words.append({'tokens': tokens, 'row': row, 'col': col, 'dir': "H", 'clue': item['clue']})
            continue

        for p_word in placed_words:
            if placed: break
            for i, p_token in enumerate(p_word['tokens']):
                if placed: break
                for j, token in enumerate(tokens):
                    if p_token == token:
                        new_dir = "V" if p_word['dir'] == "H" else "H"
                        new_row = p_word['row'] - j if p_word['dir'] == "H" else p_word['row'] + i
                        new_col = p_word['col'] + i if p_word['dir'] == "H" else p_word['col'] - j
                            
                        if new_row >= 0 and new_col >= 0 and can_place_tokens(grid, tokens, new_row, new_col, new_dir, grid_size):
                            place_tokens(grid, tokens, new_row, new_col, new_dir)
                            placed_words.append({'tokens': tokens, 'row': new_row, 'col': new_col, 'dir': new_dir, 'clue': item['clue']})
                            placed = True
                            break
                            
    number_map = {}
    current_number = 1
    final_clues = {"Across": [], "Down": []}
    
    for w in placed_words:
        coord = (w['row'], w['col'])
        if coord in number_map: num = number_map[coord]
        else:
            number_map[coord] = current_number
            num = current_number
            current_number += 1
            
        section = "Across" if w['dir'] == "H" else "Down"
        final_clues[section].append(f"{num}. {w['clue']}")

    return grid, number_map, final_clues

def get_svg_string(grid, number_map, clues, grid_size, t, cell_bg, cell_stroke, text_color):
    cell_size = 40
    grid_width = grid_size * cell_size
    total_height = (grid_size * cell_size) + 350 
    
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {grid_width} {total_height}" width="100%" height="100%">\n'
    svg += '  <rect width="100%" height="100%" fill="#ffffff"/>\n'
    
    for row in range(grid_size):
        for col in range(grid_size):
            token = grid[row][col]
            if token != EMPTY:
                x = col * cell_size
                y = row * cell_size
                # استخدام الألوان المختارة من المستخدم
                svg += f'  <rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" fill="{cell_bg}" stroke="{cell_stroke}" stroke-width="2"/>\n'
                
                if (row, col) in number_map:
                    num = number_map[(row, col)]
                    # استخدام لون الحدود كإشارة للرقم التسلسلي الصغير
                    svg += f'  <text x="{x + 4}" y="{y + 12}" font-family="Arial" font-size="11" fill="{cell_stroke}" font-weight="bold">{num}</text>\n'
                
                font_size = 18 if len(token) == 1 else 13
                # استخدام لون النص المختار
                svg += f'  <text x="{x + cell_size/2}" y="{y + cell_size/2 + 4}" font-family="Arial" font-size="{font_size}" text-anchor="middle" dominant-baseline="middle" font-weight="bold" fill="{text_color}">{token}</text>\n'
                
    y_clues = (grid_size * cell_size) + 30
    svg += f'  <text x="20" y="{y_clues}" font-family="Arial" font-size="18" font-weight="bold" fill="black">{t["clues_title"]}</text>\n'
    
    y_clues += 25
    svg += f'  <text x="20" y="{y_clues}" font-family="Arial" font-size="14" font-weight="bold" fill="black">{t["clues_across"]}</text>\n'
    for clue in clues["Across"]:
        y_clues += 20
        svg += f'  <text x="30" y="{y_clues}" font-family="Arial" font-size="13" fill="black">{clue}</text>\n'
        
    y_clues += 30
    svg += f'  <text x="20" y="{y_clues}" font-family="Arial" font-size="14" font-weight="bold" fill="black">{t["clues_down"]}</text>\n'
    for clue in clues["Down"]:
        y_clues += 20
        svg += f'  <text x="30" y="{y_clues}" font-family="Arial" font-size="13" fill="black">{clue}</text>\n'
        
    svg += '</svg>'
    return svg

# ==========================================
# واجهة المستخدم (Web UI)
# ==========================================
st.set_page_config(page_title="مولّد الألغاز الاحترافي", page_icon="🧩", layout="wide")

# اختيار لغة الواجهة في البداية
selected_lang = st.sidebar.selectbox("🌐 لغة الواجهة / UI Language / Langue:", ["العربية 🇸🇦", "English 🇬🇧", "Français 🇫🇷"])
t = translations[selected_lang] # جلب القاموس الخاص باللغة المختارة

st.title(t["title"])
st.sidebar.header(t["settings"])

# إعدادات اللغز
mode = st.sidebar.radio(t["mode_select"], (t["mode_lang"], t["mode_math"]))
grid_size = st.sidebar.slider(t["grid_size"], min_value=10, max_value=40, value=20, step=1)

# تخصيص الألوان (الميزة التي عادت!)
st.sidebar.markdown("---")
st.sidebar.subheader(t["colors_header"])
cell_bg_color = st.sidebar.color_picker(t["color_bg"], "#FFFFFF") # الافتراضي أبيض
cell_stroke_color = st.sidebar.color_picker(t["color_stroke"], "#333333") # الافتراضي رمادي غامق
text_color = st.sidebar.color_picker(t["color_text"], "#000000") # الافتراضي أسود

st.write(f"**{t['current_mode_text']}** {mode} | **{t['current_size_text']}** {grid_size}x{grid_size}")

mode_is_math = (mode == t["mode_math"])

if mode_is_math:
    default_input = "50+30=80 = حاصل جمع خمسين وثلاثين\n12*12=144 = عملية ضرب\n100-25=75 = عملية طرح\n144/12=12 = عملية قسمة"
else:
    default_input = "APPLE = فاكهة حمراء\nBANANA = فاكهة صفراء\nORANGE = فاكهة برتقالية\nWATERMELON = بطيخ صيفي"

user_input = st.text_area(t["input_label"], default_input, height=150)

if st.button(t["btn_generate"]):
    data_dict = {}
    for line in user_input.split('\n'):
        if "=" in line:
            # الحل السحري للفصل بين المعادلة والدليل
            parts = line.rsplit("=", 1)
            word = parts[0].strip()
            clue = parts[1].strip()
            if word and clue:
                data_dict[word] = clue
                
    if not data_dict:
        st.error(t["err_format"])
    else:
        grid, num_map, final_clues = generate_crossword(data_dict, mode_is_math, grid_size)
        
        # تمرير كل المتغيرات للدالة: اللغة، حجم الشبكة، والألوان الثلاثة المختارة
        svg_output = get_svg_string(grid, num_map, final_clues, grid_size, t, cell_bg_color, cell_stroke_color, text_color)
        
        st.success(t["success_msg"])
        st.components.v1.html(svg_output, height=800, scrolling=True)
        
        st.download_button(
            label=t["btn_download"],
            data=svg_output,
            file_name="professional_puzzle.svg",
            mime="image/svg+xml"
        )
