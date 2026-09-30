'use strict';
const $ = (selector, parent = document) => parent.querySelector(selector);
const $$ = (selector, parent = document) => [...parent.querySelectorAll(selector)];
const state = {data: null, match: 4, category: 'All', mode: 'ask', history: [], busy: false, view: 'overview'};
const codes = {'France':'FR','South Africa':'ZA','Mexico':'MX','South Korea':'KR','Ghana':'GH','Netherlands':'NL','Germany':'DE'};
const descriptions = {
  ask: 'Independent factual answers from original sources. Chat history is never used.',
  chat: 'Draft, brainstorm, and follow up. Celeste remembers the last five exchanges in this tab.',
  search: 'Find original passages directly. Search does not call Gemma.'
};
function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}
function button(text, className, action) {
  const node = el('button', className, text); node.type = 'button'; node.addEventListener('click', action); return node;
}
async function api(path, options) {
  const response = await fetch(path, options);
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || 'The local server could not complete this request.');
  return result;
}
function navigate(view, updateHash = true) {
  if (!['overview','journey','library','assistant'].includes(view)) view = 'overview';
  state.view = view;
  $$('.view').forEach(node => {node.hidden = node.id !== view;});
  $$('.rail .nav').forEach(node => {
    node.classList.toggle('active', node.dataset.view === view);
    if (node.dataset.view === view) node.setAttribute('aria-current','page'); else node.removeAttribute('aria-current');
  });
  if (updateHash && location.hash !== '#' + view) history.replaceState(null, '', '#' + view);
  window.scrollTo({top: 0, behavior: 'instant'});
}
function dateLabel(date, long = false) {
  return new Date(date+'T12:00:00').toLocaleDateString('en-GB', {day:'2-digit',month:long?'long':'short',...(long?{year:'numeric'}:{})});
}
function selectMatch(index) {state.match=index;renderMatches();renderMatch();navigate('journey');}
function renderMatches() {
  ['home-matches','journey-matches'].forEach(id => {
    const container = document.getElementById(id);container.replaceChildren();
    state.data.matches.forEach((match,index) => {
      const card = button('', 'match-card' + (state.match===index?' selected':''), () => selectMatch(index));
      card.setAttribute('aria-label', `Uruguay ${match.uruguay_goals}, ${match.opponent} ${match.opponent_goals}, ${match.stage}${match.shootout_uruguay_opponent?', Uruguay won the shootout 4–2':''}`);
      card.setAttribute('aria-pressed',String(state.match===index));
      const result = match.uruguay_goals>match.opponent_goals || match.shootout_uruguay_opponent ? 'win' : match.uruguay_goals<match.opponent_goals?'loss':'draw';
      card.append(el('span','match-stage',match.stage),el('i','result-dot '+result),el('span','flag flag-'+codes[match.opponent],codes[match.opponent]),el('span','opponent',match.opponent),el('strong','',`${match.uruguay_goals} – ${match.opponent_goals}`),el('span','match-date',dateLabel(match.date)),el('span','penalty-caption',match.shootout_uruguay_opponent?'URU win 4–2 on pens':''));
      container.append(card);
    });
  });
}
function inlineText(parent,text) {
  // Only bold markers are interpreted. Source and model text never becomes HTML.
  text.split(/(\*\*[^*]+\*\*)/g).forEach(part => parent.append(part.startsWith('**')&&part.endsWith('**') ? el('strong','',part.slice(2,-2)) : document.createTextNode(part)));
}
function prose(body, omitTitle = false) {
  const root=el('div','prose');let list=null;
  for (const line of body.split('\n')) {
    if (!line.trim()) {list=null;continue;}
    if (line.startsWith('# ')) {if(!omitTitle)root.append(el('h1','',line.slice(2)));list=null;}
    else if(line.startsWith('## ')){root.append(el('h2','',line.slice(3)));list=null;}
    else if(line.startsWith('- ')){if(!list){list=el('ul');root.append(list);}const li=el('li');inlineText(li,line.slice(2));list.append(li);}
    else{list=null;const p=el('p');inlineText(p,line);root.append(p);}
  }
  return root;
}
function noteBody(note) {return note.body.split('\n## Sources')[0].split('\n## Related notes')[0];}
function relatedLinks(note) {
  const row=el('div','related');
  note.related.forEach(title=>{const found=state.data.notes.find(n=>n.title===title);if(found)row.append(button(title+' ↗','chip',()=>openNote(found)));});
  return row;
}
function noteActions(note) {
  const row=el('div','reader-actions');
  row.append(button('Read original source ↗','button dark',()=>openSource(note.source_id)),button('Ask about this topic ✦','chip',()=>{
    $('#reader').close();navigate('assistant');setMode('ask');$('#question').value=`Tell me about ${note.title}.`;$('#question').focus();
  }));return row;
}
function renderMatch() {
  const match=state.data.matches[state.match];const note=state.data.notes.find(n=>n.title==='Uruguay and '+match.opponent);
  const root=$('#match-detail');root.replaceChildren();
  const score=el('div','score-panel');score.append(el('div','eyebrow',match.stage.toUpperCase()+' · '+dateLabel(match.date).toUpperCase()));
  const teams=el('div','score-teams');teams.append(el('span','','URUGUAY'),el('span','',match.opponent.toUpperCase()));
  score.append(teams,el('div','big-score',`${match.uruguay_goals} – ${match.opponent_goals}`));
  score.append(el('span','penalty-pill',match.shootout_uruguay_opponent?'After extra time · Uruguay win 4–2 on penalties':'Full time'));
  const facts=el('dl','match-facts');
  [['The stage',match.stadium+', '+match.city_in_2010],['In the stands',match.attendance.toLocaleString('en-GB')+' supporters'],['Uruguay scorers',match.uruguay_scorers],['Opposition scorers',match.opponent_scorers]].forEach(([label,value])=>{const group=el('div');group.append(el('dt','',label),el('dd','',value));facts.append(group);});
  score.append(facts);const article=el('div','match-article');article.append(el('span','review-tag',note?.reviewed?'SOURCE-REVIEWED WIKI NOTE':'WIKI NOTE · REVIEW PENDING'),el('h2','', 'Uruguay & '+match.opponent));
  if(note)article.append(prose(noteBody(note),true),noteActions(note),relatedLinks(note));
  root.append(score,article);
}
function renderLibrary() {
  const filter=$('#library-filter').value.toLowerCase().trim();const grid=$('#note-grid');grid.replaceChildren();
  const notes=state.data.notes.filter(note=>(state.category==='All'||note.category===state.category) && (note.title+' '+note.body).toLowerCase().includes(filter));
  notes.forEach(note=>{
    const card=button('','note-card',()=>openNote(note));
    const summary=noteBody(note).split('\n').find(line=>line && !line.startsWith('#'))||'';
    card.append(el('span','eyebrow',note.category.toUpperCase()),el('h3','',note.title),el('p','',summary.length>125?summary.slice(0,122)+'…':summary),el('span','note-meta',`${note.source_id} · ${note.reviewed?'Reviewed against source':'Review pending'} ↗`));grid.append(card);
  });
  if(!notes.length)grid.append(el('p','muted','No notes match that search. Try another word or category.'));
}
function renderSources() {
  const root=$('#source-list');root.replaceChildren();
  state.data.sources.forEach(source=>{const row=button('','source-row',()=>openSource(source.id));const name=el('div');name.append(el('strong','',source.title),el('small','',source.publisher+' · Original local text'));row.append(el('span','source-number',source.id),name,el('span','','↗'));root.append(row);});
}
function showReader(label) {$('#reader-label').textContent=label;if(!$('#reader').open)$('#reader').showModal();$('#reader').scrollTop=0;}
let readerRequest=0;
function openNote(note) {
  readerRequest++;const content=$('#reader-content');content.replaceChildren(el('span','review-tag',note.reviewed?'REVIEWED BY ASSISTANT · VERIFY AGAINST ORIGINALS':'REVIEW PENDING'),prose(noteBody(note)),noteActions(note),relatedLinks(note));showReader(note.category.toUpperCase()+' / '+note.source_id);
}
async function openSource(id) {
  const request=++readerRequest;const content=$('#reader-content');content.replaceChildren(el('p','muted','Opening original source…'));showReader('ORIGINAL SOURCE / '+id);
  try {
    const data=await api('/api/source/'+encodeURIComponent(id));if(request!==readerRequest)return;
    const credits=el('div','source-attribution',data.authors+' · Local snapshot. ');const link=el('a','','Published revision ↗');link.href=data.url;link.target='_blank';link.rel='noopener noreferrer';credits.append(link);
    data.licenses.forEach(url=>{const a=el('a','','License ↗');a.href=url;a.target='_blank';a.rel='noopener noreferrer';credits.append(a);});
    content.replaceChildren(el('h2','',data.title),credits,el('pre','source-text',data.text));
  }catch(error){if(request===readerRequest)content.replaceChildren(el('p','error',error.message));}
}
async function checkStatus() {
  const node=$('#model-status');node.disabled=true;$('span',node).textContent='Checking Gemma…';
  try{const result=await api('/api/status');node.classList.toggle('ready',result.ready);node.classList.toggle('unavailable',!result.ready);$('span',node).textContent=result.ready?'Gemma is ready':'Gemma unavailable';node.title=result.ready?result.model+' · Local model ready; this does not verify network disconnection.':result.message;}
  catch(error){$('span',node).textContent='Server unavailable';node.classList.remove('ready');node.classList.add('unavailable');node.title='Restart python3 dashboard.py, then click to check again.';}
  finally{node.disabled=false;}
}
function setMode(mode) {
  if(state.busy)return;
  state.mode=mode;$$('[data-mode]').forEach(node=>{const active=node.dataset.mode===mode;node.classList.toggle('active',active);node.setAttribute('aria-pressed',String(active));});
  $('#mode-description').textContent=descriptions[mode];$('#question').placeholder=mode==='search'?'Search the original sources…':mode==='chat'?'Ask for a draft, a study plan, or a follow-up…':'What would you like to discover?';$('#composer-note').textContent=mode==='search'?'ORIGINAL TEXT · NO MODEL CALL':'LOCAL GEMMA · '+(mode==='chat'?'RECENT CONVERSATION':'ORIGINAL SOURCES');
}
function displayEvidence(result, focusId) {
  const root=$('#answer-evidence');root.replaceChildren();
  if(!result.passages.length){root.append(el('p','muted',result.mode==='chat'?'This conversational response did not retrieve sources. Suggestions are not historical evidence.':'No matching source passages were found.'));return;}
  root.append(el('p','muted',result.mode==='search'?'Original text from your local archive.':'Retrieved originals. Check each claim against its source; a valid quotation does not guarantee a correct conclusion.'));
  result.passages.forEach(p=>{
    const details=el('details','passage');details.dataset.passage=p.id;details.open=focusId===p.id;
    details.append(el('summary','',p.section),el('span','passage-id',p.id+' · '+p.path),el('p','',p.text),button('Open full original ↗','text-button',()=>openSource(p.source_id)));root.append(details);
  });
  if(focusId){const node=$$('.passage',root).find(n=>n.dataset.passage===focusId);node?.scrollIntoView({behavior:'smooth',block:'nearest'});}
}
function addMessage(role,text,result) {
  $('#assistant-welcome')?.remove();const message=el('article','message '+role);message.append(el('div','message-label',role==='user'?'YOU':'CELESTE / '+result.mode.toUpperCase()));const body=el('div','message-text');
  text.split(/(\[S\d{2}-[a-f0-9]+\])/g).forEach(part=>{
    if(result && /^\[S\d{2}-[a-f0-9]+\]$/.test(part) && result.passages.some(p=>p.id===part.slice(1,-1))){body.append(button(part,'citation',()=>displayEvidence(result,part.slice(1,-1))));}else inlineText(body,part);
  });message.append(body);
  if(result){const meta=el('div','message-meta');const link=el('a','','View saved trace ↗');link.href='/api/evidence/'+result.evidence_id;link.target='_blank';link.rel='noopener';meta.append(link,el('span','',result.seconds!==null?`${result.seconds.toFixed(1)}s · local model`:'No model call'));if(result.passages.length)meta.append(button('Show sources','',()=>displayEvidence(result)));message.append(meta);}
  $('#conversation').append(message);return message;
}
async function submitQuestion(event) {
  event?.preventDefault();if(state.busy)return;const question=$('#question').value.trim();if(!question)return;
  state.busy=true;$('#question').disabled=true;const mode=state.mode;$('#send-question').disabled=true;$('#clear-chat').disabled=true;$$('[data-mode]').forEach(b=>b.disabled=true);
  addMessage('user',question);const pending=el('div','pending');const text=el('span','','');pending.append(el('span','spinner'),text);$('#conversation').append(pending);
  const start=Date.now();const tick=()=>{text.textContent=mode==='search'?'Searching the local originals…':`Celeste is reading and composing locally… ${Math.floor((Date.now()-start)/1000)}s. This can take a few minutes.`;};tick();const timer=setInterval(tick,1000);pending.scrollIntoView({block:'nearest'});
  try {
    const result=await api('/api/query',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mode,question,history:mode==='chat'?state.history.slice(-10):[]})});
    pending.remove();const message=addMessage('assistant',result.answer,result);if(mode==='chat')state.history=result.history.slice(-10);displayEvidence(result);$('#question').value='';message.scrollIntoView({block:'nearest',behavior:'smooth'});
  }catch(error){pending.className='error';pending.textContent=error.message+' Your question is still in the box so you can retry.';}
  finally {clearInterval(timer);state.busy=false;$('#question').disabled=false;$('#send-question').disabled=false;$('#clear-chat').disabled=false;$$('[data-mode]').forEach(b=>b.disabled=false);}
}
$$('[data-view]').forEach(node=>node.addEventListener('click',()=>navigate(node.dataset.view)));
window.addEventListener('hashchange',()=>navigate(location.hash.slice(1),false));
$('#explore').addEventListener('click',()=>selectMatch(0));
$('#ghana-feature').addEventListener('click',()=>selectMatch(4));
$('#forlan-stat').addEventListener('click',()=>{const note=state.data.notes.find(n=>n.title==='Diego Forlan at the World Cup');if(note)openNote(note);});
$('#library-filter').addEventListener('input',renderLibrary);
$$('[data-category]').forEach(node=>node.addEventListener('click',()=>{state.category=node.dataset.category;$$('[data-category]').forEach(b=>b.classList.toggle('active',b===node));renderLibrary();}));
$('#close-reader').addEventListener('click',()=>{$('#reader').close();readerRequest++;});
$('#reader').addEventListener('click',event=>{if(event.target===$('#reader')){const r=$('#reader').getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)$('#reader').close();}});
$('#model-status').addEventListener('click',checkStatus);
$$('[data-mode]').forEach(node=>node.addEventListener('click',()=>setMode(node.dataset.mode)));
$$('[data-question]').forEach(node=>node.addEventListener('click',()=>{if(state.busy)return;setMode('ask');$('#question').value=node.dataset.question;$('#question').focus();}));
$('#question-form').addEventListener('submit',submitQuestion);
$('#question').addEventListener('keydown',event=>{if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();submitQuestion();}});
$('#clear-chat').addEventListener('click',()=>{if(state.busy)return;state.history=[];$('#conversation').replaceChildren(el('p','muted','Conversation cleared. Ask a new question below.'));$('#answer-evidence').replaceChildren(el('p','muted','Sources will appear after a new research response.'));$('#question').value='';});
async function init(){
  try{state.data=await api('/api/bootstrap');renderMatches();renderMatch();renderLibrary();renderSources();setMode('ask');navigate(location.hash.slice(1)||'overview',false);checkStatus();}
  catch(error){$('#load-error').hidden=false;$('#load-error').textContent='Could not load the local archive. Restart python3 dashboard.py and reload this page. '+error.message;}
}
init();
