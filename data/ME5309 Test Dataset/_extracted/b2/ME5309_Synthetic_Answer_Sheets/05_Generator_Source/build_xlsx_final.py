# -*- coding: utf-8 -*-
import pickle, sys
sys.path.insert(0, '/home/claude')
from content import MAX
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as L

students = pickle.load(open('/home/claude/all60.pkl', 'rb'))
OUT = '/mnt/user-data/outputs/ME5309_Synthetic_Answer_Sheets/03_Ground_Truth/ME5309_Midsem_GroundTruth_ALL60.xlsx'

F = 'Arial'
f_norm = Font(name=F, size=10)
f_bold = Font(name=F, size=10, bold=True)
f_head = Font(name=F, size=10, bold=True, color='FFFFFF')
f_in = Font(name=F, size=10, color='0000FF')       # hard-coded inputs (blue)
f_title = Font(name=F, size=13, bold=True)
fill_head = PatternFill('solid', start_color='1F3864')
fill_max = PatternFill('solid', start_color='D9E2F3')
fill_tot = PatternFill('solid', start_color='E2EFDA')
thin = Side(style='thin', color='BFBFBF')
border = Border(left=thin, right=thin, top=thin, bottom=thin)
wrap = Alignment(wrap_text=True, vertical='top')
center = Alignment(horizontal='center', vertical='top', wrap_text=True)

wb = Workbook()
ws = wb.active
ws.title = 'Summary'
pm = wb.create_sheet('Part_Marks')
el = wb.create_sheet('Error_Log')
rb = wb.create_sheet('Rubric_ModelAnswer')

FIRST = 5
n = len(students)
LAST = FIRST + n - 1
parts = [(q, p) for q in ['Q1', 'Q2', 'Q3', 'Q4'] for p in 'abcd' if (q, p) in MAX]


def hdr(sheet, row, headers):
    for i, h in enumerate(headers, 1):
        c = sheet.cell(row=row, column=i, value=h)
        c.font, c.fill, c.alignment, c.border = f_head, fill_head, center, border


# ------------------------------------------------------------- Part_Marks
pm['A1'] = 'Part-wise expected marks (ground truth) - ME 5309 Midsem, all 60 sheets'
pm['A1'].font = f_title
pm['A2'] = ('Marks are what a careful examiner following the Rubric_ModelAnswer sheet would award (half-mark steps, '
            'error-carried-forward credit where noted). 0 = not attempted. Blue = hard-coded input.')
pm['A2'].font = f_norm
hdr(pm, 3, ['Roll No.', 'Name'] + ['%s(%s)' % (q, p) for q, p in parts])
pm.cell(row=4, column=1, value='Max marks').font = f_bold
for j, (q, p) in enumerate(parts, 3):
    c = pm.cell(row=4, column=j, value=MAX[(q, p)])
    c.font, c.fill, c.alignment, c.border = f_bold, fill_max, center, border
pm.cell(row=4, column=1).fill = fill_max
pm.cell(row=4, column=2).fill = fill_max
for i, st in enumerate(students):
    r = FIRST + i
    pm.cell(row=r, column=1, value=st['roll']).font = f_norm
    pm.cell(row=r, column=2, value=st['name']).font = f_norm
    for j, (q, p) in enumerate(parts, 3):
        c = pm.cell(row=r, column=j, value=st['_pm'][q + p])
        c.font, c.alignment, c.border = f_in, center, border
        c.number_format = '0.0'
pm.column_dimensions['A'].width = 12
pm.column_dimensions['B'].width = 22
for j in range(3, 3 + len(parts)):
    pm.column_dimensions[L(j)].width = 8
pm.freeze_panes = 'C5'

# column ranges in Part_Marks for each question
qcols = {}
for j, (q, p) in enumerate(parts, 3):
    qcols.setdefault(q, []).append(j)

# ------------------------------------------------------------- Summary
ws['A1'] = 'ME 5309 Mid-Semester - synthetic answer sheets: ground-truth marks (all 60 sheets, batches 1-5)'
ws['A1'].font = f_title
ws['A2'] = ('Total = best three of the four question scores. A struck-out question counts as 0 even if it would have '
            'scored higher. Raw = marks for the work on the sheet; Counted = after applying strike-out.')
ws['A2'].font = f_norm
heads = ['Sr', 'Roll No.', 'Name', 'Archetype / what was done', 'Answer style', 'Attempted', 'Struck out',
         'Q1 raw', 'Q2 raw', 'Q3 raw', 'Q4 raw', 'Q1 counted', 'Q2 counted', 'Q3 counted', 'Q4 counted',
         'TOTAL /30 (best 3)', 'Errors injected (parts)', 'Spelling typos inserted', 'Pipeline test focus', 'PDF file', 'Batch']
hdr(ws, 3, heads)
ws.cell(row=4, column=1, value='Max').font = f_bold
for col in range(1, len(heads) + 1):
    ws.cell(row=4, column=col).fill = fill_max
for col in range(8, 16):
    c = ws.cell(row=4, column=col, value=10)
    c.font, c.alignment = f_bold, center
c = ws.cell(row=4, column=16, value=30)
c.font, c.alignment = f_bold, center
style_name = {'V': 'Verbose / long', 'T': 'Terse / concise'}
for i, st in enumerate(students):
    r = FIRST + i
    att = ', '.join(q for q in ['Q1', 'Q2', 'Q3', 'Q4'] if q in st['attempt'])
    sty = style_name[st['style']]
    if st['id'] == 'S09':
        sty = 'Mixed (long and short parts)'
    vals = [i + 1, st['roll'], st['name'], st['persona'], sty, att,
            ', '.join(st['struck']) if st['struck'] else 'None']
    for j, v in enumerate(vals, 1):
        cc = ws.cell(row=r, column=j, value=v)
        cc.font, cc.alignment, cc.border = f_norm, wrap, border
    # raw formulas from Part_Marks (same row index)
    for k, q in enumerate(['Q1', 'Q2', 'Q3', 'Q4']):
        a, b = qcols[q][0], qcols[q][-1]
        cc = ws.cell(row=r, column=8 + k, value='=SUM(Part_Marks!%s%d:%s%d)' % (L(a), r, L(b), r))
        cc.font, cc.alignment, cc.border, cc.number_format = f_norm, center, border, '0.0'
        raw = '%s%d' % (L(8 + k), r)
        cc = ws.cell(row=r, column=12 + k,
                     value='=IF(ISNUMBER(SEARCH("%s",$G%d)),0,%s)' % (q, r, raw))
        cc.font, cc.alignment, cc.border, cc.number_format = f_norm, center, border, '0.0'
    cc = ws.cell(row=r, column=16, value='=LARGE(L%d:O%d,1)+LARGE(L%d:O%d,2)+LARGE(L%d:O%d,3)' % (r, r, r, r, r, r))
    cc.font, cc.alignment, cc.border, cc.number_format, cc.fill = f_bold, center, border, '0.0', fill_tot
    cc = ws.cell(row=r, column=17, value='=COUNTIFS(Error_Log!$A:$A,$B%d,Error_Log!$F:$F,"Error")' % r)
    cc.font, cc.alignment, cc.border = f_norm, center, border
    cc = ws.cell(row=r, column=18, value=st['_typos'])
    cc.font, cc.alignment, cc.border = f_in, center, border
    for j, v in [(19, st['tests']), (20, '02_Answer_Sheets/%s' % st['_pdf']), (21, st['batch'])]:
        cc = ws.cell(row=r, column=j, value=v)
        cc.font, cc.alignment, cc.border = f_norm, wrap, border
# stats row
sr = LAST + 2
ws.cell(row=sr, column=3, value='Batch average (/30)').font = f_bold
cc = ws.cell(row=sr, column=16, value='=AVERAGE(P%d:P%d)' % (FIRST, LAST))
cc.font, cc.number_format, cc.alignment = f_bold, '0.00', center
ws.cell(row=sr + 1, column=3, value='Highest / lowest').font = f_bold
cc = ws.cell(row=sr + 1, column=16, value='=MAX(P%d:P%d)&" / "&MIN(P%d:P%d)' % (FIRST, LAST, FIRST, LAST))
cc.font, cc.alignment = f_bold, center
widths = [5, 12, 22, 46, 16, 14, 10, 8, 8, 8, 8, 9, 9, 9, 9, 12, 11, 11, 52, 48, 7]
for j, w in enumerate(widths, 1):
    ws.column_dimensions[L(j)].width = w
ws.freeze_panes = 'D5'
ws.row_dimensions[3].height = 42

# ------------------------------------------------------------- Error_Log
el['A1'] = 'Error log: what was deliberately done in each answer sheet and the marks it costs'
el['A1'].font = f_title
el['A2'] = ('Row type: Error = deliberate mistake or omission; Alternative method = valid but unusual approach (no loss expected); '
            'Not attempted / Struck out = question-level rows. Marks awarded link to Part_Marks.')
el['A2'].font = f_norm
hdr(el, 3, ['Roll No.', 'Name', 'Question', 'Part', 'Variant id', 'Row type', 'Category', 'What the student did',
            'Marks awarded', 'Max', 'Marks lost', 'Counted in total?'])
row = 4
col_of = {q + p: j for j, (q, p) in enumerate(parts, 3)}
for i, st in enumerate(students):
    prow = FIRST + i
    for (q, p, k, rtype, cat, desc, key) in st['_log']:
        counted = 'No (struck out)' if q in st['struck'] else 'Yes'
        vals = [st['roll'], st['name'], q, p, k, rtype, cat, desc,
                '=Part_Marks!%s%d' % (L(col_of[key]), prow), MAX[(q, p)], None, counted]
        for j, v in enumerate(vals, 1):
            cc = el.cell(row=row, column=j, value=v)
            cc.font, cc.alignment, cc.border = f_norm, wrap, border
        el.cell(row=row, column=11, value='=J%d-I%d' % (row, row)).font = f_norm
        el.cell(row=row, column=11).border = border
        for j in (9, 10, 11):
            el.cell(row=row, column=j).number_format = '0.0'
            el.cell(row=row, column=j).alignment = center
        row += 1
    for q in ['Q1', 'Q2', 'Q3', 'Q4']:
        if q not in st['attempt']:
            vals = [st['roll'], st['name'], q, 'All', 'n/a', 'Not attempted', 'Omission',
                    'Question left blank (0 marks; may be dropped from best-3 anyway)', 0, 10, None, 'n/a']
        elif q in st['struck']:
            a, b = qcols[q][0], qcols[q][-1]
            vals = [st['roll'], st['name'], q, 'All', 'n/a', 'Struck out', 'Strike-out',
                    'Student crossed the whole answer out; it must not be counted even though it was attempted',
                    '=SUM(Part_Marks!%s%d:%s%d)' % (L(a), prow, L(b), prow), 10, None, 'No (struck out)']
        else:
            continue
        for j, v in enumerate(vals, 1):
            cc = el.cell(row=row, column=j, value=v)
            cc.font, cc.alignment, cc.border = f_norm, wrap, border
        el.cell(row=row, column=11, value='=J%d-I%d' % (row, row)).font = f_norm
        el.cell(row=row, column=11).border = border
        for j in (9, 10, 11):
            el.cell(row=row, column=j).number_format = '0.0'
            el.cell(row=row, column=j).alignment = center
        row += 1
for j, w in enumerate([12, 22, 9, 6, 10, 18, 18, 80, 10, 7, 10, 16], 1):
    el.column_dimensions[L(j)].width = w
el.freeze_panes = 'A4'
el.auto_filter.ref = 'A3:L%d' % (row - 1)

# ------------------------------------------------------------- Rubric
rb['A1'] = 'Rubric and model answers used for the ground-truth marks'
rb['A1'].font = f_title
rb['A2'] = ('Derived from the paper (no rubric was supplied): part marks as printed, split into items. Rules: error-carried-forward '
            'credit when method is right; bare answers without formula/substitution earn 0 (paper instruction 5); '
            '-0.5 for missing units or fewer than 3 s.f. (instructions 6-7).')
rb['A2'].font = f_norm
hdr(rb, 3, ['Part', 'Max', 'Rubric items (marks)', 'Model answer'])
RUB = [
    ('Q1(a)', 4, 'f_x = f/p = 3200 px (1.5); FOV by similar triangles = 160 mm (1.5); mm per pixel = 0.125 (1.0)',
     'f_x = 16 mm / 5 um = 3200 px. Sensor width 6.4 mm; FOV = 6.4*400/16 = 160 mm; 160/1280 = 0.125 mm/px (= Z/f_x).'),
    ('Q1(b)', 3, 'LSB = 5/4096 = 1.22 mV (1.5); convert with 10 mV/N (1.0); units and assumption (0.5)',
     'LSB = 5/2^12 = 1.2207 mV; dF = 1.2207/10 = 0.122 N.'),
    ('Q1(c)', 3, 'Formulas F = e^(AT), G = A^-1 (F-I) B (1.0); F value (1.0); G value (1.0)',
     'F = e^-0.2 = 0.8187; G = (1 - e^-0.2)/2 = 0.0906; x[k+1] = 0.8187 x[k] + 0.0906 u[k].'),
    ('Q2(a)', 2, 'States and nonlinear model (1.0); equilibrium equation and |tau0| <= mgl (1.0)',
     'x1 = theta, x2 = theta-dot; x2-dot = (tau - b x2 - mgl sin x1)/J. Equilibrium: mgl sin(theta_e) = tau0, exists iff |tau0| <= mgl = 2.4525 N.m.'),
    ('Q2(b)', 2, 'A with numerical entries (1.5); B (0.5)',
     'A = [0 1; -(mgl/J)cos60 -b/J] = [0 1; -61.31 -2.5]; B = [0; 1/J] = [0; 50].'),
    ('Q2(c)', 4, 'Gravity must be balanced so no rest at theta_d (1.5); steady-state equation (1.0); numerical solution (1.5)',
     'Kp(theta_d - theta_ss) = mgl sin(theta_ss); 50(pi/2 - theta) = 2.4525 sin(theta) gives theta_ss = 87.19 deg, error = 2.81 deg (estimate mgl/Kp = 2.81 deg accepted).'),
    ('Q2(d)', 2, 'Error = 0 (1.0); poles unchanged with justification (1.0)',
     'theta_ss = theta_d. Linearised stiffness was Kp + mgl cos(theta_d); cos 90 = 0 so poles are unchanged (true only because theta_d = 90 deg).'),
    ('Q3(a)', 2, 'Two distinct valid reasons, 1.0 each',
     '(1) Differentiation amplifies (quantisation/measurement) noise; (2) encoder quantisation gives coarse velocity steps q/T; (also: delay/lag).'),
    ('Q3(b)', 2, 'Tustin coefficients with method (1.5); DC gain verified (0.5)',
     'wc = 125.66 rad/s, a = wc T/2 = 0.06283; y[k] = 0.05912 (u[k]+u[k-1]) + 0.88177 y[k-1]; H(1) = 2a/((1+a)-(1-a)) = 1.'),
    ('Q3(c)', 4, 'Characteristic polynomial (1.5); matching with s^2+20s+100 (1.0); L values (1.5)',
     's^2 + (2+l1)s + (2 l1 + l2) = (s+10)^2 gives l1 = 18, l2 = 64.'),
    ('Q3(d)', 2, 'Observer advantage (1.0); circumstance where filter is safer (1.0)',
     'Observer uses model and input: no phase lag, estimates unmeasured states/disturbances. Filter safer when model is uncertain or changing (payload, friction, contact, saturation).'),
    ('Q4(a)', 2, 'Closed-loop poles (1.0); N_ff (1.0)',
     's^2 + 4s + 8: poles -2 +/- 2j; DC gain N_ff/8 = 1 so N_ff = 8.'),
    ('Q4(b)', 2, 'theta_ss (1.0); percentage error (1.0)',
     'theta_ss = 0.75*8/(6 + 0.75*2) = 6/7.5 = 0.8; error 20% (not 25%).'),
    ('Q4(c)', 4, 'Characteristic polynomial (1.5); desired polynomial expansion (0.5); k1, k2 (1.0); K_I (1.0)',
     's^3 + (a+b k2)s^2 + (c+b k1)s + b K_I = s^3 + 8s^2 + 24s + 32 gives k2 = 6, k1 = 18, K_I = 32.'),
    ('Q4(d)', 2, 'Zero steady-state error argument (1.0); windup and anti-windup remedy (1.0)',
     'At steady state xi-dot = r - theta_ss = 0 independent of b, c. Failure mode: integrator windup with saturation; remedy: clamping / back-calculation anti-windup.'),
]
for i, (a, b, c_, d) in enumerate(RUB, 4):
    for j, v in enumerate([a, b, c_, d], 1):
        cc = rb.cell(row=i, column=j, value=v)
        cc.font, cc.alignment, cc.border = f_norm, wrap, border
tr = 4 + len(RUB)
rb.cell(row=tr, column=1, value='Total').font = f_bold
rb.cell(row=tr, column=2, value='=SUM(B4:B%d)' % (tr - 1)).font = f_bold
rb.cell(row=tr, column=3, value='60 marks across four questions; the best three (30 marks) count').font = f_norm
for j, w in enumerate([9, 6, 70, 90], 1):
    rb.column_dimensions[L(j)].width = w

wb.save(OUT)
print('saved', OUT)
