from pathlib import Path
from lxml import html
import csv,json,re
R=Path(__file__).resolve().parents[1]
CAT=json.loads((R/'research/sources.json').read_text())
S={s['id']:s for s in CAT['sources']}
def cite(sid,label=None):
 s=S[sid];return '['+(label or s['title'])+']('+s['permanent_url']+')'
def write_csv(name,keys,rows):
 with (R/'data'/name).open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)

def cell(e,cl):
 n=e.xpath('.//*[contains(concat(" ",normalize-space(@class)," ")," '+cl+' ")]')
 return ' '.join(n[0].text_content().split()) if n else ''
rows=[
['2010-06-11','Group A','France',0,0,'','Cape Town Stadium','Cape Town','None','None',64100,'S01'],
['2010-06-16','Group A','South Africa',3,0,'','Loftus Versfeld Stadium','Pretoria','Diego Forlán 24; Diego Forlán 80 penalty; Álvaro Pereira 90+5','None',42658,'S01'],
['2010-06-22','Group A','Mexico',1,0,'','Royal Bafokeng Stadium','Rustenburg','Luis Suárez 43','None',33425,'S01'],
['2010-06-26','Round of 16','South Korea',2,1,'','Nelson Mandela Bay Stadium','Port Elizabeth','Luis Suárez 8; Luis Suárez 80','Lee Chung-yong 68',30597,'S02'],
['2010-07-02','Quarter-final','Ghana',1,1,'4-2','Soccer City','Johannesburg','Diego Forlán 55','Sulley Muntari 45+2',84017,'S02'],
['2010-07-06','Semi-final','Netherlands',2,3,'','Cape Town Stadium','Cape Town','Diego Forlán 41; Maximiliano Pereira 90+2','Giovanni van Bronckhorst 18; Wesley Sneijder 70; Arjen Robben 73',62479,'S02'],
['2010-07-10','Third-place match','Germany',2,3,'','Nelson Mandela Bay Stadium','Port Elizabeth','Edinson Cavani 28; Diego Forlán 51','Thomas Müller 19; Marcell Jansen 56; Sami Khedira 82',36254,'S02']]
keys=['date','stage','opponent','uruguay_goals','opponent_goals','shootout_uruguay_opponent','stadium','city_in_2010','uruguay_scorers','opponent_scorers','attendance','source_id']
matches=[dict(zip(keys,row)) for row in rows]
write_csv('matches.csv',keys,matches)
(R/'data/matches.json').write_text(json.dumps(matches,ensure_ascii=False,indent=2)+'\n')
# Extract the actual Uruguay squad rows, preserving the source's club convention.
t=html.fromstring((R/S['S03']['original_html']).read_bytes())
table=t.xpath('//*[@id="Uruguay"]')[0].xpath('following::table[1]')[0]
squad=[]
for tr in table.xpath('.//tr')[1:]:
 values=[' '.join(x.text_content().split()) for x in tr.xpath('./th|./td')]
 if len(values)!=6 or not values[0].isdigit():continue
 number,position,name,birth,caps,club=values
 roles={'GK':'Goalkeeper','DF':'Defender','MF':'Midfielder','FW':'Forward'}
 squad.append(dict(number=int(number),player=name,position=roles.get(re.sub(r'\d','',position),position),date_of_birth=re.search(r'\d{4}-\d{2}-\d{2}',birth).group(),age_at_tournament_start=int(re.search(r'aged (\d+)',birth).group(1)),caps_before_tournament=int(caps),club_as_listed=club,source_id='S03'))
assert len(squad)==23
write_csv('squad.csv',list(squad[0]),squad)
# Qualification match facts are extracted directly from the source HTML.
t=html.fromstring((R/S['S04']['original_html']).read_bytes())
qualifiers=[]
for box in t.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," footballbox ")]'):
 home,away=cell(box,'fhome'),cell(box,'faway')
 if 'Uruguay' not in (home,away):continue
 qualifiers.append(dict(date=cell(box,'fdate'),home=home,away=away,score=cell(box,'fscore'),source_id='S04'))
assert len(qualifiers)==18,len(qualifiers)
write_csv('qualifiers.csv',list(qualifiers[0]),qualifiers)
refs=[
('R01','RSSSF','World Cup 2010 match details','https://www.rsssf.org/tables/2010full.html'),
('R02','FIFA','Tournament review and individual awards','https://inside.fifa.com/en/tournaments/mens/worldcup/2010south-africa/news/pride-for-africa-spain-strike-gold-2247372'),
('R03','FIFA','Ghana and Uruguay in 2010','https://www.fifa.com/en/articles/ghana-uruguay-a-thriller-for-the-ages-world-cup-qatar-2022-south-africa-2010'),
('R04','DFB','Uruguay versus Ghana match record','https://datencenter.dfb.de/en/data-center/fifa-world-cup/2010-in-south-africa/quarter-final/uruguay-ghana-116187'),
('R05','FIFA','Diego Forlán against Germany','https://www.fifa.com/en/tournaments/mens/worldcup/articles/diego-forlan-goal-uruguay-germany-2010'),
('R06','FIFA','Abreu and the decisive penalty','https://www.fifa.com/en/articles/when-el-loco-lived-up-to-his-name')]
(R/'research/references.json').write_text(json.dumps([dict(id=i,publisher=p,title=t,url=u,use='External verification link; not reproduced in the local corpus') for i,p,t,u in refs],ensure_ascii=False,indent=2)+'\n')
FIFA=refs[1][3];RSSSF=refs[0][3]
d='''# Uruguay at the 2010 World Cup

Uruguay finished fourth at the 2010 FIFA World Cup in South Africa, reaching the semi-finals for the first time since 1970. Óscar Washington Tabárez coached the team, Diego Lugano was its regular captain, and Diego Forlán won the Golden Ball as the tournament’s best player.

This dossier brings together the qualification campaign, the Costa Rica playoff, all seven World Cup matches, the 23-player squad, goals, venues, decisive incidents, and source-quality notes. It is research material for the personal wiki project. It is not a Gemma-generated wiki or evidence that the application has been implemented.

'''+cite('S02','Knockout-stage history')+'; '+cite('S03','Squad and coach')+f'; [FIFA tournament review]({FIFA}).\n\n'
d+='''## Campaign at a glance

| Measure | Uruguay’s record |
|---|---|
| Final position | Fourth |
| Matches played | 7 |
| Wins, draws, defeats | 3 wins, 2 draws, 2 defeats |
| Goals scored and conceded | 11 scored, 8 conceded |
| Goal difference | +3 |
| Group A finish | First, with 7 points |
| Group-stage goals | 4 scored, none conceded |
| Leading scorer | Diego Forlán, 5 goals |
| Main individual award | Forlán, Golden Ball |

The Ghana match is statistically a draw after extra time, followed by a Uruguay shootout win. Shootout kicks are not added to match goals or individual tournament scoring totals. This explains why the statistical record lists three wins even though Uruguay also advanced past Ghana.

'''+cite('S06','Final standings and awards')+'; '+cite('S01','Group A standings')+'.\n\n'
d+='''## Qualification and the Costa Rica playoff

Uruguay finished fifth in the South American qualifying league with 24 points from 18 matches: six wins, six draws, and six defeats. The team scored 28 goals and conceded 20. Fifth place earned an intercontinental playoff against Costa Rica, the fourth-placed CONCACAF team.

Uruguay won the first leg 1–0 in San José on 14 November 2009, with a goal from Diego Lugano. The second leg ended 1–1 at the Estadio Centenario in Montevideo on 18 November. Sebastián Abreu scored for Uruguay and Walter Centeno equalised for Costa Rica. Uruguay qualified 2–1 on aggregate.

The complete 18-match qualifying schedule is included in `data/qualifiers.csv`. The preserved playoff article includes lineups, substitutions, venues, referees, and both match reports.

'''+cite('S04','CONMEBOL qualification')+'; '+cite('S05','Costa Rica–Uruguay playoff')+'.\n\n'
d+='''## Group draw and group standings

The final draw took place on 4 December 2009 in Cape Town. Uruguay joined host nation South Africa, Mexico, and France in Group A. The group was played from 11 to 22 June 2010.

| Team | Points | Played | Won | Drawn | Lost | Goals for | Goals against |
|---|---|---|---|---|---|---|---|
| Uruguay | 7 | 3 | 2 | 1 | 0 | 4 | 0 |
| Mexico | 4 | 3 | 1 | 1 | 1 | 3 | 2 |
| South Africa | 4 | 3 | 1 | 1 | 1 | 3 | 5 |
| France | 1 | 3 | 0 | 1 | 2 | 1 | 4 |

Uruguay and Mexico advanced. Uruguay faced South Korea, the runner-up in Group B, in the round of 16.

'''+cite('S07','Contemporary group-draw report')+'; '+cite('S01','Group A record')+'.\n\n'
d+='## All seven World Cup matches\n\nScores below always place Uruguay first. Dates use the local match date. Goal times follow the match records in the English sources; `90+5` means five minutes into second-half stoppage time.\n\n| Date | Stage | Opponent | Score | Uruguay scorers |\n|---|---|---|---|---|\n'
for m in matches:
 score=f"{m['uruguay_goals']}–{m['opponent_goals']}"+(' after extra time; 4–2 on penalties' if m['shootout_uruguay_opponent'] else '')
 d+=f"| {m['date']} | {m['stage']} | {m['opponent']} | {score} | {m['uruguay_scorers']} |\n"
d+='\n'+cite('S01','Group-stage match records')+'; '+cite('S02','Knockout match records')+f'; [RSSSF cross-check]({RSSSF}).\n\n'
sections=[
('Uruguay versus France','S01','Uruguay opened on 11 June at Cape Town Stadium, also known as Green Point. The match finished 0–0. Nicolás Lodeiro came on as a substitute and was sent off after two bookings, leaving Uruguay to finish with ten players. The opening point was followed by two group-stage wins.'),
('Uruguay versus South Africa','S01','On 16 June at Loftus Versfeld in Pretoria, Uruguay beat the hosts 3–0. Forlán scored from distance in the 24th minute and converted a penalty in the 80th. South African goalkeeper Itumeleng Khune was sent off after bringing down Suárez. Álvaro Pereira added a third goal in stoppage time. Uruguay now had four points and had not conceded.'),
('Uruguay versus Mexico','S01','Uruguay won 1–0 at Royal Bafokeng Stadium on 22 June. Suárez scored the only goal with a header in the 43rd minute. Uruguay finished first in Group A with seven points and three clean sheets. Mexico also qualified, ahead of South Africa on goal difference.'),
('Uruguay versus South Korea','S02','At Nelson Mandela Bay Stadium on 26 June, Suárez opened the scoring in the eighth minute after a Forlán cross. Lee Chung-yong equalised with a header in the 68th minute. Suárez then scored a curling shot in the 80th minute to secure a 2–1 victory. Uruguay reached the quarter-finals for the first time since 1970.'),
('Uruguay versus Ghana','S02','On 2 July at Soccer City in Johannesburg, Sulley Muntari put Ghana ahead just before half-time. Forlán equalised with a free kick in the 55th minute. The game remained 1–1 through extra time. In its closing moments, Suárez blocked a goal-bound header with his hand on the goal line and was sent off. Asamoah Gyan struck the resulting penalty against the crossbar. Uruguay then won the shootout 4–2, with Muslera saving two kicks and Abreu scoring the decisive fifth Uruguayan penalty.'),
('Uruguay versus the Netherlands','S02','Uruguay lost 2–3 in the semi-final at Cape Town Stadium on 6 July. Giovanni van Bronckhorst scored first; Forlán equalised before half-time. Wesley Sneijder and Arjen Robben put the Netherlands 3–1 ahead in the second half. Maximiliano Pereira scored during stoppage time, but Uruguay could not find another equaliser. Suárez missed the match following his red card against Ghana.'),
('Uruguay versus Germany','S02','Uruguay lost 2–3 in the third-place match at Nelson Mandela Bay Stadium on 10 July. Thomas Müller gave Germany the lead, Cavani equalised, and Forlán put Uruguay 2–1 ahead. Marcell Jansen equalised and Sami Khedira scored the winner. Forlán struck the crossbar with a late free kick. Uruguay finished fourth, while Germany took third place.')]
for title,sid,body in sections:d+='### '+title+'\n\n'+body+'\n\n'+cite(sid,'Source and match record')+'.\n\n'
d+='''## The Ghana penalty shootout

| Round | Uruguay kick | Ghana kick |
|---|---|---|
| 1 | Forlán scored | Gyan scored |
| 2 | Victorino scored | Appiah scored |
| 3 | Scotti scored | Muslera saved John Mensah’s kick |
| 4 | Maximiliano Pereira missed | Muslera saved Dominic Adiyiah’s kick |
| 5 | Abreu scored with a chipped penalty | No fifth kick was required |

Final shootout score: Uruguay 4–2 Ghana. Gyan’s penalty against the crossbar occurred at the end of extra time; he subsequently scored his separate shootout attempt. Abreu’s decisive kick is often described as a Panenka-style penalty. It does not count towards Uruguay’s 11 tournament goals.

'''+cite('S02','Quarter-final narrative and shootout')+f'; [FIFA account]({refs[2][3]}).\n\n'
d+='''## Squad and leadership

Coach: Óscar Washington Tabárez. Regular captain: Diego Lugano. The following table uses the English squad source’s player roles and clubs at the tournament. Roles are roster categories, not a claim that each player occupied the same tactical position in every match. Club names remain proper names in their original spelling.

| No. | Player | Squad role | Club listed in the source |
|---|---|---|---|
'''
for p in squad:d+=f"| {p['number']} | {p['player']} | {p['position']} | {p['club_as_listed']} |\n"
d+='\n'+cite('S03','Uruguay squad')+'. `data/squad.csv` also records dates of birth, ages, and international caps as listed before the tournament.\n\n'
d+='''## Goals and individual contributions

| Player | Match goals | Opponents |
|---|---|---|
| Diego Forlán | 5 | South Africa twice; Ghana; Netherlands; Germany |
| Luis Suárez | 3 | Mexico; South Korea twice |
| Álvaro Pereira | 1 | South Africa |
| Maximiliano Pereira | 1 | Netherlands |
| Edinson Cavani | 1 | Germany |

These totals sum to 11, excluding shootout kicks. Forlán shared the tournament’s highest goal total of five with Müller, David Villa, and Sneijder. Müller received the Golden Boot under the tournament’s tie-breaking criteria. Forlán received the Golden Ball, an award for the best player rather than the top scorer. The source overview records 23.4% of the Golden Ball vote for Forlán.

Muslera’s two shootout saves and Abreu’s final kick were decisive against Ghana. Suárez scored both round-of-16 goals as well as the winner against Mexico. Cavani scored Uruguay’s first goal against Germany. Lugano captained the side, while Tabárez managed the full campaign.

'''+cite('S01','Group matches')+'; '+cite('S02','Knockout matches')+'; '+cite('S06','Scoring and awards')+f'; [FIFA awards summary]({FIFA}).\n\n'
d+='''## Venues and crowds

| Opponent | Stadium | City in 2010 | Attendance |
|---|---|---|---|
'''
for m in matches:d+=f"| {m['opponent']} | {m['stadium']} | {m['city_in_2010']} | {m['attendance']:,} |\n"
d+='\n'+cite('S01','Group match reports')+'; '+cite('S02','Knockout match reports')+'. Cape Town Stadium and Green Point refer to the same venue in these accounts. The table uses contemporary city names rather than replacing them with later names.\n\n'
d+='''## Tactical reading and historical significance

The preserved match sources provide starting lineups, substitutions, cards, and accounts of the main changes in each game. They show Forlán, Suárez, and Cavani starting together from the South Africa match, with personnel changes as the tournament progressed. Numerical formation labels should be treated as an analyst’s interpretation: different sources can label the same lineup differently.

Reaching the semi-finals ended a 40-year absence from that stage. Uruguay progressed farther than any other South American team at this tournament. The achievement should still be described accurately: Uruguay finished fourth, did not reach the final, and lost its final two matches.

'''+cite('S02','Knockout bracket and match accounts')+f'; [RSSSF lineups]({RSSSF}).\n\n'
d+='''## Research limits and source handling

This is a substantial research collection, not an exhaustive archive of every interview, tactical opinion, or private team detail. The seven English articles contain wider tournament context as well as Uruguay-specific evidence. Future retrieval should select relevant sections rather than send the whole collection to a small model.

The original HTML downloads are preserved without changes. Plain-text versions remove interface elements and normalize formatting; they are not translations or model-written summaries. Public images and videos are linked from some sources but are not downloaded or licensed by this package.

Treat event minutes, formation labels, historical club affiliations, and opinionated match descriptions carefully. Keep the date of a match separate from an article’s publication or update date. The quality notes explain known interpretation issues. The generated dossier, tables, and expected answers remain outside the original-source corpus.

## Next steps for the assignment

The research stage is complete. Next, choose and install a compatible local Gemma runtime, generate readable linked wiki notes from these sources, and implement the required chat, ask, search, ingest, and help commands. No model tests, runtime measurements, Obsidian screenshots, or offline demonstration have been completed yet.

The four fixed research tests and a broader question bank are stored under `evaluation/`. They must not be indexed as source evidence. The final wiki should have one coherent topic per note, with links back to original sources and meaningful links between related topics.

## Attribution

This dossier adapts information from the Wikipedia and Wikinews pages linked above. Contributor histories, version links, licenses, and download hashes are recorded in `research/Sources and Licenses.md` and `research/sources.json`. This dossier is shared under CC BY-SA 4.0; each original source retains its own license. External FIFA, DFB, and RSSSF pages are cited for verification and are not reproduced in full.
'''
(R/'Uruguay 2010 Research Dossier.md').write_text(d)
# Source catalog.
c='# Sources and Licenses\n\nSeven original English articles form the downloaded research corpus. English filenames and documentation are used throughout. Proper names retain their original spelling. Full HTML snapshots are preserved in `vault/raw/originals/`; extracted article text is in `vault/raw/`.\n\n'
for s in CAT['sources']:
 c+=f"## {s['id']} {s['title']}\n\nAuthor attribution: {s['authors']}. Language: English.\n\n[Article]({s['url']}) · [Consulted revision]({s['permanent_url']}) · [History and contributors]({s['history_url']}).\n\nLocal text: `{s['text_path']}`. Original download: `{s['original_html']}`. Extracted words: {s['word_count']:,}.\n\nLicense links supplied by the page: "+', '.join(f'[Creative Commons]({u})' for u in s['license_urls'])+'.\n\n'
c+='''## Reuse and transformations

The Wikipedia pages link to CC BY-SA 4.0. The Wikinews page links to both CC BY 4.0 and its historical CC BY 2.5 notice; both are preserved in the catalog and original HTML. Keep contributor attribution, page and history links, license links, and the transformation notice when redistributing. Adaptations of Wikipedia material must retain the applicable share-alike terms.

Extraction removes interface elements, normalizes whitespace and tables, and preserves selected meaningful image alternative text. It does not translate, summarize, or silently correct the articles. Full HTML retains the original reference lists and links. No photographs or videos were downloaded; their licensing may differ from the article text.

The six Wikipedia articles are distinct documents, not six independent editorial organizations. FIFA, DFB, and RSSSF provide additional cross-checks. Keep this distinction clear when describing source diversity.

## External verification references

These pages are linked for checking facts. Their full copyrighted text is not included in the corpus and does not inherit Wikimedia licensing.

'''
for i,p,t,u in refs:c+=f'- {i}: [{p}: {t}]({u}).\n'
(R/'research/Sources and Licenses.md').write_text(c)
q=[
{'id':'ask-01','question':'What were Uruguay’s results in the group stage of the 2010 World Cup, and how many points did they finish with?','expected_answer':'A 0–0 draw with France, a 3–0 win over South Africa, and a 1–0 win over Mexico. Uruguay finished first in Group A with seven points.','source_ids':['S01'],'source_sections':['Standings','Uruguay vs France','South Africa vs Uruguay','Mexico vs Uruguay']},
{'id':'ask-02','question':'How was Uruguay’s match against Ghana decided, and what did Muslera and Abreu do?','expected_answer':'The match ended 1–1 after extra time. Uruguay won the shootout 4–2. Muslera saved John Mensah’s and Dominic Adiyiah’s kicks; Abreu converted the decisive kick.','source_ids':['S02'],'source_sections':['Uruguay vs Ghana']},
{'id':'ask-03','question':'Who did Uruguay play after the quarter-finals, and where did they finish?','expected_answer':'Uruguay lost 2–3 to the Netherlands in the semi-final and 2–3 to Germany in the third-place match, finishing fourth.','source_ids':['S02','S06'],'source_sections':['Uruguay vs Netherlands','Match for third place','Final standings']},
{'id':'ask-04','question':'What did Diego Forlán eat for breakfast on the day Uruguay played Ghana in the 2010 World Cup?','expected_answer':'The sources do not provide this information. The system should explicitly report insufficient evidence.','source_ids':[],'source_sections':[]}]
for x in q:x['status']='Not run; expectation defined before implementation';x['expected_source_paths']=[S[s]['text_path'] for s in x['source_ids']]
(R/'evaluation/questions.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
(R/'evaluation/Question Bank.md').write_text('''# Uruguay 2010 Question Bank

These are proposed evaluation questions, not source evidence. Keep this directory outside the retrieval index. The four required fixed tests are in `questions.json`; none has been executed against Gemma.

## Qualification

1. Where did Uruguay finish in CONMEBOL qualification?
2. How many points, wins, draws, and defeats did Uruguay record in qualification?
3. Who did Uruguay face in the intercontinental playoff?
4. What were the two playoff scores and the aggregate result?
5. Who scored Uruguay’s goals in those two matches?

## Group stage

6. Which countries were in Uruguay’s group?
7. What happened to Nicolás Lodeiro in the opening match?
8. Who scored against South Africa?
9. Who scored the winner against Mexico?
10. How many goals did Uruguay concede in the group stage?

## Knockout matches

11. Who scored both goals against South Korea?
12. How did Forlán equalise against Ghana?
13. What happened after Suárez’s handball?
14. Did Gyan miss his shootout kick, or a separate penalty before the shootout?
15. Which two Ghana players had their shootout kicks saved?
16. Who scored Uruguay’s decisive shootout penalty?
17. Who scored for Uruguay against the Netherlands?
18. Did Uruguay take the lead against Germany?
19. Which German player scored the winning goal?

## Squad and awards

20. Who coached Uruguay and who was its regular captain?
21. Which three goalkeepers were in the squad?
22. What was Forlán’s shirt number?
23. How many tournament goals did Suárez score?
24. What is the difference between Forlán’s Golden Ball and Müller’s Golden Boot?
25. Why are Abreu’s shootout goal and Uruguay’s shootout kicks excluded from tournament goal totals?

## Evidence boundaries

26. What did Forlán eat for breakfast before the Ghana match? Expected: insufficient evidence.
27. If a user invents a personal conversation with Tabárez in chat, should ask mode treat it as a historical source? Expected: no.
28. Can search show the original Ghana passage without starting Gemma? Expected: yes, once the retrieval tool exists.
''')
(R/'research/Source Quality Notes.md').write_text('''# Source Quality Notes

The source files preserve what the downloaded English articles say. This document records interpretation and extraction limits separately, so the originals are not silently rewritten.

## Match results and shootouts

Uruguay’s Ghana result is 1–1 after extra time and 4–2 in the shootout. Statistical match records count the former as a draw. A source describing a Uruguay win may mean advancement on penalties. State both scores whenever ambiguity matters. Shootout goals are excluded from individual match-goal totals.

## Event minutes

Some event labels use the elapsed clock minute while narrative match records use the ordinal minute of play. For example, a video labeled 50 minutes can describe a goal reported in the 51st minute. The dossier follows the English Group A and knockout match tables. Preserve source labels and investigate differences rather than treating every one-minute discrepancy as a different event.

## Roles and formations

Squad positions and match roles are not interchangeable. Álvaro Pereira can appear as a defender in a squad list and as a midfielder in a match lineup. Published diagrams and formation labels may differ. Do not infer a single fixed formation for the entire campaign from one graphic.

## Names and club affiliations

Maxi Pereira and Maximiliano Pereira identify the same player. Egidio Arévalo and Egidio Arévalo Ríos also refer to the same player. Club fields use the English squad source’s historical convention; a loan club and a parent club can differ. Proper names remain in their original spelling even though the project is in English.

## Extracted text

The original HTML snapshots are unchanged. Extracted text normalizes whitespace and tables, removes interface material, and retains meaningful alternative text where available. Some row-spanning table values and graphical substitution markers can lose context in plain text. Use the preserved HTML when an exact table relationship matters. A source reference number without its full bibliography should be followed in the preserved HTML.

## Scope and independence

The corpus contains whole articles, including other teams and broader tournament context. Retrieval should identify the Uruguay-specific sections. Six sources come from Wikipedia and one from Wikinews; these are distinct articles, not seven independent publishers. External FIFA, DFB, and RSSSF links are available for verification but their full articles have not been added as local evidence.

## Limits of verification

The research checks cover the seven scores, dates, scorers, venues, squad size, qualification record, shootout sequence, and main award distinction. They do not independently certify every sentence in every downloaded source. The dossier does not establish what players privately ate, thought, or said unless a source records it. All Gemma evaluation results are still pending.
''')
(R/'research/Research Collection Overview.md').write_text('''# Uruguay 2010 Research Collection

This English-language research package covers Uruguay’s route to fourth place at the 2010 World Cup. It includes seven original English articles, all seven World Cup match records, 18 qualifying fixtures, the 23-player squad, an explanatory dossier, and evaluation questions for the future local Gemma wiki.

- [Read the research dossier](Uruguay%202010%20Research%20Dossier.md).
- [Review sources and licenses](research/Sources%20and%20Licenses.md).
- [Read source quality notes](research/Source%20Quality%20Notes.md).
- [Browse original-source text](vault/raw/).
- [Inspect match data](data/matches.json).
- [View the squad](data/squad.csv).
- [View the qualifying fixtures](data/qualifiers.csv).
- [Review the four pending tests](evaluation/questions.json).
- [Explore the question bank](evaluation/Question%20Bank.md).

## What is complete

Research and source collection are complete for this stage. Full HTML downloads are preserved in `vault/raw/originals/`, with source URLs, revision links, licenses, download timestamps, and SHA-256 hashes in `research/sources.json`. Plain-text source extractions are in `vault/raw/`. The dossier and data tables are derived research materials, not independent primary sources.

## What comes next

Gemma and its runtime have not been installed. The CLI harness, generated wiki pages, Obsidian screenshots, measured memory and response time, and offline demonstration are still pending. Do not describe the saved expected answers as actual model results.

The future retrieval index should read original-source text, not the `evaluation/` directory or answer keys. Whole articles contain wider tournament context, so relevant sections should be selected before sending passages to the model. Final wiki notes should be generated using local Gemma and then checked against the sources.

## Reproducing the research files

The scripts require Python 3 and lxml. `scripts/collect_sources.py` downloads the English sources and extracts text; `scripts/build_research.py` builds the dossier and tables from the saved source metadata and snapshots. Downloading needs internet. The saved HTML and hashes preserve the exact research version; a new download may retrieve changed pages. Back up the collection before refreshing it.

## Attribution

Keep the source catalog, contributor histories, license links, and transformation notes when sharing. The dossier is shared under CC BY-SA 4.0. Each original source retains its own license. External verification references have not been reproduced in full. No model weights, credentials, photographs, or videos are included.
''')
print('English dossier:',len(d.split()),'words; sources:',len(S),'matches:',len(matches),'squad:',len(squad),'qualifiers:',len(qualifiers))
