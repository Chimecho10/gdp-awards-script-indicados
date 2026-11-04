from collections import Counter
from pathlib import Path
import re
import unicodedata

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.xmlchemy import OxmlElement
from pptx.util import Inches, Pt

BASE_DIR = Path(__file__).resolve().parent
FUNDOS = BASE_DIR / "fundos"
GOLD = RGBColor(247, 207, 131)
LIGHT = RGBColor(253, 232, 191)
WHITE = RGBColor(255, 248, 236)
FONT = "Cinzel"


def _text(slide, value, left, top, width, height, pt,
          color=GOLD, align=PP_ALIGN.CENTER, bold=False):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    frame = box.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.margin_left = frame.margin_right = Inches(0.08)
    frame.margin_top = frame.margin_bottom = Inches(0.02)
    frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    para = frame.paragraphs[0]
    para.alignment = align
    para.space_before = 0
    para.space_after = 0
    run = para.add_run()
    run.text = str(value)
    run.font.name = FONT
    run.font.size = Pt(pt)
    run.font.bold = bold
    run.font.color.rgb = color
    return box


def _background(prs, filename):
    path = FUNDOS / filename
    if not path.is_file():
        raise FileNotFoundError(f"Fundo do template não encontrado: {path}")
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.shapes.add_picture(str(path), 0, 0,
                             width=prs.slide_width, height=prs.slide_height)
    return slide


def _fade(slide):
    transition = OxmlElement("p:transition")
    transition.set("spd", "med")
    transition.set("advClick", "1")
    transition.append(OxmlElement("p:fade"))
    slide._element.cSld.addnext(transition)


def _clean_category(category):
    return re.sub(r"[\U0001F300-\U0001FAFF\ufe0f]", "", str(category)).strip()


def _names(candidates):
    results = []
    for candidate in candidates:
        if isinstance(candidate, (list, tuple)):
            value = candidate[0] if candidate else ""
        elif isinstance(candidate, dict):
            value = candidate.get("nome", candidate.get("name", ""))
        else:
            value = candidate
        if value is not None and str(value).strip():
            results.append(str(value).strip())
    return sorted(results, key=str.casefold)


def _is_duo(category):
    simplified = "".join(c for c in unicodedata.normalize("NFD", category.casefold())
                         if unicodedata.category(c) != "Mn")
    return "dupla" in simplified


def _member_indications(nominees):
    counts = Counter()
    for category, candidates in nominees.items():
        unique_members = set()
        for label in _names(candidates):
            if _is_duo(str(category)):
                members = [part.strip() for part in label.split(",")]
                if len(members) != 2 or not all(members):
                    members = [label]
            else:
                members = [label]
            unique_members.update(members)
        counts.update(unique_members)
    return sorted(counts.items(), key=lambda pair: (-pair[1], pair[0].casefold()))


def _category_title(slide, category, centered=False):
    label = _clean_category(category).upper()
    if centered:
        font = 67 if len(label) <= 22 else 53 if len(label) <= 30 else 43
        _text(slide, label, 1.35, 4.34, 17.3, 1.6, font)
    else:
        font = 49 if len(label) <= 23 else 39 if len(label) <= 33 else 32
        _text(slide, label, .84, .61, 18.0, 1.12, font,
              align=PP_ALIGN.LEFT)


def _stage_category(prs, category):
    slide = _background(prs, "categoria.png")
    _category_title(slide, category, centered=True)
    _fade(slide)


def _stage_count(prs, category, quantity):
    slide = _background(prs, "indicados.png")
    _category_title(slide, category)
    _text(slide, f"{quantity} {'INDICADO' if quantity == 1 else 'INDICADOS'}",
          3.1, 4.34, 13.8, 1.45, 81, color=GOLD)
    _fade(slide)


def _stage_reveal(prs, category, names, shown):
    slide = _background(prs, "indicados.png")
    _category_title(slide, category)
    _text(slide, "INDICADOS", .92, 1.96, 5.5, .62, 34,
          color=GOLD, align=PP_ALIGN.LEFT)
    total = len(names)
    if total <= 3:
        start_y, line_step = 3.08, 1.34
    elif total == 4:
        start_y, line_step = 2.88, 1.22
    else:
        start_y, line_step = 2.67, 1.09

    for index, name in enumerate(names[:shown]):
        length = len(name)
        size = 46 if length <= 17 else 39 if length <= 25 else 32
        _text(slide, name.upper(), 5.5, start_y + index * line_step,
              13.1, .92, size, color=LIGHT)

    _fade(slide)


def _stage_summary(prs, indications):
    slide = _background(prs, "indicados.png")
    _text(slide, "INDICAÇÕES POR MEMBRO", 1.25, .85, 16.0, .94, 59,
          align=PP_ALIGN.LEFT)
    _text(slide, "TOTAL DE CATEGORIAS EM QUE CADA UM FOI INDICADO",
          1.3, 1.88, 16.4, .52, 25, color=LIGHT, align=PP_ALIGN.LEFT)
    quantity = len(indications)
    ncols = 2 if quantity <= 18 else 3
    nrows = (quantity + ncols - 1) // ncols
    step = min(.66, 5.5 / max(nrows, 1))
    size = 37 if nrows <= 9 else 28
    colwidth = 17.2 / ncols
    for index, (member, count) in enumerate(indications):
        col = index // nrows
        row = index % nrows
        left = 1.3 + col * colwidth
        top = 3.1 + row * step
        _text(slide, f"{member.upper()}  —  {count}",
              left, top, colwidth - .32, step, size, color=WHITE,
              align=PP_ALIGN.LEFT)
    _fade(slide)


def generate_slides_nominees(nominees, path):
    if not isinstance(nominees, dict):
        raise TypeError("nominees deve ser um dicionário por categoria")
    if not nominees:
        raise ValueError("nominees está vazio")

    output = Path(path)
    if output.suffix.lower() != ".pptx":
        output = output / "GDP_Awards_Indicados.pptx"
    output.parent.mkdir(parents=True, exist_ok=True)

    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(20), Inches(11.25)

    cover = _background(prs, "capa.png")
    _text(cover, "GDP AWARDS 2026", 2.7, 3.93, 14.6, 1.35, 81)
    _text(cover, "INDICADOS", 5.0, 5.42, 10.0, 1.04, 68)
    _fade(cover)

    for category, candidates in nominees.items():
        names = _names(candidates)
        _stage_category(prs, category)
        _stage_count(prs, category, len(names))
        for shown in range(1, len(names) + 1):
            _stage_reveal(prs, category, names, shown)

    _stage_summary(prs, _member_indications(nominees))
    prs.save(output)
    print(f"Apresentação gerada: {output} ({len(prs.slides)} slides)")
    return output


if __name__ == "__main__":
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Gerar apresentação GDP Awards")
    parser.add_argument("json", help="Arquivo nominees.json")
    parser.add_argument("--saida", default=".", help="Pasta ou PPTX de saída")
    args = parser.parse_args()
    with open(args.json, encoding="utf-8") as file:
        nominees = json.load(file)
    generate_slides_nominees(nominees, args.saida)
