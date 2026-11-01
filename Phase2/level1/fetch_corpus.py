#!/usr/bin/env python3
"""Fetch bounded WikiText input snapshots; never redistribute source text in Git."""
from pathlib import Path
import argparse,hashlib,json,urllib.request
ROOT=Path(__file__).resolve().parents[1]
EXPECTED={
 'train':'88fa1a10cacc84b916b9d730259190ade358373a9797cfdb96049e17762529d6',
 'validation':'417e7b238525b0a167f16cf0668930317d2c1737579ca337859a7acf372e498d',
 'test':'cb700e96eb44e3c39a4dd0cfd811896a7eef67cbf8c1d2c4b5739a3449a34386'}
DATASET_CARD='https://huggingface.co/datasets/Salesforce/wikitext/blob/b08601e04326c79dfdd32d625aee71d232d685c3/README.md'
def source_url(split):
 return 'https://datasets-server.huggingface.co/rows?dataset=Salesforce%2Fwikitext&config=wikitext-2-raw-v1&split='+split+'&offset=0&length=100'
def load(directory,download=False):
 directory=Path(directory);directory.mkdir(parents=True,exist_ok=True);result={}
 for split,digest in EXPECTED.items():
  p=directory/f'wikitext_{split}.json'
  if not p.exists():
   if not download:raise FileNotFoundError('Missing corpus cache; run level1/fetch_corpus.py --download')
   with urllib.request.urlopen(source_url(split),timeout=60) as response:p.write_bytes(response.read())
  raw=json.loads(p.read_text());text=''.join(row['row']['text'] for row in raw['rows'])
  actual=hashlib.sha256(text.encode()).hexdigest()
  if actual!=digest:raise ValueError('WikiText content snapshot changed: '+split+' '+actual)
  result[split]={'text':text,'source_url':source_url(split),'text_sha256':actual,'source_rows':len(raw['rows']),
   'source_total_rows':raw['num_rows_total'],'dataset':'Salesforce/wikitext / wikitext-2-raw-v1',
   'dataset_card':DATASET_CARD,'license_note':'Upstream metadata names CC BY-SA 3.0; dataset card text links CC BY-SA 4.0. Source text is not redistributed here.',
   'snapshot_contract':'First100 API rows in published split; exact concatenated UTF-8 text checksum required. API URL is live, checksum prevents silent drift.'}
 return result
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--download',action='store_true');p.add_argument('--output',type=Path,default=ROOT/'build/data');a=p.parse_args()
 data=load(a.output,a.download)
 metadata={s:{k:v for k,v in d.items() if k!='text'} for s,d in data.items()}
 (a.output/'corpus_sources.json').write_text(json.dumps(metadata,indent=2)+'\n');print('Verified WikiText train/validation/test bounded snapshots')
if __name__=='__main__':main()
