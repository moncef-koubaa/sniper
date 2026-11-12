---
description: Full interview preparation from one email address or message. Interactive only; never writes the tracker.
argument-hint: "<interviewer email address or pasted message>"
---
Follow CLAUDE.md.

INTERVIEW PREP. I have an interview. Prepare me completely.

  Email: $ARGUMENTS

Work out the rest yourself from my mailbox (Gmail connector), my tracker
(02_tracker\tracker.csv and blocked.csv), 04_outbound and their site.
My reports for section 6, in ..\my documents\reports and projects\ (changed 18 Oct 2026):
{{MY_REPORTS}}, and 00_profile\PROFILE.md and
DEFENSIBLE_CLAIMS.md for what is mine and what is the team's.

This session does not hunt, does not apply and does not write the tracker.
It does one job: get me ready. Run it interactively, never on the schedule.

RESEARCH RULES
Open the actual pages. Anything you did not read on a page you opened is
marked UNVERIFIED, and anything you are reasoning rather than reading is
marked INFERRED. Never invent a publication, a project, a funder, a title
or a person. If you cannot find something, say so plainly: a blank I know
about is useful, a guess that I repeat in the room is not.

Produce the whole thing as one markdown file I can read on my phone:
05_reports\<YYYY-MM-DD>_interview_prep_<Org>_<Name>.md, plus a PDF of it next to it.
Then build the interview folder with its three files (section 10, changed 13 Oct
2026), every time the prep is built or rebuilt, and give me the folder path in
the final report.

0. ESTABLISH THE FACTS FIRST
Before any research, pin down what this interview actually is.

a. Search Gmail for that address, and for its domain, in both received
   and sent mail. Read every thread in full, mine and theirs, oldest
   first. The invitation is usually not the only relevant message: my
   original application, their acknowledgement and any document request
   all carry information.
b. Match the domain and the address against tracker.csv. If a row
   matches, read it: the project title, the application URL, the score,
   the notes, the date I applied, and which CV and letter version went
   out. Read those documents from 04_outbound so I know exactly what
   they have already seen about me.
c. From all of that, fill in and state back to me at the top:
     Organisation
     Position or project
     Interviewer, name and role
     Date, time, my time zone and theirs
     Format: video or in person, platform, length
     Anyone else attending
     Anything they asked me to bring, prepare or send
     The documents they already have from me
   Mark each one VERIFIED with the source (which email, which tracker
   row) or UNKNOWN. Never guess a date or a time. If the interview time
   is ambiguous across time zones, say so plainly rather than picking one.
d. If the address matches nothing in my mail and nothing in the tracker,
   stop and tell me, rather than researching the wrong organisation.
e. If the email is from a generic HR or no-reply address and names no
   individual, say the interviewer is UNKNOWN and research the team or
   group named in the offer instead. Do not guess who will be in the room.

1. THE ORGANISATION
What they actually do, in plain terms. Size, type, where this team sits
inside it. Their work in my field specifically, not their mission
statement. Recent work from the last 3 years: projects, products,
publications, funding, partnerships, anything they announced. Who their
competitors or peer institutions are. Anything that tells me why this
position exists right now.

2. THE SUPERVISOR OR INTERVIEWER
Only from public professional sources: their own institution page,
Google Scholar, ORCID, ResearchGate, the organisation's site, LinkedIn,
conference pages. Nothing personal, nothing from social media that is
not professional.
- Their background and career path
- What they actually work on now, and how it differs from what they
  worked on five years ago
- Their five most relevant publications or projects to this position,
  with one line each on what the work found or built
- Techniques and instruments their group uses
- Who they collaborate with
- Whether they have supervised interns or international students before
- The open problem their recent work points at next. This is the single
  most useful thing in this section: it is what section 7 is built on.
- Three things about their work I could refer to in the room that would
  show I read it properly, each with the specific paper or page it
  comes from

3. THE PROJECT ITSELF
What the work would actually involve, week by week if the offer gives
enough to say so. The techniques and instruments I would use. Where it
sits in the group's larger effort. What a supervisor would consider a
successful internship here. What the hard parts are likely to be.
Then, explicitly: the line from their published work to this project.
Which paper or result does this internship follow on from, and what
would it add. If the offer does not say and you cannot establish it
from their publications, say so rather than inventing a lineage.

4. QUESTIONS THEY WILL ASK ME
Group them: about me and my motivation, about the organisation and why
them, about my technical background, about the project, about the
practical side (dates, convention de stage, visa, languages,
accommodation).
For each question: the question, then one line on what they are really
testing, then the FULL ANSWER, written out completely so that I can say it
as it is in the room. Not bullet points, not an outline, not "use section 5"
or "see CHECK": the actual words, in the first person, in plain spoken
sentences, as in {{PREP_MODEL}} (the model:
match its depth and its fully written answers for every question).
- Length: 60 to 150 words for most answers (about 30 to 60 seconds
  spoken), up to 200 for "tell me about yourself" and the main technical
  ones. Short questions (languages, dates) get short answers.
- Language: the language the interview will be held in (the language of
  their emails if not stated). If unclear, write the answer in English and
  add the French version under it.
- Content: only facts from my real files (CV sent to them, reports,
  PROFILE.md, DEFENSIBLE_CLAIMS.md). Real numbers, instruments and results.
  My contribution and the team's kept apart in the wording ("I ran...",
  "the team measured..."). Coursework stated as coursework. Grades only as
  CLAUDE.md allows. No banned words, no em dashes.
- Never mention {{NEVER_MENTION}},
  in an answer, a weak spot, a deck slide, the speaker notes or the NotebookLM
  prompt, and never use it as an argument (13 Oct 2026). {{KEY_RESULTS_STORY}}
- Where an answer depends on something not yet settled (a CHECK item in
  section 6), still write the full answer, put the uncertain part in
  [CHECK: ...] brackets, and write the alternative sentence to say if the
  check goes the other way.
- Where they could follow up, add one line "If they push:" with the full
  follow-up answer.
Include the uncomfortable ones, also fully answered. {{FIELD_CHOICE_QUESTION}}. Why an international PFE. {{FAILURE_QUESTION}}. What I do not know yet. Any weakness section 0
found (duplicate applications, CV inconsistencies, a gap in the techniques
they list).
Also write out in full: the "tell me about yourself" answer (section 5
opening plus the next 60 to 90 seconds), and the answer to each of the
three hardest technical questions per project in section 6.

5. WHAT TO LEAD WITH FROM MY CV
Which experiences to put first for this specific interview and why.
Which ones to keep back unless asked. One sentence I can use as an
opening when they say "tell me about yourself", built from evidence, not
adjectives.
Since section 0 established which CV and letter they already have, say
which parts they have already read, so I expand rather than repeat.

6. PROJECT REFRESHER
This is the section I will read the morning of the interview. Go through
my uploaded reports and, for every project in my experience, produce a
full technical brief:

  - The question the project set out to answer, and why it mattered
  - What I personally did, and separately what the team or group did.
    Keep those two lists apart. Never merge them.
  - Materials and exact compositions
  - Full method: synthesis or sample preparation, conditions,
    temperatures, times, concentrations, every parameter the report
    records
  - Every instrument and technique I operated, with the settings and
    parameters used
  - The results, with the actual numbers from the report
  - What the numbers mean, and what I concluded
  - What went wrong, what I would do differently, and what the
    limitations were
  - The three hardest technical questions someone could ask me about
    this project, each with the full spoken answer (same rules as
    section 4: complete sentences I can say as they are)
  - Anything in the report I could not tie to my own hands: list it
    under CHECK BEFORE THE INTERVIEW so I can settle it myself rather
    than being caught out

Be precise. Real numbers, real conditions, real instrument settings. A
vague refresher is worse than none because it gives me false confidence.

6A. TECHNIQUES (added 7 Oct 2026)
One entry for every technique, instrument and method named on the CV
they have (00_profile\PROFILE.md and the CV in 04_outbound), in my reports,
and anywhere on the host's pages: the offer, the group pages, the
interviewer's publications (section 2). Not only the ones we share: every
one the host uses, even ones I have never touched. Group them: "On my CV"
first, then "Used by the host", and mark each host entry "operated" or
"not yet operated" so I never claim it.
For each technique:
  - Name, full name and usual abbreviation (FR and EN if they differ,
    e.g. {{TECHNIQUE_ABBREV_EXAMPLE}})
  - What it is, in two plain sentences: the physical principle
  - The problem it targets: the question it answers in a lab or plant
  - What it measures, and what the instrument or method gives out
    (a spectrum, a pattern, a curve, a number)
  - A small sketch of the typical graph, drawn as inline SVG inside the
    markdown so it shows in the PDF: the general shape ({{SKETCH_SHAPES}}). Both axes
    labelled with the quantity and the unit ({{SKETCH_AXES_EXAMPLE}}), and one or two features named on the sketch
    ({{SKETCH_FEATURES_EXAMPLE}}). A
    generic shape, not my data, and say so in the caption.
  - How to read it: what a change in the graph means ({{READING_EXAMPLE}})
  - Where I used it (the project, and what I did with my own hands, kept
    apart from the team) or, for a host technique, how it would fit the
    project and what I know of it from coursework or reading
  - One likely question on it, with the full spoken answer (section 4
    rules)
Cover every technique from both lists; none left out, none shortened.
Build the PDF from HTML (markdown to HTML with the SVGs inline, then
headless Chrome --print-to-pdf) and check the sketches show in the PDF.

7. FIVE QUESTIONS I ASK THEM
Five questions, each one built on something you actually read in their
publications or on their group pages, and each one connected forward to
the project I would be doing. A question about their work that does not
land on this project sounds like I am reciting research I did the night
before. A question about the project that does not come from their work
sounds like I read the offer and nothing else. Every question must do
both.

Build each one on this shape:
  - The anchor: the specific paper, result, method choice or group page
    it comes from, named exactly, with the year
  - The question itself, one or two sentences, in my voice
  - The link: the sentence that ties the anchor to what I would be doing,
    so the question follows naturally from the conversation instead of
    arriving from nowhere
  - What asking it signals, in one line
  - What their likely answer tells me about whether I want this position

Across the five, cover different ground: one on the scientific direction,
one on the method or instrumentation I would actually use, one on how my
six months fits the group's longer effort, one on what a good outcome
looks like to them, and one on how the group works day to day.

Rank them, best first. If the interview runs short I will only get to
two, so the first two must be the strongest.

None of them may be answerable from the public pages alone. If I could
have looked up the answer, the question is wasted.

8. KEEP IN MIND
The things that decide how this goes. What they are worried about with a
non-EU final-year student, and how the convention de stage, my dates and
the visa timeline answer that before they raise it. Where my profile is
genuinely strong here and where it is genuinely thin, and how to handle
the thin part honestly rather than talking around it. Anything about
their culture, language or interview style that changes how I should
come across.

9. SMALL TIPS
Practical and short. What to have open or on the desk. What to have
ready to send straight after. Timing, time zones, what to do in the
first and last two minutes. Anything specific to this organisation or
country.

Do not pad any section. If you have little for one, say so and move on.
If the date and time are confirmed and no Calendar event exists, create one
("PFE interview: <company>", link in the description).

10. THE INTERVIEW FOLDER (changed 18 Oct 2026)
One folder per interview in my interviews folder, next to the workspace:
{{ROOT}}\interviews\<YYYY-MM-DD>_<Organisation>_<Interviewer>\
YYYY-MM-DD is the interview date from interviews.csv. If the date is unknown,
use today and end the folder name with _date-TBC. <Organisation> and
<Interviewer> are short, as in the prep file name {{PREP_NAME_EXAMPLE}}. If the folder
exists (a rebuild, or the date moved), reuse it and rename it to the right date.
Nothing goes loose in the root of the interviews folder. It gets three files:

  a. <YYYY-MM-DD>_interview_prep_<Organisation>_<Interviewer>.pdf: the full
     prep PDF above, same content and quality (section 6A sketches, {{PREP_MODEL_SHORT}}
     as the model). The 05_reports copy stays too.
  b. <YYYY-MM-DD>_<Organisation>_presentation.pptx: a short self-presentation
     deck for this interview. The model for structure, length, style, slide
     set and speaker notes is the deck I edited (changed 17 Oct 2026):
     {{DECK_MODEL}}.
     Keep only its slides: title, about me, agenda, {{DECK_PROJECT_SLIDES}}, instruments, how I understand
     their research, what I read about the group, where I could contribute,
     practical and thank you. No "What I would change" lessons slide, no "Three
     things the numbers told me" slide, no other filler slide; the agenda does
     not announce a slide that is not there.
     Speaker notes follow its pattern. First say what the slide shows, in
     simple spoken words, then the result or progress it explains, in a few
     short sentences. Anything that over-explains (instrument settings, exact
     peak positions or wavenumbers, extra figures, mechanisms, dates) goes
     between // and // inside the notes: kept for questions, not said in the
     talk. {{DECK_NOTE_EXAMPLE}} The agenda slide has no notes.
     Build it with 00_profile\interview_deck\build_deck.js (run "npm install"
     in that folder once if node_modules is missing):
       node build_deck.js specs\<YYYY-MM-DD>_<Organisation>_<Interviewer>.json <folder>\<pptx>
     The spec (copy the closest one in specs\) gives the language ("en" or
     "fr", from interview_language), the title, the agenda, {{DECK_SPEC_PROJECTS}}, the "not yet" card,
     the host slides (how I understand their research in three steps, four
     cards of what I read about the group, three ways I could contribute) and
     the speaker notes, which are the script, written to be said as they are
     apart from the // parts.
     The shared slides (about me, the projects, instruments) come from
     00_profile\interview_deck\profile_deck.json (changed 18 Oct 2026) and hold
     only PROFILE.md and DEFENSIBLE_CLAIMS.md facts;
     every host fact comes from section 1 to 3 of this prep, and anything
     INFERRED is said as my reading or my question, never as a fact. WRITING
     rules apply (no banned words, no em dashes); coursework stays coursework;
     a host technique I have not operated is only ever "not yet". If they asked
     for a presentation of a given length or content, follow their brief
     {{HOST_BRIEF_EXAMPLE}} instead of the standard slides. Open it in PowerPoint,
     export the slides as PNG and look at them: nothing cut off or overlapping.
  c. NOTEBOOKLM_PROMPT.txt: a ready-to-paste NotebookLM prompt, always a
     plain-text note (.txt, UTF-8), never .md, and no Markdown syntax inside:
     no # headings, no ** or backticks, no ``` fences; headings are plain
     lines in capitals, the text to paste sits between the lines
     "----- COPY FROM HERE -----" and "----- COPY TO HERE -----" (changed
     17 Oct 2026). Model:
     {{NOTEBOOKLM_MODEL}}. Step 1 says to
     upload the prep PDF and the pptx as the only sources. Step 2 is the prompt:
     it says which language the interview is in (interview_language, or the
     language of their emails) and that NotebookLM coaches me in that language
     throughout; it states the interview facts and the campaign rules (my work
     against the team's, coursework, grades, money as in UNPAID OR LOW-PAID
     OFFERS, no banned words); then it coaches me one part at a time, waiting
     for me between parts: the key points about the host, the project and the
     interviewer; the techniques I must be able to explain; my likely
     questions with model answers; my weak spots and how to handle them; the
     questions I should ask them; and a final mock interview that asks one
     question at a time, waits for my answer, scores it and corrects it.
     Step 3 (optional) is an audio-overview instruction in the same language.

End with the three things I should do today, in order, and how long each
takes. Remember: section 6 flags anything in my reports that cannot clearly be
tied to my own hands under CHECK BEFORE THE INTERVIEW.
