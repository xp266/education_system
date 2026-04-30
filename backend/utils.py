
"""
后端工具函数
"""
import re


def strip_markdown(text):
    """
    安全移除 Markdown 格式，返回纯文本，保留所有内容
    """
    if not text:
        return text

    formula_placeholders = {}
    placeholder_counter = 0

    # 保护 $$...$$ 块级公式
    def protect_block_math(match):
        nonlocal placeholder_counter
        key = f"@@MATH{placeholder_counter}@@"
        formula_placeholders[key] = match.group(0)
        placeholder_counter += 1
        return key
    text = re.sub(r'\$\$[\s\S]*?\$\$', protect_block_math, text)

    # 保护 \[...\] 块级公式
    def protect_latex_block(match):
        nonlocal placeholder_counter
        key = f"@@MATH{placeholder_counter}@@"
        formula_placeholders[key] = match.group(0)
        placeholder_counter += 1
        return key
    text = re.sub(r'\\\[.*?\\\]', protect_latex_block, text, flags=re.DOTALL)

    # 保护 $...$ 行内公式
    def protect_inline_math(match):
        nonlocal placeholder_counter
        key = f"@@MATH{placeholder_counter}@@"
        formula_placeholders[key] = match.group(0)
        placeholder_counter += 1
        return key
    text = re.sub(r'\$(?!\$)[^\$]+?\$(?!\$)', protect_inline_math, text)

    # 保护 \(...\) 行内公式
    def protect_latex_inline(match):
        nonlocal placeholder_counter
        key = f"@@MATH{placeholder_counter}@@"
        formula_placeholders[key] = match.group(0)
        placeholder_counter += 1
        return key
    text = re.sub(r'\\\(.*?\\\)', protect_latex_inline, text, flags=re.DOTALL)

    # 移除代码块 ```...``` 保留内容
    def replace_code_block(match):
        content = match.group(1)
        content = re.sub(r'^[a-zA-Z0-9_-]+\n', '', content)
        return content
    text = re.sub(r'```([\s\S]*?)```', replace_code_block, text)

    # 处理表格
    def process_table(text):
        lines = text.split('\n')
        result = []
        in_table = False
        for line in lines:
            pipe_count = 0
            for c in line:
                if c == '|':
                    pipe_count += 1
            if pipe_count >= 2:
                in_table = True
                line = line.strip()
                if line.startswith('|'):
                    line = line[1:]
                if line.endswith('|'):
                    line = line[:-1]
                is_separator = True
                for c in line:
                    if c not in '-:| ':
                        is_separator = False
                        break
                if not is_separator:
                    cells = []
                    for cell in line.split('|'):
                        cells.append(cell.strip())
                    result.append('  '.join(cells))
            else:
                if in_table and line.strip() == '':
                    continue
                result.append(line)
        return '\n'.join(result)
    text = process_table(text)

    # 移除粗体 **...** / __...__
    text = re.sub(r'(\*\*|__)(.*?)\1', r'\2', text)

    # 移除斜体 *...* / _..._
    text = re.sub(r'(?<!\\)(\*|_)(.*?)(?<!\\)\1', r'\2', text)

    # 移除行内代码 `...`
    text = re.sub(r'`([^`]+)`', r'\1', text)

    # 移除标题 #
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)

    # 移除引用 >
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)

    # 清理多余空行
    text = re.sub(r'\n\s*\n', '\n', text)
    text = re.sub(r'\n\s*\n', '\n', text)

    for key, formula in formula_placeholders.items():
        text = text.replace(key, formula)
    return text.strip()

