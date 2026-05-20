import streamlit as st
import re

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

def generate_crossword(data_dict, mode, grid_size):
    grid = create_grid(grid_size)
    processed_data = []
    
    for word, clue in data_dict.items():
        if mode == "math":
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

def get_svg_string(grid, number_map, clues, grid_size, bg_color, cell_color, line_color, text_color):
    cell_size = 40
    grid_width = grid_size * cell_size
    total_height = (grid_size * cell_size) + 350 
    
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {grid_width} {total_height}" width="100%" height="100%">\n'
    # لون الخلفية الكلية
    svg += f'  <rect width="100%" height="100%" fill="{bg_color}"/>\n'
    
    for row in range(grid_size):
        for col in range(grid_size):
            token = grid[row][col]
            if token != EMPTY:
                x = col * cell_size
                y = row * cell_size
                
                # رسم المربع مع الألوان المخصصة
                svg += f'  <rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" fill="{cell_color}" stroke="{line_color}" stroke-width="2"/>\n'
                
                # الأرقام الصغيرة
                if (row, col) in number_map:
                    num = number_map[(row, col)]
                    svg += f'  <text x="{x + 4}" y="{y + 12}" font-family="Arial" font-size="11" fill="{text_color}" font-weight="bold">{num}</text>\n'
                
                # النصوص والحلول
                font_size = 18 if len(token) == 1 else 13
                svg += f'  <text x="{x + cell_size/2}" y="{y + cell_size/2 + 4}" font-family="Arial" font-size="{font_size}" text-anchor="middle" dominant-baseline="middle" font-weight="bold" fill="{text_color}">{token}</text>\n'
                
    # نصوص الأدلة بالأسفل
    y_clues = (grid_size * cell_size) + 30
    svg += f'  <text x="20" y="{y_clues}" font-family="Arial" font-size="18" font-weight="bold" fill="{text_color}">Clues (الأدلة):</text>\n'
    
    y_clues += 25
    svg += f'  <text x="20" y="{y_clues}" font-family="Arial" font-size="14" font-weight="bold" fill="{text_color}">Across (أفقي):</text>\n'
    for clue in clues["Across"]:
        y_clues += 20
        svg += f'  <text x="30" y="{y_clues}" font-family="Arial" font-size="13" fill="{text_color}">{clue}</text>\n'
        
    y_clues += 30
    svg += f'  <text x="20" y="{y_clues}" font-family="Arial" font-size="14" font-weight="bold" fill="{text_color}">Down (عمودي):</text>\n'
    for clue in clues["Down"]:
        y_clues += 20
        svg += f'  <text x="30" y="{y_clues}" font-family="Arial" font-size="13" fill="{text_color}">{clue}</text>\n'
        
    svg += '</svg>'
    return svg

# ==========================================
# واجهة المستخدم (Web UI)
# ==========================================
st.set_page_config(page_title="مولّد الألغاز الاحترافي", page_icon="🧩", layout="wide")
st.title("🧩 مولّد الألغاز المتقاطعة (لغات ورياضيات)")

# 1. إعدادات الشبكة والصعوبة
st.sidebar.header("⚙️ إعدادات اللغز")
mode = st.sidebar.radio("اختر نوع اللغز:", ("لغات (أحرف)", "رياضيات (أرقام وعمليات)"))
grid_size = st.sidebar.slider("حجم الشبكة (درجة الصعوبة):", min_value=10, max_value=40, value=20, step=1)

# 2. إعدادات الألوان للطباعة (الجديدة)
st.sidebar.markdown("---")
st.sidebar.header("🎨 إعدادات الألوان للطباعة")
bg_color = st.sidebar.color_picker("لون الخلفية الكلية", "#FFFFFF")
cell_color = st.sidebar.color_picker("لون تعبئة المربعات", "#F5F5F5") # افتراضي رمادي فاتح جداً
line_color = st.sidebar.color_picker("لون خطوط الشبكة", "#000000")
text_color = st.sidebar.color_picker("لون النصوص والأرقام", "#000000")

st.write(f"**الوضع الحالي:** {mode} | **حجم الشبكة:** {grid_size}x{grid_size}")

if mode == "لغات (أحرف)":
    default_input = "APPLE = فاكهة حمراء\nBANANA = فاكهة صفراء\nORANGE = فاكهة برتقالية\nWATERMELON = بطيخ صيفي"
    mode_val = "lang"
else:
    default_input = "50+30=80 = حاصل جمع خمسين وثلاثين\n12*12=144 = عملية ضرب\n100-25=75 = عملية طرح\n144/12=12 = عملية قسمة"
    mode_val = "math"

user_input = st.text_area("أدخل البيانات (الصيغة: الكلمة/المعادلة = الدليل/السؤال)", default_input, height=150)

if st.button("توليد اللغز 🚀"):
    data_dict = {}
    for line in user_input.split('\n'):
        if "=" in line:
            parts = line.split("=")
            word = parts[0].strip()
            clue = parts[1].strip()
            if word and clue:
                data_dict[word] = clue
                
    if not data_dict:
        st.error("الرجاء إدخال البيانات بالصيغة الصحيحة.")
    else:
        grid, num_map, final_clues = generate_crossword(data_dict, mode_val, grid_size)
        
        # تمرير الألوان إلى الدالة
        svg_output = get_svg_string(grid, num_map, final_clues, grid_size, bg_color, cell_color, line_color, text_color)
        
        st.success("تم توليد اللغز وتلوينه بنجاح!")
        st.components.v1.html(svg_output, height=800, scrolling=True)
        
        st.download_button(
            label="📥 تحميل اللغز كملف (SVG) جاهز للطباعة",
            data=svg_output,
            file_name="styled_puzzle.svg",
            mime="image/svg+xml"
        )
