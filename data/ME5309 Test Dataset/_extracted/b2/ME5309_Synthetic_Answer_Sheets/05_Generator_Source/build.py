# -*- coding: utf-8 -*-
import os, re, random, sys
sys.path.insert(0, '/home/claude')
from content import VAR, MAX, GIVEN
from students import BATCH1

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

OUT = '/mnt/user-data/outputs/batch1'
PDFDIR = OUT + '/answer_sheets'
os.makedirs(PDFDIR, exist_ok=True)

FD = '/usr/share/fonts/truetype/dejavu/'
pdfmetrics.registerFont(TTFont('DJ', FD + 'DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DJ-B', FD + 'DejaVuSans-Bold.ttf'))
pdfmetrics.registerFont(TTFont('DJ-I', FD + 'DejaVuSans-Oblique.ttf'))
pdfmetrics.registerFont(TTFont('DJ-BI', FD + 'DejaVuSans-BoldOblique.ttf'))
addMapping('DJ', 0, 0, 'DJ'); addMapping('DJ', 1, 0, 'DJ-B')
addMapping('DJ', 0, 1, 'DJ-I'); addMapping('DJ', 1, 1, 'DJ-BI')

TYPOS = {
    'because': 'becuase', 'therefore': 'therefor', 'calculate': 'calcualte', 'frequency': 'frequncy',
    'resolution': 'resolutoin', 'approximately': 'aproximately', 'equilibrium': 'equilibrum',
    'equilibria': 'equilibira', 'assumptions': 'assumtions', 'derivative': 'derivitive',
    'noise': 'noice', 'amplified': 'amplifed', 'controller': 'controler', 'steady': 'stedy',
    'estimate': 'estimat', 'observer': 'obsever', 'quantisation': 'quantisaton', 'gravity': 'graviy',
    'stability': 'stabilty', 'measurement': 'measurment', 'sampling': 'sampeling', 'filter': 'fliter',
    'difference': 'diffrence', 'differentiation': 'diferentiation', 'characteristic': 'characterstic',
    'polynomial': 'polynomal', 'desired': 'desiered', 'substituting': 'substitutting',
    'torque': 'torqe', 'compensation': 'compensaton', 'saturates': 'saturtes', 'integrator': 'integrater',
    'remedy': 'remidy', 'stable': 'stabel', 'angle': 'angel', 'receive': 'recieve', 'which': 'wich',
    'since': 'sence', 'result': 'reuslt', 'matching': 'matchng', 'discretisation': 'discretisaton',
    'poles': 'pols', 'actuator': 'acuator', 'unity': 'unitiy', 'accumulating': 'acumulating',
    'check': 'chek', 'answer': 'anwser', 'conclusion': 'conclusoin',
}
WORD_RE = re.compile(r'\b(' + '|'.join(sorted(TYPOS, key=len, reverse=True)) + r')\b', re.I)


def add_typos(text, rate, rng):
    count = 0
    parts = re.split(r'(<[^>]+>)', text)
    for i, seg in enumerate(parts):
        if seg.startswith('<'):
            continue

        def rep(m):
            nonlocal count
            if rng.random() < rate:
                w = m.group(0)
                t = TYPOS[w.lower()]
                count += 1
                return t.capitalize() if w[0].isupper() else t
            return m.group(0)
        parts[i] = WORD_RE.sub(rep, seg)
    return ''.join(parts), count


def fix(text):
    text = text.replace('§tt', 'θ\u00a8').replace('§t', 'θ\u02d9').replace('§x', 'x\u02d9')
    # combining marks are not rendered by reportlab: use spacing equivalents after the base letter
    return text.replace('\u0307', '\u02d9').replace('\u0308', '\u00a8').replace('\u0302', '\u02c6')


def resolve(sel, style):
    return 'ok_' + style if sel == 'ok' else sel


def build_pdf(st, pdfdir=None):
    rng = random.Random(st['id'] + 'typo')
    fname = 'ME5309_Midsem_%s_%s.pdf' % (st['id'], st['name'].replace(' ', '_'))
    path = os.path.join(pdfdir or PDFDIR, fname)
    base = ParagraphStyle('b', fontName='DJ', fontSize=9.6, leading=14, spaceAfter=4)
    head = ParagraphStyle('h', fontName='DJ-B', fontSize=12.5, leading=16, spaceBefore=10, spaceAfter=6,
                          textColor=colors.HexColor('#1a237e'))
    title = ParagraphStyle('t', fontName='DJ-B', fontSize=14, leading=18, spaceAfter=4)
    small = ParagraphStyle('s', fontName='DJ', fontSize=9.6, leading=14)
    note = ParagraphStyle('n', parent=base, fontName='DJ-I')

    typos_total = 0
    story = [Paragraph('ME 5309 – Mid-Semester Examination: ANSWER SHEET', title),
             Paragraph('<b>Roll No.:</b> %s &nbsp;&nbsp;&nbsp;&nbsp; <b>Name:</b> %s' % (st['roll'], st['name']), small),
             Spacer(1, 3)]
    att = ', '.join(q for q in ['Q1', 'Q2', 'Q3', 'Q4'] if q in st['attempt'])
    line = '<b>Questions attempted:</b> %s' % att
    if st['struck']:
        line += ' &nbsp;(%s struck out – not to be considered)' % ', '.join(st['struck'])
    story += [Paragraph(line, small), HRFlowable(width='100%', thickness=0.8, color=colors.grey, spaceBefore=4, spaceAfter=2)]

    def P(text, style, struck=False):
        nonlocal typos_total
        text, c = add_typos(text, st['typo'], rng)
        typos_total += c
        text = fix(text)
        if struck:
            text = '<strike>%s</strike>' % text
        return Paragraph(text, style)

    for q in ['Q1', 'Q2', 'Q3', 'Q4']:
        if q not in st['attempt']:
            continue
        struck = q in st['struck']
        h = 'Question %s' % q[1]
        if struck:
            h += '   [CROSSED OUT BY STUDENT]'
        story.append(Paragraph(h, head))
        for t in st['pre'].get(q, []):
            story.append(P(t, note, struck))
        if st['style'] == 'V':
            story.append(P(GIVEN[q], note, struck))
        for p in 'abcd':
            key = q + p
            if key not in st['sel']:
                continue
            v = VAR[(q, p, resolve(st['sel'][key], st['style']))]
            first = True
            for t in v['t']:
                lab = '<b>(%s)</b>&nbsp;&nbsp;' % p if first else ''
                first = False
                story.append(P(lab + t, base, struck))
        for t in st['post'].get(q, []):
            story.append(P(t, note, struck))
        story.append(Spacer(1, 6))

    def footer(c, d):
        c.saveState()
        c.setFont('DJ', 8)
        c.setFillColor(colors.grey)
        c.drawString(18 * mm, 10 * mm, '%s – %s' % (st['roll'], st['name']))
        c.drawRightString(A4[0] - 18 * mm, 10 * mm, 'Page %d' % d.page)
        c.restoreState()

    doc = SimpleDocTemplate(path, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                            topMargin=16 * mm, bottomMargin=18 * mm,
                            title='ME 5309 Midsem answer sheet – %s' % st['name'], author=st['name'])
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return fname, typos_total


def marks_for(st):
    """returns dict key->marks (0 if unattempted) and rows for error log"""
    pm = {}
    log = []
    for q in ['Q1', 'Q2', 'Q3', 'Q4']:
        for p in 'abcd':
            if (q, p) not in MAX:
                continue
            key = q + p
            if q in st['attempt'] and key in st['sel']:
                k = resolve(st['sel'][key], st['style'])
                v = VAR[(q, p, k)]
                pm[key] = v['m']
                if not k.startswith('ok_T') and not k.startswith('ok_V'):
                    rtype = 'Alternative method' if v['ty'] == 'Valid alternative' else 'Error'
                    log.append((q, p, k, rtype, v['ty'], v['e'], key))
            else:
                pm[key] = 0
    return pm, log


if __name__ == '__main__':
    results = []
    for st in BATCH1:
        fname, nt = build_pdf(st)
        pm, log = marks_for(st)
        st['_pm'], st['_log'], st['_pdf'], st['_typos'] = pm, log, fname, nt
        qs = {q: sum(pm.get(q + p, 0) for p in 'abcd') for q in ['Q1', 'Q2', 'Q3', 'Q4']}
        counted = {q: (0 if q in st['struck'] else qs[q]) for q in qs}
        best3 = sum(sorted(counted.values(), reverse=True)[:3])
        print(st['id'], st['name'], qs, 'best3=', best3, 'typos=', nt)
    import pickle
    pickle.dump(BATCH1, open('/home/claude/batch1.pkl', 'wb'))
