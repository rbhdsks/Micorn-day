#!/usr/bin/env python3
"""Publication figures from retained RTL CSV, plus separately labelled CDM arithmetic."""
from pathlib import Path
import csv,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'level5/plots';OUT.mkdir(exist_ok=True)
COLORS={'none':'#66788A','next_line':'#ED875D','stride':'#168C91'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':15,'axes.titleweight':'bold','axes.labelsize':11,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'white','axes.facecolor':'white','savefig.facecolor':'white','axes.labelcolor':'#152B43','text.color':'#152B43','xtick.color':'#526174','ytick.color':'#526174','pdf.fonttype':42,'svg.fonttype':'none'})
with (ROOT/'level5/results/reference/summary.csv').open() as f:ROWS=list(csv.DictReader(f))
NAMES=sorted({r['workload'] for r in ROWS});GROUP={(r['workload'],r['policy']):r for r in ROWS}
LABELS={'column_stride':'Column stride','embedding_gather':'Irregular gather','interleaved_conflicting':'Conflicting streams','modelled_matmul_ijk_ab_reads':'Matmul ijk A/B','modelled_matmul_ikj_ab_reads':'Matmul ikj A/B','phase_shift':'Phase shift','pollution_return':'Hot-line pollution','same_line':'Same-line reuse','tensor_stream':'Dense words','three_line_bursts':'Three-line bursts','tiled_reuse':'Tile reuse','two_stream_disjoint_sets':'Disjoint streams','zero_gap_stream':'Zero compute gap'}
INDEX=[]
def save(fig,stem,caption,kind='measured RTL'):
    fig.tight_layout()
    for fmt in ['png','pdf','svg']:
        target=OUT/f'{stem}.{fmt}';fig.savefig(target,dpi=190,bbox_inches='tight')
        if fmt=='svg':target.write_text('\n'.join(line.rstrip() for line in target.read_text().splitlines())+'\n')
    plt.close(fig);INDEX.append({'file':stem,'caption':caption,'evidence':kind})

def horizontal(metric,stem,title,xlabel,policies=('next_line','stride'),baseline=None):
    fig,ax=plt.subplots(figsize=(10,6.2));y=np.arange(len(NAMES));h=.31
    for j,p in enumerate(policies):
        vals=[float(GROUP[n,p][metric]) for n in NAMES]
        ax.barh(y+(j-(len(policies)-1)/2)*h,vals,height=h*.9,color=COLORS[p],label=p.replace('_',' ').title())
    ax.set_yticks(y,[LABELS[n] for n in NAMES]);ax.invert_yaxis();ax.set_xlabel(xlabel);ax.set_title(title,loc='left',pad=18)
    if baseline is not None:ax.axvline(baseline,color='#233C52',lw=.8,ls='--')
    ax.grid(axis='x',alpha=.16);ax.set_axisbelow(True);ax.legend(frameon=False,loc='lower right');save(fig,stem,title+'; all 13 workloads, identical cache and timing.')

def main():
    horizontal('speedup','01_speedup','Completion speedup depends on access pattern','No-prefetch completion cycles / policy cycles',baseline=1)
    horizontal('demand_hit_rate','02_hit_rate','Demand hit rate is not execution speedup','Demand hits / accepted demand accesses',policies=('none','next_line','stride'))
    horizontal('mean_accept_to_response_cycles','03_latency','Response availability includes late-prefetch benefits','Mean cycles from accepted demand to response availability',policies=('none','next_line','stride'))
    # Traffic excludes the tiny-baseline pollution case from the shared scale and explains it separately.
    names=[n for n in NAMES if n!='pollution_return'];fig,ax=plt.subplots(figsize=(10,5.7));y=np.arange(len(names))
    for j,p in enumerate(['next_line','stride']):ax.barh(y+(j-.5)*.3,[float(GROUP[n,p]['dram_reads'])/float(GROUP[n,'none']['dram_reads']) for n in names],.27,color=COLORS[p],label=p.replace('_',' ').title())
    ax.set_yticks(y,[LABELS[n] for n in names]);ax.invert_yaxis();ax.axvline(1,color='#233C52',ls='--',lw=.8);ax.set_xlabel('Total DRAM transactions / no-prefetch transactions');ax.set_title('Speculation can increase memory traffic',loc='left',pad=18);ax.legend(frameon=False);save(fig,'04_traffic','Traffic ratio; pollution case shown separately to preserve the scale.')
    names=['column_stride','phase_shift','tensor_stream','three_line_bursts','zero_gap_stream','pollution_return'];fig,ax=plt.subplots(figsize=(10,4.7));left=np.zeros(len(names))
    for key,label,color in [('timely_useful','Timely','#168C91'),('late_useful','Late','#66788A'),('unused_evicted','Unused evicted','#ED875D'),('resident_unconsumed','Resident','#D7DCD9')]:
        v=np.array([int(GROUP[n,'stride'][key]) for n in names]);ax.barh(np.arange(len(names)),v,left=left,label=label,color=color);left+=v
    ax.set_yticks(np.arange(len(names)),[LABELS[n] for n in names]);ax.invert_yaxis();ax.set_xlabel('Issued stride-prefetch transactions');ax.set_title('Useful predictions may arrive late',loc='left',pad=18);ax.legend(frameon=False,ncol=4,loc='upper center',bbox_to_anchor=(.5,-.15));save(fig,'05_prefetch_fates','Stride-prefetch outcomes conserve after natural quiescence.')
    fig,axes=plt.subplots(1,2,figsize=(10,4));policies=['none','next_line','stride'];labels=['None','Next-line','Stride']
    for ax,metric,title in zip(axes,['completion_cycles','dram_reads'],['Completion cycles','Total DRAM transactions']):
        vals=[int(GROUP['pollution_return',p][metric]) for p in policies];bars=ax.bar(labels,vals,color=[COLORS[p] for p in policies],width=.55)
        ax.bar_label(bars,labels=[f'{x:,}' for x in vals],padding=5);ax.set_ylim(0,max(vals)*1.2);ax.set_title(title,loc='left');ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
    fig.suptitle('A wrong prefetch displaces a hot demand line',x=.01,ha='left',fontweight='bold',fontsize=15);save(fig,'06_pollution','320 demanded reads, four distinct demanded lines; all data correct despite the slowdown.')
    # Workload evidence at the actual 16-byte geometry.
    analysis={n:json.loads((ROOT/f'level5/results/reference/analysis/{n}.summary.json').read_text()) for n in NAMES}
    fig,ax=plt.subplots(figsize=(10,4.9));ax.barh(np.arange(len(NAMES)),[analysis[n]['unique_cache_lines'] for n in NAMES],color='#168C91');ax.set_yticks(np.arange(len(NAMES)),[LABELS[n] for n in NAMES]);ax.invert_yaxis();ax.axvline(64,color='#ED875D',ls='--',label='64 cache slots');ax.set_xlabel('Distinct touched 16-byte lines');ax.set_title('Trace footprint spans reuse and streaming regimes',loc='left',pad=16);ax.legend(frameon=False);save(fig,'07_workload_footprint','Unique touched lines are a footprint measure, not a cache-capacity requirement.')
    # Analytical CDM figures, explicitly independent from the RTL benchmark.
    data=json.loads((ROOT/'research/cdm/results/illustrative_choices.json').read_text());fig,ax=plt.subplots(figsize=(8.5,4))
    for r,color in zip(data,['#168C91','#233C52','#ED875D']):ax.plot(np.arange(1,7),r['chosen_probabilities'],'o-',label=f"Rank {r['rank']}",color=color)
    ax.set(xlabel='Observation in the supplied six-choice example',ylabel='Probability assigned to observed choice',ylim=(0,1),xticks=range(1,7));ax.set_title('CDM initial-factor arithmetic',loc='left',pad=18);ax.legend(frameon=False);save(fig,'08_cdm_probabilities','Supplied illustrative factors; not fitted models and not cache measurements.','recalculated notes illustration')
    ns=np.array([250,500,1000,2000,3000,5000]);fig,ax=plt.subplots(figsize=(8.5,4));ax.loglog(ns,8*ns**2/2**20,'o-',label='Full n²',color='#233C52')
    for r,color in zip([1,2,3],['#168C91','#ED875D','#8E88AD']):ax.loglog(ns,8*2*ns*r/2**20,'o-',label=f'Rank {r}: 2nr',color=color)
    ax.set(xlabel='Alternatives n',ylabel='Float64 parameter storage (MiB)');ax.set_title('Low-rank factors reduce parameter storage',loc='left',pad=18);ax.legend(frameon=False,ncol=2);ax.grid(which='major',alpha=.14);save(fig,'09_cdm_storage','Analytic tensor storage excludes optimizer, gradients, data and temporary matrices.','analytic storage')
    (OUT/'figure_index.json').write_text(json.dumps(INDEX,indent=2)+'\n')
    gallery='# Phase 1 figures\n\nEach figure is supplied as PNG, PDF and SVG. Figures 01-07 derive from retained RTL/trace evidence. Figures 08-09 separately reproduce CDM illustration arithmetic and analytic storage.\n\n'+''.join(f"## {x['caption']}\n\n![{x['caption']}]({x['file']}.png)\n\nEvidence: {x['evidence']}.\n\n" for x in INDEX)
    (OUT/'README.md').write_text(gallery.rstrip()+'\n')
    print('Generated',len(INDEX),'figure families in level5/plots')
if __name__=='__main__':main()
