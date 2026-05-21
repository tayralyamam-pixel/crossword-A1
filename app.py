import streamlit as st
import re
import random

# ==========================================
# قاموس اللغات (Translation Dictionary)
# ==========================================
translations = {
    "العربية 🇸🇦": {
        "title": "🧩 صانع الألغاز المتقاطعة الاحترافي",
        "settings": "⚙️ إعدادات اللغز",
        "lang_select": "🌐 لغة الواجهة:",
        "mode_select": "نوع اللغز:",
        "mode_lang": "لغات (أحرف)",
        "mode_math": "رياضيات (أرقام وعمليات)",
        "grid_size": "الحد الأقصى للشبكة:",
        "colors_header": "🎨 تخصيص الألوان",
        "color_bg": "لون المربعات (الخلفية):",
        "color_stroke": "لون الحدود (الخطوط):",
        "color_text": "لون الأحرف/الأرقام:",
        "title_label": "عنوان اللغز (اختياري):",
        "input_label": "أدخل البيانات (الكلمة/المعادلة = الدليل):",
        "btn_generate": "توليد اللغز 🚀",
        "err_format": "الرجاء إدخال البيانات بالصيغة الصحيحة.",
        "success_msg": "تم توليد اللغز! استخدم الأزرار بالأسفل لتغيير الشكل.",
        "preview_label": "👀 معاينة الشكل:",
        "btn_prev_layout": "⬅️ الشكل السابق",
        "btn_next_layout": "الشكل التالي ➡️",
        "btn_download": "📥 تحميل (SVG)",
        "clues_title": "الأدلة والأسئلة (Clues):",
        "clues_across": "أفقي (Across):",
        "clues_down": "عمودي (Down):",
        "warning_unplaced": "⚠️ بعض الكلمات لم تجد مساحة! جرب تكبير حجم الشبكة أو الضغط على (الشكل التالي)."
    },
    "English 🇬🇧": {
        "title": "🧩 Pro Crossword Puzzle Maker",
        "settings": "⚙️ Settings",
        "lang_select": "🌐 UI Language:",
        "mode_select": "Puzzle Type:",
        "mode_lang": "Languages (Letters)",
        "mode_math": "Math (Numbers/Ops)",
        "grid_size": "Max Grid Size:",
        "colors_header": "🎨 Colors",
        "color_bg": "Cell Background:",
        "color_stroke": "Border Color:",
        "color_text": "Text Color:",
        "title_label": "Puzzle Title (Optional):",
        "input_label": "Enter Data (Word/Equation = Clue):",
        "btn_generate": "Generate Puzzle 🚀",
        "err_format": "Please use the correct format.",
        "success_msg": "Puzzle ready! Use buttons below to change layout.",
        "preview_label": "👀 Layout Preview:",
        "btn_prev_layout": "⬅️ Previous Layout",
        "btn_next_layout": "Next Layout ➡️",
        "btn_download": "📥 Download (SVG)",
        "clues_title": "Clues:",
        "clues_across": "Across:",
        "clues_down": "Down:",
        "warning_unplaced": "⚠️ Some words couldn't fit! Try increasing grid size or clicking Next Layout."
    },
    "Français 🇫🇷": {
        "title": "🧩 Créateur de Mots Croisés Pro",
        "settings": "⚙️ Paramètres",
        "lang_select": "🌐 Langue de l'interface:",
        "mode_select": "Type de Puzzle:",
        "mode_lang": "Langues (Lettres)",
        "mode_math": "Maths (Nombres/Ops)",
        "grid_size": "Taille Max Grille:",
        "colors_header": "🎨 Couleurs",
        "color_bg": "Fond des cellules:",
        "color_stroke": "Couleur des bordures:",
        "color_text": "Couleur du texte:",
        "title_label": "Titre du Puzzle (Optionnel):",
        "input_label": "Entrez les données (Mot/Équation = Indice):",
        "btn_generate": "Générer le Puzzle 🚀",
        "err_format": "Veuillez utiliser le bon format.",
        "success_msg": "Puzzle prêt ! Changez la disposition ci-dessous.",
        "preview_label": "👀 Aperçu de la disposition:",
        "btn_prev_layout": "⬅️ Disposition Précédente",
        "btn_next_layout": "Disposition Suivante ➡️",
        "btn_download": "📥 Télécharger (SVG)",
        "clues_title": "Indices :",
        "clues_across": "Horizontal :",
        "clues_down": "Vertical :",
        "warning_unplaced": "⚠️ Certains mots n'ont pas pu s'intégrer! Augmentez la grille ou changez de disposition."
    }
}

EMPTY = "."

def create_grid(size):
    return [[EMPTY for _ in range(size)] for _ in range(size)]

def can_place_tokens(grid, tokens, row, col, direction, grid_size):
    # التأكد من عدم الخروج عن حدود الشبكة
    if direction == "H" and col + len(tokens) > grid_size: return False
    if direction == "V" and row + len(tokens) > grid_size: return False
    
    # فحص أطراف الكلمة (الرأس والذيل) لضمان عدم الالتصاق بكلمة أخرى
    if direction == "H":
        if col > 0 and grid[row][col-1] != EMPTY: return False
        if col + len(tokens) < grid_size and grid[row][col+len(tokens)] != EMPTY: return False
    if direction == "V":
        if row > 0 and grid[row-1][col] != EMPTY: return False
        if row + len(tokens) < grid_size and grid[row+len(tokens)][col] != EMPTY: return False

    for i in range(len(tokens)):
        r = row if direction == "H" else row + i
        c = col + i if direction == "H" else col
        
        # 1. إذا كان المربع مشغولاً بحرف مختلف (تصادم خاطئ)
        if grid[r][c] != EMPTY and grid[r][c] != tokens[i]: 
            return False
            
        # 2. قاعدة التباعد (Spacing Rule): التأكد من عدم ملامسة أعمدة موازية
        if grid[r][c] == EMPTY:
            if direction == "H":
                if r > 0 and grid[r-1][c] != EMPTY: return False
                if r < grid_size - 1 and grid[r+1][c] != EMPTY: return False
            if direction == "V":
                if c > 0 and grid[r][c-1] != EMPTY: return False
                if c < grid_size - 1 and grid[r][c+1] != EMPTY: return False
                
    return True

def place_tokens(grid, tokens, row, col, direction):
    for i in range(len(tokens)):
        r = row if direction == "H" else row + i
        c = col + i if direction == "H" else col
        grid[r][c] = tokens[i]

def generate_crossword(data_dict, mode_is_math, grid_size, seed):
    grid = create_grid(grid_size)
    processed_data = []
    
    for word, clue in data_dict.items():
        if mode_is_math:
            tokens = re.findall(r'\d+|[+\-*/=]', word) 
        else:
            tokens = list(word.upper().replace(" ", ""))
        if tokens:
            processed_data.append({'original': word, 'tokens': tokens, 'clue': clue})
            
    # ترتيب حسب الطول يعطي أفضل النتائج الهيكلية
    processed_data.sort(key=lambda x: len(x['tokens']), reverse=True)
    
    random.seed(seed) # تطبيق البذرة العشوائية لتوليد أشكال مختلفة
    placed_words = []
    unplaced_count = 0
    
    for item in processed_data:
        tokens = item['tokens']
        placed = False
        
        if not placed_words:
            row = grid_size // 2
            col = (grid_size - len(tokens)) // 2
            place_tokens(grid, tokens, row, col, "H")
            placed_words.append({'tokens': tokens, 'row': row, 'col': col, 'dir': "H", 'clue': item['clue']})
            continue

        possible_placements = []
        for p_word in placed_words:
            for i, p_token in enumerate(p_word['tokens']):
                for j, token in enumerate(tokens):
                    if p_token == token:
                        new_dir = "V" if p_word['dir'] == "H" else "H"
                        new_row = p_word['row'] - j if p_word['dir'] == "H" else p_word['row'] + i
                        new_col = p_word['col'] + i if p_word['dir'] == "H" else p_word['col'] - j
                            
                        if new_row >= 0 and new_col >= 0 and can_place_tokens(grid, tokens, new_row, new_col, new_dir, grid_size):
                            possible_placements.append((new_row, new_col, new_dir))
                            
        # إذا وجدنا أكثر من مكان متاح للتقاطع، نختار واحداً عشوائياً بناءً على (الشكل)
        if possible_placements:
            new_row, new_col, new_dir = random.choice(possible_placements)
            place_tokens(grid, tokens, new_row, new_col, new_dir)
            placed_words.append({'tokens': tokens, 'row': new_row, 'col': new_col, 'dir': new_dir, 'clue': item['clue']})
            placed = True
        else:
            unplaced_count += 1
                            
    # قص المساحات الفارغة من الأطراف (Auto-Crop) لتوسيط اللغز
    min_r, max_r, min_c, max_c = grid_size, 0, grid_size, 0
    is_empty = True
    for r in range(grid_size):
        for c in range(grid_size):
            if grid[r][c] != EMPTY:
                is_empty = False
                min_r = min(min_r, r)
                max_r = max(max_r, r)
                min_c = min(min_c, c)
                max_c = max(max_c, c)
                
    if not is_empty:
        # إضافة مربع واحد كحافة فارغة حول اللغز
        min_r = max(0, min_r - 1)
        max_r = min(grid_size - 1, max_r + 1)
        min_c = max(0, min_c - 1)
        max_c = min(grid_size - 1, max_c + 1)
        
        cropped_grid = []
        for r in range(min_r, max_r + 1):
            cropped_grid.append(grid[r][min_c:max_c + 1])
            
        # تحديث خرائط الأرقام
        number_map = {}
        current_number = 1
        final_clues = {"Across": [], "Down": []}
        
        for w in placed_words:
            # تعديل الإحداثيات بناءً على القص
            adj_row = w['row'] - min_r
            adj_col = w['col'] - min_c
            coord = (adj_row, adj_col)
            
            if coord in number_map:
                num = number_map[coord]
            else:
                number_map[coord] = current_number
                num = current_number
                current_number += 1
                
            section = "Across" if w['dir'] == "H" else "Down"
            final_clues[section].append(f"{num}. {w['clue']}")
            
        return cropped_grid, number_map, final_clues, unplaced_count
    
    return grid, {}, {"Across": [], "Down": []}, unplaced_count

def get_svg_string(grid, number_map, clues, t, cell_bg, cell_stroke, text_color, puzzle_title):
    cell_size = 40
    grid_rows = len(grid)
    grid_cols = len(grid[0]) if grid_rows > 0 else 0
    grid_width = grid_cols * cell_size
    
    # حساب المسافة العلوية إذا كان هناك عنوان
    y_offset = 70 if puzzle_title else 20
    total_height = (grid_rows * cell_size) + y_offset + 350 
    
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {grid_width} {total_height}" width="100%" height="100%">\n'
    svg += '  <rect width="100%" height="100%" fill="#ffffff"/>\n'
    
    # طباعة العنوان إذا وجد
    if puzzle_title:
        svg += f'  <text x="{grid_width/2}" y="40" font-family="Arial" font-size="28" font-weight="bold" text-anchor="middle" fill="{text_color}">{puzzle_title}</text>\n'
        
    for row in range(grid_rows):
        for col in range(grid_cols):
            token = grid[row][col]
            if token != EMPTY:
                x = col * cell_size
                y = (row * cell_size) + y_offset
                svg += f'  <rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" fill="{cell_bg}" stroke="{cell_stroke}" stroke-width="2"/>\n'
                
                if (row, col) in number_map:
                    num = number_map[(row, col)]
                    svg += f'  <text x="{x + 4}" y="{y + 12}" font-family="Arial" font-size="11" fill="{cell_stroke}" font-weight="bold">{num}</text>\n'
                
                font_size = 18 if len(token) == 1 else 13
                svg += f'  <text x="{x + cell_size/2}" y="{y + cell_size/2 + 4}" font-family="Arial" font-size="{font_size}" text-anchor="middle" dominant-baseline="middle" font-weight="bold" fill="{text_color}">{token}</text>\n'
                
    y_clues = (grid_rows * cell_size) + y_offset + 40
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
st.set_page_config(page_title="مولد الألغاز", page_icon="🧩", layout="wide")

# تهيئة المتغيرات في الجلسة للحفاظ على اللغز عند تغيير الأشكال
if "puzzle_data" not in st.session_state:
    st.session_state.puzzle_data = None
if "layout_seed" not in st.session_state:
    st.session_state.layout_seed = 1

selected_lang = st.sidebar.selectbox("🌐 UI Language / لغة الواجهة:", ["العربية 🇸🇦", "English 🇬🇧", "Français 🇫🇷"])
t = translations[selected_lang]

st.title(t["title"])
st.sidebar.header(t["settings"])

mode = st.sidebar.radio(t["mode_select"], (t["mode_lang"], t["mode_math"]))
grid_size = st.sidebar.slider(t["grid_size"], min_value=15, max_value=50, value=30, step=1)

st.sidebar.markdown("---")
st.sidebar.subheader(t["colors_header"])
cell_bg_color = st.sidebar.color_picker(t["color_bg"], "#FFFFFF")
cell_stroke_color = st.sidebar.color_picker(t["color_stroke"], "#333333")
text_color = st.sidebar.color_picker(t["color_text"], "#000000")

mode_is_math = (mode == t["mode_math"])

if mode_is_math:
    default_input = "50+30=80 = حاصل جمع خمسين وثلاثين\n12*12=144 = عملية ضرب\n100-25=75 = عملية طرح\n144/12=12 = عملية قسمة"
else:
    default_input = "APPLE = فاكهة حمراء\nBANANA = فاكهة صفراء\nORANGE = فاكهة برتقالية\nWATERMELON = بطيخ صيفي"

# قسم إدخال البيانات والعنوان
puzzle_title = st.text_input(t["title_label"], "")
user_input = st.text_area(t["input_label"], default_input, height=150)

if st.button(t["btn_generate"]):
    data_dict = {}
    for line in user_input.split('\n'):
        if "=" in line:
            parts = line.rsplit("=", 1)
            word = parts[0].strip()
            clue = parts[1].strip()
            if word and clue:
                data_dict[word] = clue
                
    if not data_dict:
        st.error(t["err_format"])
    else:
        st.session_state.puzzle_data = data_dict
        st.session_state.layout_seed = random.randint(1, 1000) # بذرة عشوائية جديدة

# منطقة المعاينة وتغيير الأشكال
if st.session_state.puzzle_data:
    grid, num_map, final_clues, unplaced = generate_crossword(
        st.session_state.puzzle_data, 
        mode_is_math, 
        grid_size, 
        st.session_state.layout_seed
    )
    
    st.markdown("---")
    st.subheader(t["preview_label"])
    
    if unplaced > 0:
        st.warning(t["warning_unplaced"])
        
    # أزرار التمرير بين الأشكال المختلفة
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button(t["btn_prev_layout"]):
            st.session_state.layout_seed -= 1
            st.rerun()
    with col3:
        if st.button(t["btn_next_layout"]):
            st.session_state.layout_seed += 1
            st.rerun()
            
    svg_output = get_svg_string(grid, num_map, final_clues, t, cell_bg_color, cell_stroke_color, text_color, puzzle_title)
    
    st.components.v1.html(svg_output, height=650, scrolling=True)
    
    st.download_button(
        label=t["btn_download"],
        data=svg_output,
        file_name="awesome_puzzle.svg",
        mime="image/svg+xml"
    )
