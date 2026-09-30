#!/usr/bin/env python3
"""Celeste: a small, inspectable local-Gemma personal wiki harness."""
import argparse
import datetime as dt
import hashlib
import json
import re
import shutil
import sys
import time
import uuid
from pathlib import Path
from urllib.parse import quote
from local_model import LocalModel, ModelError
from retrieval import build_index, search, selected_sections

ROOT=Path(__file__).resolve().parent
ANSWER_SCHEMA={'type':'object','properties':{
 'status':{'type':'string','enum':['answered','insufficient_evidence']},
 'claims':{'type':'array','items':{'type':'object','properties':{
  'text':{'type':'string'},'evidence':{'type':'array','items':{'type':'object','properties':{'passage':{'type':'string'},'quote':{'type':'string'}},'required':['passage','quote'],'additionalProperties':False},'minItems':1}},'required':['text','evidence'],'additionalProperties':False}},
 'reason':{'type':'string'}},'required':['status','claims','reason'],'additionalProperties':False}
NOTE_SCHEMA={'type':'object','properties':{'summary':{'type':'string'},'details':{'type':'array','items':{'type':'string'},'minItems':3,'maxItems':7}},'required':['summary','details'],'additionalProperties':False}
TOPICS=[
 ('Tournament/Group A Campaign','S01','Group A standings',['Uruguay and France','Uruguay and South Africa','Uruguay and Mexico']),
 ('Matches/Uruguay and France','S01','Uruguay vs France',['Group A Campaign','Uruguay and South Africa']),
 ('Matches/Uruguay and South Africa','S01','South Africa vs Uruguay',['Group A Campaign','Uruguay and Mexico','Diego Forlan at the World Cup']),
 ('Matches/Uruguay and Mexico','S01','Mexico vs Uruguay',['Group A Campaign','Uruguay and South Korea']),
 ('Matches/Uruguay and South Korea','S02','Uruguay vs South Korea',['Uruguay and Mexico','Uruguay and Ghana']),
 ('Matches/Uruguay and Ghana','S02','Uruguay vs Ghana',['Uruguay and South Korea','Uruguay and Netherlands','Diego Forlan at the World Cup']),
 ('Matches/Uruguay and Netherlands','S02','Uruguay vs Netherlands',['Uruguay and Ghana','Uruguay and Germany']),
 ('Matches/Uruguay and Germany','S02','Match for third place',['Uruguay and Netherlands','Diego Forlan at the World Cup']),
 ('Team/Uruguay World Cup Squad','S03','Uruguay squad',['Group A Campaign','Costa Rica Playoff']),
 ('Qualification/South American Qualifying','S04','South American qualification',['Costa Rica Playoff']),
 ('Qualification/Costa Rica Playoff','S05','Costa Rica playoff',['South American Qualifying','Uruguay World Cup Squad','Group A Campaign']),
 ('Team/Diego Forlan at the World Cup','S06','Individual awards',['Uruguay and South Africa','Uruguay and Ghana','Uruguay and Germany']),
 ('Tournament/World Cup Group Draw','S07','World Cup group draw',['Group A Campaign','Costa Rica Playoff']),
]

def load_config():return json.loads((ROOT/'config.json').read_text())
def prompt(name):return (ROOT/'prompts'/(name+'.txt')).read_text()
def stamp():return dt.datetime.now(dt.timezone.utc).isoformat()
def normalized(text):return ' '.join(text.split())

def save_record(record):
    folder=ROOT/'evidence'/'runs';folder.mkdir(parents=True,exist_ok=True)
    rid=dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S')+'-'+record['interaction_mode']+'-'+uuid.uuid4().hex[:6]
    record.update(record_id=rid,created_at=stamp(),execution='local',network_disconnection='not verified by this record')
    record['source_catalog_sha256']=hashlib.sha256((ROOT/'research/sources.json').read_bytes()).hexdigest()
    record['configuration']=load_config()
    dest=folder/(rid+'.json');dest.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    # A readable card is saved alongside the complete machine-readable trace.
    lines=['# '+record['interaction_mode'].title()+' evidence card','',f"Created: {record['created_at']}",'','Execution: local. Network disconnection: not verified by this record.','']
    if record.get('question'):lines+=['## Question','',record['question'],'']
    if record.get('answer'):lines+=['## Actual displayed result','',record['answer'],'']
    if record.get('error'):lines+=['## Error','',record['error'],'']
    if record.get('model'):
        identity=record['model']['identity'];metrics=record['model']['measurements']
        lines+=['## Model and measurements','',f"Model: `{identity['model']}`. Digest: `{identity['digest']}`.",'',f"Runtime: {identity['runtime']}. Quantization: {identity['details'].get('quantization_level')}. Wall time: {metrics['wall_seconds']} seconds.",'',f"Sampled peak Ollama process RSS: {metrics['ollama_process_rss_peak_bytes']} bytes. This is process RSS, not total unified-memory consumption.",'']
    for i,p in enumerate(record.get('passages',[]),1):
        lines+=['## Retrieved passage P'+str(i),'',f"`{p['id']}` — `{p['path']}` — {p['section']} — characters {p['start']}–{p['end']}",'',p['text'],'']
    lines+=['## Assessment','',record.get('assessment','Pending human review. A valid source reference does not by itself prove that a claim follows from its source.'),'']
    dest.with_suffix('.md').write_text('\n'.join(lines))
    return str(dest.relative_to(ROOT))

def validate_answer(answer,passages):
    if not isinstance(answer,dict) or answer.get('status') not in ('answered','insufficient_evidence'):raise ValueError('Invalid answer status')
    if answer['status']=='insufficient_evidence':
        # Abstention takes precedence; never display incidental draft claims.
        # The unmodified model JSON remains in the evidence card.
        return 'Insufficient evidence. '+answer.get('reason','The sources do not answer this question.')
    if not answer.get('claims'):raise ValueError('Answered result contains no supported claims')
    rendered=[]
    for claim in answer['claims']:
        if not claim.get('text') or not claim.get('evidence'):raise ValueError('Uncited claim')
        citations=[]
        for item in claim['evidence']:
            match=re.fullmatch(r'P([1-9][0-9]*)',item.get('passage',''))
            if not match or int(match[1])>len(passages):raise ValueError('Citation points outside retrieved evidence')
            p=passages[int(match[1])-1];excerpt=normalized(item.get('quote',''))
            if len(excerpt)<5 or excerpt not in normalized(p['text']):raise ValueError('Evidence quote is absent from its cited original passage')
            citations.append('['+p['id']+']')
        rendered.append(claim['text']+' '+' '.join(dict.fromkeys(citations)))
    if answer.get('reason'):rendered.append(answer['reason'])
    return '\n\n'.join(rendered)

def ask(question,config,mode='ask'):
    passages=search(ROOT,question,config['retrieval_count'])
    record=dict(interaction_mode=mode,question=question,passages=passages)
    if not passages:
        record.update(answer='Insufficient evidence. No matching original passages were found.',assessment='No model call: retrieval found no evidence.')
    else:
        context='\n\n'.join(f"[P{i}] {p['section']} | {p['path']}\n{p['text']}" for i,p in enumerate(passages,1))
        # Explain tournament-stage wording without supplying an answer or opponent.
        interpreted=re.sub(r'after (?:the )?quarter[- ]finals', 'in the semi-final and in the subsequent final or third-place match',question,flags=re.I)
        record['interpreted_question']=interpreted
        user='QUESTION:\n'+interpreted+'\n\nORIGINAL PASSAGES:\n'+context
        record['prompt_messages']=[{'role':'system','content':prompt('research')},{'role':'user','content':user}]
        try:
            schema=json.loads(json.dumps(ANSWER_SCHEMA))
            schema['properties']['claims']['items']['properties']['evidence']['items']['properties']['passage']['enum']=['P'+str(i) for i in range(1,len(passages)+1)]
            raw,metadata=LocalModel(config).chat(record['prompt_messages'],schema)
            record.update(raw_model_output=raw,model=metadata)
            parsed=json.loads(raw)
            try:
                validate_answer(parsed,passages)
            except ValueError as validation_error:
                record['first_attempt']={'raw_model_output':raw,'model':metadata,'error':str(validation_error)}
                repair=record['prompt_messages']+[{'role':'assistant','content':raw},{'role':'user','content':'Validation failed: '+str(validation_error)+'. Return a corrected complete JSON answer. Each quote must be a single exact contiguous substring of its cited passage. Remove redundant evidence items rather than joining separated fragments. Keep all requested facts only when supported.'}]
                raw,metadata=LocalModel(config).chat(repair,schema)
                record.update(raw_model_output=raw,model=metadata,repair_prompt_messages=repair)
                parsed=json.loads(raw)
            record['parsed_answer']=parsed
            if parsed.get('status')=='insufficient_evidence' and parsed.get('claims'):record['suppressed_claims']=parsed['claims']
            record['answer']=validate_answer(parsed,passages)
            record['citation_check']=('Abstention: draft claims suppressed; no factual claims displayed.' if parsed['status']=='insufficient_evidence' else 'All displayed claim IDs and exact evidence quotes checked; semantic support requires review.')
        except (ModelError,ValueError,KeyError,TypeError) as exc:
            record.update(error=str(exc),answer='Unable to produce a verified answer: '+str(exc),assessment='Failed run; retained for inspection.')
            path=save_record(record)
            raise ModelError(record['answer']+'\nEvidence: '+path) from exc
    record['evidence_path']=save_record(record)
    return record

def needs_notes(message):
    lower=message.lower()
    if lower.startswith('/notes '):return True
    if any(x in lower for x in ['draft','brainstorm','study plan','make that','make it','shorter','what can','hello','hi there']):return False
    return bool(re.search(r'\b(uruguay|ghana|forlan|forlán|suarez|suárez|muslera|abreu|2010|group a|tabarez|tabárez)\b',lower) and re.search(r'\b(who|what|when|where|how|did|was|were|tell|explain|describe)\b',lower))

def chat_turn(message,history,config):
    if needs_notes(message):
        question=message.removeprefix('/notes ').strip()
        result=ask(question,config,mode='chat')
        answer=result['answer'];path=result['evidence_path']
    else:
        messages=[{'role':'system','content':prompt('persona')}]+history[-10:]+[{'role':'user','content':message}]
        raw,metadata=LocalModel(config).chat(messages,max_tokens=700)
        result=dict(interaction_mode='chat',question=message,answer=raw,passages=[],retrieval_used=False,model=metadata,prompt_messages=messages)
        path=save_record(result);answer=raw
    history.extend([{'role':'user','content':message},{'role':'assistant','content':answer}])
    return answer,path

def write_index():
    text='# Uruguay 2010 Wiki\n\nExplore Uruguay’s route from qualification to fourth place at the 2010 World Cup. Each note includes original-source references and related topics.\n\n'
    groups={}
    for relative,_,_,_ in TOPICS:
        path=ROOT/'vault/wiki'/(relative+'.md')
        if path.exists():groups.setdefault(relative.split('/')[0],[]).append(path.stem)
    descriptions={'Qualification':'The road to South Africa.','Tournament':'The draw and group-stage campaign.','Matches':'Follow all seven matches in order.','Team':'The squad and individual achievements.'}
    for group,names in groups.items():
        text+='## '+group+'\n\n'+descriptions[group]+'\n\n'+''.join('- [['+name+']]\n' for name in names)+'\n'
    (ROOT/'vault/index.md').write_text(text)

def ingest(config,index_only=False,source_id=None,force=False):
    start=time.perf_counter();counts=build_index(ROOT,config)
    if index_only:return dict(index=counts,generated=[],skipped=[],wall_seconds=round(time.perf_counter()-start,3))
    model=LocalModel(config);model.identity()
    sections={(s['source_id'],s['section']):s for s in selected_sections(ROOT)}
    manifest_path=ROOT/'.local/ingest_manifest.json'
    manifest=json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    generated=[];skipped=[]
    for relative,sid,title,related in TOPICS:
        if source_id and sid!=source_id:continue
        section=sections[sid,title]; name=relative.split('/')[-1]
        # Source boundaries may exceed the model budget. Make the truncation explicit.
        words=list(re.finditer(r'\S+',section['text']))
        end=words[min(len(words),1400)-1].end() if words else 0
        excerpt=section['text'][:end]
        fingerprint=hashlib.sha256((excerpt+prompt('ingest')+json.dumps(config,sort_keys=True)+relative+str(related)).encode()).hexdigest()
        dest=ROOT/'vault/wiki'/(relative+'.md')
        if not force and manifest.get(relative,{}).get('fingerprint')==fingerprint and dest.exists():skipped.append(name);continue
        messages=[{'role':'system','content':prompt('ingest')},{'role':'user','content':'TOPIC: '+name+'\nSOURCE SECTION: '+title+'\nORIGINAL TEXT:\n'+excerpt}]
        raw,metadata=model.chat(messages,NOTE_SCHEMA,max_tokens=750)
        obj=json.loads(raw)
        if not isinstance(obj.get('summary'),str) or not isinstance(obj.get('details'),list):raise ModelError('Invalid wiki note JSON')
        record=dict(interaction_mode='ingest',question='Summarize '+name,raw_model_output=raw,answer=obj['summary'],model=metadata,prompt_messages=messages,source_id=sid,source_path=section['path'],source_start=section['start'],source_end=section['start']+end,source_words_sent=len(excerpt.split()),source_truncated=end<len(section['text'].rstrip()))
        evidence=save_record(record)
        text='---\nsource_id: '+sid+'\nsource_section: '+json.dumps(title)+'\nmodel: '+config['model']+'\nreview_status: pending\n---\n\n# '+name+'\n\n'+obj['summary']+'\n\n## Details\n\n'+''.join('- '+str(s)+'\n' for s in obj['details'])
        source_file=Path(section['path']).name
        text+='\n## Sources\n\n- [Original local text](../../raw/'+quote(source_file)+') — '+title+'.\n- [Published source revision]('+section['source_url']+').\n\n## Related notes\n\n'
        for other in related:text+='- [['+other+']] — related campaign context.\n'
        if dest.exists():
            backup=ROOT/'.local/note_backups'/(dt.datetime.now().strftime('%Y%m%dT%H%M%S')+'-'+dest.name);backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dest,backup)
        dest.parent.mkdir(parents=True,exist_ok=True);tmp=dest.with_suffix('.tmp');tmp.write_text(text);tmp.replace(dest)
        manifest[relative]=dict(fingerprint=fingerprint,evidence=evidence,source_id=sid,generated_at=stamp())
        manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
        generated.append(name);print('Generated: '+name,flush=True)
    write_index()
    return dict(index=counts,generated=generated,skipped=skipped,wall_seconds=round(time.perf_counter()-start,3))

def main(argv=None):
    parser=argparse.ArgumentParser(description='Celeste: a local Gemma assistant and source-grounded Uruguay 2010 wiki. No cloud fallback.')
    sub=parser.add_subparsers(dest='command')
    sub.add_parser('help',help='Show available commands')
    p=sub.add_parser('ingest',help='Index original sources and generate linked wiki notes with local Gemma')
    p.add_argument('directory',nargs='?',default='vault/raw');p.add_argument('--index-only',action='store_true',help='Build search without calling Gemma');p.add_argument('--source',choices=['S01','S02','S03','S04','S05','S06','S07']);p.add_argument('--force',action='store_true',help='Regenerate notes, backing up existing versions')
    p=sub.add_parser('search',help='Show original passages and paths; does not call the model');p.add_argument('query');p.add_argument('--limit',type=int,default=6);p.add_argument('--json',action='store_true')
    p=sub.add_parser('ask',help='Answer a standalone factual question with checked source citations');p.add_argument('question');p.add_argument('--mode',choices=['local'],default='local');p.add_argument('--json',action='store_true')
    p=sub.add_parser('chat',help='Conversational assistant with recent context and optional source retrieval');p.add_argument('--message',help='Run one conversational turn')
    sub.add_parser('status',help='Show exact model, runtime and configuration')
    args=parser.parse_args(argv);config=load_config()
    try:
        if args.command in (None,'help'):parser.print_help();return 0
        if args.command=='status':print(json.dumps(LocalModel(config).identity(),ensure_ascii=False,indent=2))
        elif args.command=='ingest':
            if Path(args.directory).resolve()!=(ROOT/'vault/raw').resolve():raise ValueError('This project ingests its cataloged vault/raw directory only. Add new sources to the catalog explicitly.')
            result=ingest(config,args.index_only,args.source,args.force)
            result['evidence_path']=save_record(dict(interaction_mode='ingest-summary',answer=json.dumps(result,indent=2),result=result))
            print(json.dumps(result,indent=2))
        elif args.command=='search':
            if not 1<=args.limit<=20:raise ValueError('Search limit must be between 1 and 20')
            passages=search(ROOT,args.query,args.limit)
            path=save_record(dict(interaction_mode='search',question=args.query,passages=passages,answer='Returned '+str(len(passages))+' original passages; no model call.',model_called=False))
            if args.json:print(json.dumps(dict(passages=passages,evidence_path=path),ensure_ascii=False,indent=2))
            else:
                for p in passages:print('\n['+p['id']+'] '+p['path']+' — '+p['section']+'\n'+p['text'])
                print('\nEvidence: '+path)
        elif args.command=='ask':
            result=ask(args.question,config)
            if args.json:print(json.dumps(result,ensure_ascii=False,indent=2))
            else:
                print('Mode: ask | Execution: local | Model: '+config['model']+'\n\n'+result['answer'])
                for p in result['passages']:print('['+p['id']+'] '+p['path']+' — '+p['section'])
                print('\nEvidence: '+result['evidence_path'])
        elif args.command=='chat':
            history=[]
            print('Celeste | local '+config['model']+' | /notes /search /reset /save /quit')
            if args.message:
                answer,path=chat_turn(args.message,history,config);print(answer+'\nEvidence: '+path);return 0
            while True:
                try:message=input('\nYou: ').strip()
                except (EOFError,KeyboardInterrupt):print();break
                if message in ('/quit','/exit'):break
                if not message:continue
                if message=='/reset':history.clear();print('Conversation cleared.');continue
                if message=='/save':
                    path=save_record(dict(interaction_mode='chat-transcript',history=history,answer='Transcript saved outside the source corpus.'));print(path);continue
                if message.startswith('/search '):
                    for p in search(ROOT,message[8:],6):print('['+p['id']+'] '+p['path']+'\n'+p['text'])
                    continue
                answer,path=chat_turn(message,history,config);print('\nCeleste: '+answer+'\nEvidence: '+path)
        return 0
    except (ValueError,ModelError,OSError,KeyError,json.JSONDecodeError) as exc:
        print('Error: '+str(exc),file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
