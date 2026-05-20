import streamlit as st

# --- الخوارزمية الأساسية (نفسها التي استخدمناها سابقاً) ---
GRID_SIZE = 20
EMPTY = "."

def create_grid(size):
    return [[EMPTY for _ in range(size)] for _ in range(size)]

def can_place_word(grid, word, row, col, direction):
    if direction == "H" and col + len(word) > GRID_SIZE: return False
    if direction == "V" and row + len(word) > GRID_SIZE: return False
    for i in range(len(word)):
        r = row if direction == "H" else row + i
        c = col + i if direction == "H" else col
        if grid[r][c] != EMPTY and grid[r][c] != word[i]: return False
    return True

def place_word(grid, word, row, col, direction):
    for i in range(len(word)):
        r = row if direction == "H" else row + i
        c = col + i if direction == "H" else col
        grid[r][c] = word[i]

def generate_crossword_with_clues(data_dict):
    grid = create_grid(GRID_SIZE)
    sorted_keys = sorted(data_dict.keys(), key=len, reverse=True)
    placed_words = []
    
    for word in sorted_keys:
        word_upper = word.upper()
        placed = False
        if not placed_words:
            place_word(grid, word_upper, GRID_SIZE//2, (GRID_SIZE-len(word_upper))//2, "H")
            placed_words.append({'word': word_upper, 'row': GRID_SIZE//2, 'col': (GRID_SIZE-len(word_upper))//2, 'dir': "H", 'clue': data_dict[word]})
            continue

        for p_word in placed_words:
            if placed: break
            for i, p_char in enumerate(p_word['word']):
                if placed: break
                for j, char in enumerate(word_upper):
                    if p_char == char:
                        new_dir = "V" if p_word['dir'] == "H" else "H"
                        new_row = p_word['row'] - j if p_word['dir'] == "H" else p_word['row'] + i
                        new_col = p_word['col'] + i if p_word['dir'] == "H" else p_word['col'] - j
                            
                        if new_row >= 0 and new_col >= 0 and can_place_word(grid, word_upper, new_row, new_col, new_dir):
                            place_word(grid, word_upper, new_row, new_col, new_dir)
                            placed_words.append({'word': word_upper, 'row': new_row, 'col': new_col, 'dir': new_dir, 'clue': data_dict[word]})
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

def get_svg_string(grid, number_map, clues):
    cell_size = 40
    grid_width = GRID_SIZE * cell_size
    total_height = (GRID_SIZE * cell_size) + 300 
    
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {grid_width} {total_height}" width="100%" height="100%">\n'
    svg += '  <rect width="100%" height="100%" fill="#ffffff"/>\n'
    
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            char = grid[row][col]
            if char != EMPTY:
                x = col * cell_size
                y = row * cell_size
                svg += f'  <rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" fill="white" stroke="#333" stroke-width="2"/>\n'
                if (row, col) in number_map:
                    num = number_map[(row, col)]
                    svg += f'  <text x="{x + 4}" y="{y + 12}" font-family="Arial" font-size="11" fill="#444" font-weight="bold">{num}</text>\n'
                svg += f'  <text x="{x + cell_size/2}" y="{y + cell_size/2 + 4}" font-family="Arial" font-size="18" text-anchor="middle" dominant-baseline="middle" font-weight="bold">{char}</text>\n'
                
    y_clues = (GRID_SIZE * cell_size) + 30
    svg += f'  <text x="20" y="{y_clues}" font-family="Arial" font-size="18" font-weight="bold">Clues:</text>\n'
    
    y_clues += 25
    svg += f'  <text x="20" y="{y_clues}" font-family="Arial" font-size="14" font-weight="bold">Across:</text>\n'
    for clue in clues["Across"]:
        y_clues += 20
        svg += f'  <text x="30" y="{y_clues}" font-family="Arial" font-size="12">{clue}</text>\n'
        
    y_clues += 30
    svg += f'  <text x="20" y="{y_clues}" font-family="Arial" font-size="14" font-weight="bold">Down:</text>\n'
    for clue in clues["Down"]:
        y_clues += 20
        svg += f'  <text x="30" y="{y_clues}" font-family="Arial" font-size="12">{clue}</text>\n'
        
    svg += '</svg>'
    return svg

# --- واجهة المستخدم (Web UI) ---
st.set_page_config(page_title="أداة صنع الألغاز", page_icon="🧩")
st.title("🧩 صانع الألغاز المتقاطعة الاحترافي")
st.write("أدخل الكلمات والأدلة في المربع أدناه، وسنقوم بتوليد شبكة الألغاز بصيغة SVG لتعديلها في برنامج التصميم الخاص بك.")

# مربع إدخال البيانات
default_input = "HTML = لغة هيكلة صفحات الويب\nREACT = مكتبة جافاسكريبت شهيرة\n144 = حاصل ضرب 12 في 12\nDESIGN = عملية التخطيط الهندسي"
user_input = st.text_area("أدخل الكلمات والأدلة (كل عنصر في سطر بصيغة: الكلمة = الدليل)", default_input, height=150)

if st.button("توليد اللغز 🚀"):
    # تحويل النص المدخل إلى قاموس بايثون
    data_dict = {}
    lines = user_input.split('\n')
    for line in lines:
        if "=" in line:
            parts = line.split("=")
            word = parts[0].strip().upper()
            clue = parts[1].strip()
            if word and clue:
                data_dict[word] = clue
                
    if not data_dict:
        st.error("الرجاء إدخال البيانات بالصيغة الصحيحة (الكلمة = الدليل)")
    else:
        # توليد اللغز
        grid, num_map, final_clues = generate_crossword_with_clues(data_dict)
        svg_output = get_svg_string(grid, num_map, final_clues)
        
        st.success("تم توليد اللغز بنجاح!")
        
        # عرض اللغز في الصفحة
        st.components.v1.html(svg_output, height=600, scrolling=True)
        
        # زر التحميل
        st.download_button(
            label="📥 تحميل اللغز (SVG)",
            data=svg_output,
            file_name="crossword_puzzle.svg",
            mime="image/svg+xml"
        )
