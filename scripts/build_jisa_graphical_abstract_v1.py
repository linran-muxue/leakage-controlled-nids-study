from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

root = Path(__file__).resolve().parents[1]
out_dir = root / 'results_paper_materials_v3'
out_dir.mkdir(parents=True, exist_ok=True)

fig, ax = plt.subplots(figsize=(13.28, 5.31), dpi=130)
ax.set_xlim(0, 13.28)
ax.set_ylim(0, 5.31)
ax.axis('off')
fig.patch.set_facecolor('white')

title = 'Leakage-controlled and coverage-aware intrusion-detection evaluation'
ax.text(6.64, 4.85, title, ha='center', va='center', fontsize=18, fontweight='bold', color='#17324d')
ax.text(6.64, 4.42, 'CIC-IDS2017 primary study  |  NSL-KDD and UNSW-NB15 independent benchmarks',
        ha='center', va='center', fontsize=10.5, color='#4c5b66')

boxes = [
    (0.35, 2.35, 2.15, 1.25, '#e8f1fb', '1  Audit', 'source files\ninvalid values\nduplicates/conflicts'),
    (2.85, 2.35, 2.15, 1.25, '#edf7ed', '2  Lock protocol', 'train-only fitting\n60 χ² features\n100 trees, leaf=2'),
    (5.35, 2.35, 2.15, 1.25, '#fff4df', '3  Compare', 'full RF\nχ² RF\nweighted vs equal voting'),
    (7.85, 2.35, 2.15, 1.25, '#f5eafb', '4  Stress test', 'repeated splits\nprobability quality\nopen-set/latency'),
    (10.35, 2.35, 2.55, 1.25, '#e9f5f6', '5  Bound claims', '95.78% accuracy\n95.79% macro-F1\nno weighting gain'),
]
for x, y, w, h, color, head, body in boxes:
    patch = FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.04,rounding_size=0.08',
                           linewidth=1.2, edgecolor='#6d7d89', facecolor=color)
    ax.add_patch(patch)
    ax.text(x + 0.12, y + h - 0.28, head, ha='left', va='center', fontsize=11, fontweight='bold', color='#17324d')
    ax.text(x + 0.12, y + h - 0.62, body, ha='left', va='top', fontsize=8.8, color='#26343d', linespacing=1.25)

for i in range(len(boxes) - 1):
    x1 = boxes[i][0] + boxes[i][2] + 0.06
    x2 = boxes[i + 1][0] - 0.06
    y = boxes[i][1] + boxes[i][3] / 2
    ax.add_patch(FancyArrowPatch((x1, y), (x2, y), arrowstyle='-|>', mutation_scale=14,
                                 linewidth=1.4, color='#587080'))

ax.text(6.64, 1.45, 'Evidence hierarchy', ha='center', va='center', fontsize=11, fontweight='bold', color='#17324d')
ax.text(6.64, 1.08,
        'controlled CIC subset  →  repeated-split uncertainty  →  nested selection control  →  independent datasets',
        ha='center', va='center', fontsize=9.3, color='#4c5b66')
ax.text(6.64, 0.48,
        'Interpretation: feature reduction preserves performance; validation weighting is an applicability analysis, not a proven superiority claim.',
        ha='center', va='center', fontsize=8.7, color='#7b3f00')

fig.savefig(out_dir / 'Graphical_Abstract_JISA.png', dpi=130, bbox_inches='tight', pad_inches=0.05)
fig.savefig(out_dir / 'Graphical_Abstract_JISA.pdf', bbox_inches='tight', pad_inches=0.05)
plt.close(fig)
print(f'GRAPHICAL_ABSTRACT={out_dir / "Graphical_Abstract_JISA.png"}')
print(f'GRAPHICAL_ABSTRACT_PDF={out_dir / "Graphical_Abstract_JISA.pdf"}')
