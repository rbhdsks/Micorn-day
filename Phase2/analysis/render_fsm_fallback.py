#!/usr/bin/env python3
"""Render retained RTL samples when the Octave/gnuplot multi-axis exporter stalls."""
from pathlib import Path
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

root=Path(__file__).resolve().parents[1]
with (root/'analysis/data/fsm_wave.csv').open() as f:
    rows=[r for r in csv.DictReader(f) if 5<=int(r['cycle'])<=100]
x=[int(r['cycle']) for r in rows]
fig,axes=plt.subplots(3,1,figsize=(12,6.8),sharex=True,layout='constrained')
axes[0].step(x,[int(r['state']) for r in rows],where='post',color='#264d6b')
axes[0].set(yticks=[0,1,2],yticklabels=['IDLE','SEND','WAIT'],ylim=(-.25,2.25),title='Independent simulation: FSM and memory handshakes')
for ax,valid,ready,label in [(axes[1],'mem_valid','mem_ready','Memory request'),(axes[2],'mem_rsp_valid','mem_rsp_ready','Memory response')]:
    ax.step(x,[int(r[valid]) for r in rows],where='post',color='#00858c',label='valid')
    ax.step(x,[int(r[ready])+1.4 for r in rows],where='post',color='#e67c4c',label='ready (offset +1.4)')
    ax.set(yticks=[0,1,1.4,2.4],yticklabels=['valid 0','valid 1','ready 0','ready 1'],ylim=(-.2,2.65),ylabel=label)
for ax in axes:
    ax.grid(axis='x',color='#dde3e5',linewidth=.6)
    ax.spines[['top','right']].set_visible(False)
axes[-1].set(xlabel='Simulation cycle',xlim=(5,100))
for ext in ['png','pdf']:
    fig.savefig(root/'plots'/f'17_fsm_handshake_trace.{ext}',dpi=180)
plt.close(fig)
