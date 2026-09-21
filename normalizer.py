import re

ONES = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]

def _read_two_digits(num_str: str) -> str:
    if len(num_str) == 1:
        return ONES[int(num_str)]
    t, o = int(num_str[0]), int(num_str[1])
    res = "mười" if t == 1 else ONES[t] + " mươi"
    if o == 0:
        return res
    elif o == 1:
        return res + " mốt" if t > 1 else res + " một"
    elif o == 4:
        return res + " tư" if t > 1 else res + " bốn"
    elif o == 5:
        return res + " lăm"
    else:
        return res + " " + ONES[o]

def _read_three_digits(num_str: str) -> str:
    num_str = num_str.zfill(3)
    h, t, o = int(num_str[0]), int(num_str[1]), int(num_str[2])
    res = ONES[h] + " trăm"
    if t == 0 and o == 0:
        return res
    if t == 0:
        return res + " linh " + ONES[o]
    return res + " " + _read_two_digits(num_str[1:])

def read_integer(n: int) -> str:
    if n == 0:
        return "không"
    if n < 0:
        return "âm " + read_integer(-n)
    
    units = ["", "nghìn", "triệu", "tỷ", "nghìn tỷ", "triệu tỷ"]
    s = str(n)
    groups = []
    while len(s) > 3:
        groups.append(s[-3:])
        s = s[:-3]
    groups.append(s)
    
    words = []
    for i, g in enumerate(groups):
        val = int(g)
        if val > 0:
            if i == len(groups) - 1:
                if len(g) == 1:
                    w = ONES[int(g)]
                elif len(g) == 2:
                    w = _read_two_digits(g)
                else:
                    w = _read_three_digits(g)
            else:
                w = _read_three_digits(g)
            unit = units[i]
            words.append((w + " " + unit).strip())
            
    return " ".join(reversed(words))

def read_decimal(num_str: str) -> str:
    parts = re.split(r'[.,]', num_str)
    a = read_integer(int(parts[0]))
    b = " ".join(ONES[int(ch)] for ch in parts[1])
    return f"{a} phẩy {b}"

def normalize_vietnamese_text(text: str) -> str:
    if not text:
        return ""

    # 1. Percentages (decimals or integers)
    def _percent_rep(m):
        val = m.group(1)
        if '.' in val or ',' in val:
            return f"{read_decimal(val)} phần trăm"
        return f"{read_integer(int(val))} phần trăm"
    text = re.sub(r'(\d+(?:[.,]\d+)?)\s*%', _percent_rep, text)

    # 2. Units with slash or symbols
    text = re.sub(r'(\d+)\s*km/h\b', lambda m: f"{read_integer(int(m.group(1)))} ki lô mét trên giờ", text, flags=re.IGNORECASE)
    text = re.sub(r'\bkm/h\b', "ki lô mét trên giờ", text, flags=re.IGNORECASE)
    text = re.sub(r'(\d+)\s*°C\b', lambda m: f"{read_integer(int(m.group(1)))} độ xê", text, flags=re.IGNORECASE)
    text = re.sub(r'°C', " độ xê", text)

    # 3. Currency symbols ($ / USD)
    text = re.sub(r'\$(\d+(?:[.,]\d+)?)', lambda m: f"{read_decimal(m.group(1)) if ('.' in m.group(1) or ',' in m.group(1)) else read_integer(int(m.group(1)))} đô la", text)
    text = re.sub(r'(\d+(?:[.,]\d+)?)\s*\$', lambda m: f"{read_decimal(m.group(1)) if ('.' in m.group(1) or ',' in m.group(1)) else read_integer(int(m.group(1)))} đô la", text)

    # 4. Specific Abbreviations & Words
    replacements = [
        (r"\bAI\b", "ây ai"),
        (r"\bA\.I\b", "ây ai"),
        (r"\bCEO\b", "xi i ô"),
        (r"\bTP\.?\s*HCM\b", "thành phố hồ chí minh"),
        (r"\bTP\.?\s*Hà Nội\b", "thành phố hà nội"),
        (r"\bUBND\b", "ủy ban nhân dân"),
        (r"\bCSGT\b", "cảnh sát giao thông"),
        (r"\bVTV\b", "vê tê vê"),
        (r"\bVOV\b", "vê o vê"),
        (r"\bFacebook\b", "phây buốc"),
        (r"\bFB\b", "phây buốc"),
        (r"\bYoutube\b", "du túp"),
        (r"\bGoogle\b", "gú gồ"),
        (r"\bChatGPT\b", "chát di pi ti"),
        (r"\bTTS\b", "ti ti ét"),
        (r"\bVbee\b", "vi bi"),
        (r"\bkm\b", "ki lô mét"),
        (r"\bkg\b", "ki lô gam"),
    ]
    for pattern, rep in replacements:
        text = re.sub(pattern, rep, text, flags=re.IGNORECASE)

    # 5. Dates: (ngày )DD/MM/YYYY
    def _date_rep(m):
        prefix = m.group(1) or ""
        d, mth, y = m.group(2), m.group(3), m.group(4)
        has_ngay = "ngày " if not prefix.strip().lower().startswith("ngày") else ""
        return f"{prefix}{has_ngay}{read_integer(int(d))} tháng {read_integer(int(mth))} năm {read_integer(int(y))}"
    text = re.sub(r'(\b(?:ngày\s+)?)(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b', _date_rep, text, flags=re.IGNORECASE)

    # 6. Time: HHhMM or HH:MM
    def _time_rep(m):
        h, mn = m.group(1), m.group(2)
        return f"{read_integer(int(h))} giờ {read_integer(int(mn))} phút"
    text = re.sub(r'\b(\d{1,2})[h:](\d{2})\b', _time_rep, text)

    # 7. Money shortcuts like 150k, 2.5tr
    text = re.sub(r'(\d+)\s*[kK]\b', lambda m: f"{read_integer(int(m.group(1)))} nghìn ", text)

    def _tr_rep(m):
        n = m.group(1)
        if '.' in n or ',' in n:
            return f"{read_decimal(n)} triệu "
        return f"{read_integer(int(n))} triệu "
    text = re.sub(r'(\d+(?:[.,]\d+)?)\s*tr\b', _tr_rep, text)

    # 8. Currency with dots e.g. 150.000đ or 1.500.000 đồng / vnđ
    def _currency_rep(m):
        raw = m.group(1).replace('.', '').replace(',', '')
        return f"{read_integer(int(raw))} đồng"
    text = re.sub(r'\b(\d{1,3}(?:[.,]\d{3})+)\s*(?:đ|đồng|vnđ|vnd)\b', _currency_rep, text, flags=re.IGNORECASE)

    # 9. Remaining decimals e.g. 3.14 or 3,14
    text = re.sub(r'\b(\d+[.,]\d+)\b', lambda m: read_decimal(m.group(1)), text)

    # 10. Remaining standalone integers
    text = re.sub(r'\b\d+\b', lambda m: read_integer(int(m.group(0))), text)

    # 11. Clean up extra punctuation & whitespace
    text = re.sub(r'[^\w\s.,?!;:\-–—\(\)áàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÉÈẺẼẸÊẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÚÙỦŨỤƯỨỪỬỮỰÝỲỶỸỴĐ]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text
