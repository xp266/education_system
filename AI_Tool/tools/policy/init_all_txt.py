
"""
按一定规则处理pdf，提取文本，用于向量检索的切块
"""

import os
import re
import pdfplumber
import sys

# 路径配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
PDF_PATH = os.path.abspath(os.path.join(BASE_DIR, "files/学生手册", "2025年本科学生手册.pdf"))
SAVE_TXT_PATH = os.path.join(BASE_DIR, "files/学生手册", "all.txt")
CUT_MARK = "#"  # 分割标记符号
CUT_MARK_NUM = 20  # 分割标记重复次数
SEPARATOR = CUT_MARK * CUT_MARK_NUM

def get_font_group(size):
    """按字体大小分组"""
    if size <= 6:
        return "标注文字"
    elif size <= 8:
        return "小文字"
    elif size <= 10:
        return "正文"
    elif size <= 12:
        return "特殊标题"
    elif size <= 18:
        return "标题"
    else:
        return "大文字"


def clean_special_chars(text):
    """清理 … 和超长 - .和页码"""
    text = text.replace("…", "").replace("┈", "")
    text = re.sub(r'-{6,}', '', text)
    text = re.sub(r'\.{6,}', '', text)
    text = re.sub(r'(?:\*\*\s*)?—\s*(\d[\d\s]*)\s*—(?:\s*\*\*)?', '', text)
    return text

def add_line_breaks(text):
    """智能换行规则"""
    # 1. 数字/中文数字 + 、或. 前面换行
    text = re.sub(r'(?<!\n)([一二三四五六七八九十\d]+[、.])', r'\n\1', text)
    # 2. (数字/中文数字) 前面换行
    text = re.sub(r'(?<!\n)\(([一二三四五六七八九十 ]+)\)', r'\n(\1)', text)
    # 3. 第中文数字章/节 前后都换行
    text = re.sub(r'(?<!\n)(第[一二三四五六七八九十]+[章节])', r'\n\1', text)
    text = re.sub(r'(第[一二三四五六七八九十]+[章节])(?!\n)', r'\1\n', text)
    return text

def remove_before_catalog(text):
    """去除目录之前的所有文字"""
    pattern = r'(目录|目\s*录|第一章|第一篇|第\s*[一二三四五六七八九十]+\s*章)'
    match = re.search(pattern, text)
    if match:
        text = text[match.start():]
    return text.strip()

def merge_short_blocks(text, separator=SEPARATOR):
    """连续短块合并，去掉分隔符，保留换行"""
    blocks = text.split(separator)
    blocks = [b.strip() for b in blocks if b.strip()]

    if not blocks:
        return ""

    merged = []
    temp_short = []

    for block in blocks:
        block_len = len(block.strip())

        if re.match(r'^【\d+-\d+】$', block.strip()):
            if temp_short:
                merged.append("\n".join(temp_short))
                temp_short = []
            merged.append(block)
            continue

        if block_len < 50:
            temp_short.append(f"**{block}**")
        else:
            if temp_short:
                merged.append(separator + "\n")
                merged.append("\n".join(temp_short) + "\n")
                temp_short = []
            merged.append(block)

    if temp_short:
        merged.append(separator + "\n")
        merged.append("\n".join(temp_short))

    return "\n".join(merged)


def move_table_name_to_end(text):
    """识别表格标题格式的行，将其移动到上一段末尾"""
    lines = text.splitlines()
    processed = []
    
    for line in lines:
        stripped = line.strip()
        if re.fullmatch(r'\s*\*\*.+表\*\*\s*', stripped):
            if processed:
                processed[-1] = processed[-1].rstrip() + " " + stripped
            continue
        processed.append(line)
    
    return "\n".join(processed)

def aggregate_page_range(total_text, sep=SEPARATOR):
    """页码追踪和聚合"""
    split_sep = f"\n{sep}\n"
    big_blocks = total_text.split(split_sep)
    res_blocks = []
    page_pattern = re.compile(r'【(\d+)-(\d+)】')

    for block in big_blocks:
        if not block.strip():
            continue
        page_nums = []
        matchs = page_pattern.findall(block)
        for s, e in matchs:
            page_nums.append(int(s))
            page_nums.append(int(e))
        new_block = page_pattern.sub('', block).strip()
        if page_nums:
            min_p = min(page_nums)
            max_p = max(page_nums)
            page_tag = f"【{min_p}-{max_p}】"
            final_block = f"{page_tag}\n{new_block}"
        else:
            final_block = new_block
        res_blocks.append(final_block)
    
    return f"\n{sep}\n".join(res_blocks)


def correct_page_numbers(total_text, sep=SEPARATOR):
    """正文页码矫正"""
    split_sep = f"\n{sep}\n"
    blocks = total_text.split(split_sep)
    if not blocks:
        return total_text

    page_pattern = re.compile(r'【(\d+)-(\d+)】')
    corrected_blocks = []
    base_offset = 0  # 偏移量

    for idx, block in enumerate(blocks):
        if not block.strip():
            continue
            
        match = page_pattern.search(block)
        if not match:
            corrected_blocks.append(block)
            continue

        # 提取当前块原始页码
        start_p = int(match.group(1))
        end_p = int(match.group(2))

        # 第一个块：计算偏移量，不修改页码
        if idx == 0:
            base_offset = end_p - 1
            corrected_blocks.append(block)
            continue

        # 非第一个块：校正页码
        new_start = start_p - base_offset
        new_end = end_p - base_offset
        new_tag = f"【{new_start}-{new_end}】"
        # 替换页码
        new_block = page_pattern.sub(new_tag, block)
        corrected_blocks.append(new_block)

    return f"\n{sep}\n".join(corrected_blocks)




def format_text_rules(text):
    """
    渲染正常版：解决所有Markdown格式问题 + 换行问题
    1. 第x章/第x节：**第x章 描述**\n（描述去空格换行，末尾强制加换行）
    2. 第x条：**第x条：**（前面自动加换行，不重复加粗）
    3. 三种列表项自动加 "- "，排除特殊情况
    """
    num_pattern = r"[一二三四五六七八九十百]+"
    chapter_pattern = fr"第{num_pattern}章"
    section_pattern = fr"第{num_pattern}节"
    article_pattern = fr"第{num_pattern}条"

    # --------------------
    # 1. 处理章：末尾强制加换行，避免和后面内容挤在一起
    # --------------------
    text = re.sub(
        fr"({chapter_pattern})(.*?)(?={section_pattern}|{article_pattern}|{chapter_pattern}|$)",
        lambda m: f"**{m.group(1)} {re.sub(r'\s+', '', m.group(2))}**\n",
        text,
        flags=re.DOTALL
    )

    # --------------------
    # 2. 处理节：同样末尾强制加换行
    # --------------------
    text = re.sub(
        fr"({section_pattern})(.*?)(?={article_pattern}|{section_pattern}|{chapter_pattern}|$)",
        lambda m: f"**{m.group(1)} {re.sub(r'\s+', '', m.group(2))}**\n",
        text,
        flags=re.DOTALL
    )

    # --------------------
    # 3. 处理条：解决前面识别不到换行的问题
    # --------------------
    # 先统一处理所有空白换行，避免空格/制表符干扰
    text = re.sub(r"[ \t]+", " ", text)  # 把所有空格/制表符换成单个空格
    text = re.sub(r"\n+", "\n", text)    # 把连续换行合并成单个

    # 情况A：条前面没有换行 → 加换行 + 加粗+冒号
    text = re.sub(
        fr"(?<!\n)({article_pattern})",
        r"\n**\1：** ",
        text
    )
    # 情况B：条前面已有换行 → 只加粗+冒号
    text = re.sub(
        fr"(?<=\n)({article_pattern})",
        r"**\1：** ",
        text
    )

    # --------------------
    # 4. 处理列表项：去掉限制，处理所有行
    # --------------------
    lines = text.split('\n')
    processed_lines = []
    
    cn_num = r'[一二三四五六七八九十百]+'
    num = r'\d+'
    
    # 修复：去掉[:max(20, len(lines))]，处理所有行
    for line in lines:
        stripped = line.strip()
        add_prefix = True
        
        # 排除特殊情况
        if re.search(rf'\({cn_num}\)\s*[-至到]', stripped):
            add_prefix = False
        if re.search(rf'第{cn_num}、{cn_num}', stripped):
            add_prefix = False
        if re.search(rf'{num}\.{num}', stripped):
            add_prefix = False
        
        # 匹配三种列表规则
        if add_prefix:
            pattern = (
                rf'^(\({cn_num}\)|\({num}\))|'
                rf'^({cn_num}、)|'
                rf'^({num}\.)'
            )
            if re.match(pattern, stripped):
                line = f"- {line}"
        
        processed_lines.append(line)
    
    text = '\n'.join(processed_lines)
    
    return text



def extract_pdf_by_font_group(pdf_path, save_path):
    segments = []
    current_segment_text = []
    current_start_page = None
    last_group = None

    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        for page_idx, page in enumerate(pdf.pages, start=1):
            chars = page.chars
            if not chars:
                continue

            for char in chars:
                text = char["text"].strip()
                size = round(char["size"], 2)

                if not text:
                    continue

                current_group = get_font_group(size)
                if current_group == "标注文字":
                    if current_segment_text:
                        current_segment_text.append(text)
                    continue

                if last_group is not None and current_group != last_group:
                    if current_segment_text:
                        seg_text = "".join(current_segment_text)
                        segments.append({
                            "text": seg_text,
                            "start": current_start_page,
                            "end": page_idx
                        })
                        current_segment_text = []

                if not current_segment_text:
                    current_start_page = page_idx
                current_segment_text.append(text)
                last_group = current_group

        if current_segment_text:
            seg_text = "".join(current_segment_text)
            segments.append({
                "text": seg_text,
                "start": current_start_page,
                "end": total_pages
            })

    # 拼接带页码文本
    final_parts = []
    for i, seg in enumerate(segments):
        txt = seg["text"]
        s = seg["start"]
        e = seg["end"]
        page_tag = f"【{s}-{e}】"
        if i == 0:
            final_parts.append(f"{page_tag}\n{txt}")
        else:
            final_parts.append(f"\n{SEPARATOR}\n{page_tag}\n{txt}")

    final_text = "".join(final_parts)

    # 清洗排版流程
    final_text = clean_special_chars(final_text)
    final_text = add_line_breaks(final_text)
    final_text = remove_before_catalog(final_text)
    final_text = merge_short_blocks(final_text)
    final_text = move_table_name_to_end(final_text)
    final_text = aggregate_page_range(final_text)

    final_text = correct_page_numbers(final_text)

    # 处理换行问题
    final_text = re.sub(r'\*\*\n', '**', final_text)

    # 应用格式规则
    final_text = format_text_rules(final_text)


    # 写入文件
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(final_text.strip())

    print("文本处理完成")

if __name__ == "__main__":
    extract_pdf_by_font_group(PDF_PATH, SAVE_TXT_PATH)