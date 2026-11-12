# PERSONALISE

Every placeholder of the package: what it means, an example value (fake, from
02_setup_prompt\answers_TEMPLATE.json) and the files that use it. The setup asks you for these values,
writes them to answers.json and runs fill_placeholders.py; your values then live in
campaign\00_profile\personalisation_map.json. "(derived)" values are computed if you leave them out.
Values marked EXAMPLE are rule examples: give your own, or a neutral sentence.

| Placeholder | Meaning | Example | Used in |
|---|---|---|---|
| `{{CAMPAIGN_NAME}}` | name of the campaign (titles) | PFE 2027 | 03_kit\campaign\CLAUDE.md, 05_build_sources\build_guide_source.html, 05_build_sources\make_runbook.py |
| `{{CAMPAIGN_FILE_STEM}}` | campaign name without spaces: names your runbook and Build Guide in guides (derived) | (derived: PFE2027) | 03_kit\campaign\CLAUDE.md, 05_build_sources\friendly_setup_and_usage.html, make_runbook.py and render_guides.py (file names) |
| `{{CAMPAIGN_START}}` | date the campaign mail starts (Gmail after:) | 2026/09/01 | 03_kit\campaign\.claude\commands\pfe-inbox.md |
| `{{CHROME_PROFILE}}` | Chrome profile folder with the Claude extension | Default | 03_kit\campaign\CLAUDE.md, 05_build_sources\build_guide_source.html, 05_build_sources\make_runbook.py |
| `{{CONTACT_EMAIL}}` | email printed on CV and letters | test@example.com | 03_kit\campaign\CLAUDE.md |
| `{{COUNTRIES_HUNTED_BEFORE}}` | countries already covered | none yet | 03_kit\campaign\.claude\commands\pfe-hunter.md, 05_build_sources\make_runbook.py |
| `{{COURSES}}` | list: course names the CV may show (build.py refuses others) | Strength of Materials, Fluid Mechanics, Heat Transfer | 00_profile\personalisation_map.json (read by build.py / preflight.py) |
| `{{COURSEWORK_ONLY_AREAS}}` | areas known only from coursework, never sold as experience | Control theory and robotics | 03_kit\campaign\CLAUDE.md |
| `{{DECK_MODEL}}` | deck used as the model | the first deck you edit yourself (none yet: the slide set of build_deck.js as it is) | 03_kit\campaign\.claude\commands\pfe-interview-prep.md, 03_kit\campaign\CLAUDE.md, 05_build_sources\make_runbook.py |
| `{{DECK_MODEL_SHORT}}` | its short name | model | 05_build_sources\build_guide_source.html, 05_build_sources\make_runbook.py |
| `{{DECK_NOTE_EXAMPLE}}` | example speaker note with a // part | Example: "The main result held across every sample //the spread stayed small, which we traced to the preparation step//." (after S0 PROFILE) | 03_kit\campaign\.claude\commands\pfe-interview-prep.md |
| `{{DECK_PROJECT_SLIDES}}` | which project slides the deck keeps | the project slides of profile_deck.json | 03_kit\campaign\.claude\commands\pfe-interview-prep.md |
| `{{DECK_SPEC_PROJECTS}}` | how a deck spec orders projects | which project comes first (a key of profile_deck.json projects) | 03_kit\campaign\.claude\commands\pfe-interview-prep.md |
| `{{DEGREE}}` | degree and field | Mechanical Engineering | 03_kit\campaign\00_profile\FORM_ANSWERS.md, 03_kit\campaign\00_profile\interview_deck\profile_deck.json, 03_kit\campaign\CLAUDE.md |
| `{{DEMONSTRATED_EXPERIENCE}}` | what your real experience is (positioning) | mechanical design, prototyping and testing | 03_kit\campaign\CLAUDE.md |
| `{{EXCLUDED_ORGS}}` | organisations never to apply to | no organisation (EXAMPLE: list here any organisation you must never apply to) | 03_kit\campaign\.claude\commands\pfe-checker.md, 03_kit\campaign\.claude\commands\pfe-hunter.md, 03_kit\campaign\CLAUDE.md, 05_build_sources\build_guide_source.html, 05_build_sources\make_runbook.py |
| `{{FAILURE_QUESTION}}` | interview prep: the "what if it does not work" question of your field (after S0 PROFILE) | What I would do if the main experiment or prototype does not work | 03_kit\campaign\.claude\commands\pfe-interview-prep.md |
| `{{FIELD_CHOICE_QUESTION}}` | interview prep: the "why this field and not the neighbouring one" question (after S0 PROFILE) | Why this field and not a neighbouring one | 03_kit\campaign\.claude\commands\pfe-interview-prep.md |
| `{{FILE_STEM}}` | name part of document file names, First_Last (derived) | (derived) | 03_kit\campaign\00_profile\FORM_ANSWERS.md, 03_kit\campaign\CLAUDE.md, 05_build_sources\make_runbook.py |
| `{{FINAL_YEAR}}` | final academic year | 2026-2027 | 03_kit\campaign\CLAUDE.md |
| `{{FIRST_NAME}}` | first word of FULL_NAME (derived) | (derived) | 03_kit\campaign\.claude\commands\pfe-applier.md, 03_kit\campaign\.claude\commands\pfe-checker.md, 03_kit\campaign\.claude\commands\pfe-send.md, 03_kit\campaign\CLAUDE.md, 05_build_sources\make_runbook.py |
| `{{FORM_ADDRESS}}` | portal answer: postal address | NEEDS_ANSWER | 03_kit\campaign\00_profile\FORM_ANSWERS.md |
| `{{FORM_DATE_OF_BIRTH}}` | portal answer: date of birth | NEEDS_ANSWER | 03_kit\campaign\00_profile\FORM_ANSWERS.md |
| `{{FORM_DIVERSITY}}` | portal answer: diversity questions | prefer not to say | 03_kit\campaign\00_profile\FORM_ANSWERS.md |
| `{{FORM_EU_CITIZEN}}` | portal answer: EU/EEA citizen | no | 03_kit\campaign\00_profile\FORM_ANSWERS.md |
| `{{FORM_GENDER}}` | portal answer: gender | prefer not to say | 03_kit\campaign\00_profile\FORM_ANSWERS.md |
| `{{FORM_SALARY}}` | portal answer: salary wording EN and FR | paid position, no figure (FR: stage rémunéré, sans montant) | 03_kit\campaign\00_profile\FORM_ANSWERS.md |
| `{{FULL_NAME}}` | your full name as on your CV | Test User | 03_kit\campaign\.claude\commands\pfe-inbox.md, 03_kit\campaign\00_profile\FORM_ANSWERS.md, 03_kit\campaign\00_profile\interview_deck\profile_deck.json, 03_kit\campaign\04_outbound\_gen\run34\specs\EXAMPLE_PFE-0001.json, 03_kit\campaign\CLAUDE.md, 05_build_sources\build_guide_source.html, 05_build_sources\friendly_setup_and_usage.html, 05_build_sources\make_runbook.py |
| `{{GMAIL_ACCOUNT}}` | Gmail account of the connector; applications and portals use it | test@example.com | 03_kit\campaign\.claude\commands\pfe-applier.md, 03_kit\campaign\00_profile\FORM_ANSWERS.md, 03_kit\campaign\00_profile\interview_deck\profile_deck.json, 03_kit\campaign\CLAUDE.md, 05_build_sources\build_guide_source.html, 05_build_sources\friendly_setup_and_usage.html |
| `{{GMAIL_LABEL}}` | Gmail label for campaign mail | pfe-test | 03_kit\campaign\.claude\commands\pfe-inbox.md, 03_kit\campaign\CLAUDE.md, 05_build_sources\build_guide_source.html, 05_build_sources\make_runbook.py |
| `{{GMAIL_LABEL_ID}}` | its id (Gmail list_labels) | Label_0000000000000000000 | 03_kit\campaign\.claude\commands\pfe-inbox.md, 03_kit\campaign\CLAUDE.md |
| `{{GMAIL_LABEL_TO_LEAVE}}` | other labels the runs must leave alone | none | 03_kit\campaign\.claude\commands\pfe-inbox.md, 03_kit\campaign\CLAUDE.md, 05_build_sources\kit_blocks.json |
| `{{GRADES_EN}}` | the only grade wording allowed, English | EXAMPLE: top 20% of cohort | 03_kit\campaign\00_profile\FORM_ANSWERS.md, 03_kit\campaign\CLAUDE.md, 05_build_sources\build_guide_source.html |
| `{{GRADES_FR}}` | the same in French | EXAMPLE: top 20 % de la promotion | 03_kit\campaign\00_profile\FORM_ANSWERS.md, 03_kit\campaign\CLAUDE.md |
| `{{GRADUATION}}` | graduation month and year | September 2027 | 03_kit\campaign\00_profile\FORM_ANSWERS.md, 03_kit\campaign\00_profile\interview_deck\profile_deck.json, 03_kit\campaign\CLAUDE.md |
| `{{HOME_CITY}}` | city you live in | Sfax | 03_kit\campaign\00_profile\FORM_ANSWERS.md, 03_kit\campaign\CLAUDE.md |
| `{{HOST_BRIEF_EXAMPLE}}` | example of a host asking for its own talk format | (EXAMPLE: as a host may ask for a 10-minute talk) | 03_kit\campaign\.claude\commands\pfe-interview-prep.md |
| `{{INSTRUMENTS}}` | list: instruments on CV paragraph 5 (build.py reorders only these) | CNC machining, 3D printing, tensile testing | 00_profile\personalisation_map.json (read by build.py / preflight.py) |
| `{{INSTRUMENTS_LINE}}` | instruments and techniques you personally operated, one line | CNC machining, 3D printing, tensile testing | 03_kit\campaign\CLAUDE.md |
| `{{KEY_RESULTS_STORY}}` | the key numbers of your strongest project | EXAMPLE: your strongest project rests on your own work: name its two or three key numbers here. | 03_kit\campaign\.claude\commands\pfe-interview-prep.md |
| `{{LANGUAGES_LINE}}` | working languages, one sentence | French and English, both working languages | 03_kit\campaign\CLAUDE.md |
| `{{LINKEDIN}}` | LinkedIn on the CV | linkedin.com/in/test-user | 00_profile\personalisation_map.json (read by build.py / preflight.py) |
| `{{MEMORY_KEY}}` | Claude Code project key of WORKSPACE (derived) | (derived) |  |
| `{{MY_REPORTS}}` | your report files read by interview prep | EXAMPLE: your project and internship reports in ..\my documents\reports and projects\ | 03_kit\campaign\.claude\commands\pfe-interview-prep.md |
| `{{NATIONALITY}}` | nationality (visa reasoning) | Moroccan | 03_kit\campaign\.claude\commands\pfe-hunter.md, 03_kit\campaign\00_profile\FORM_ANSWERS.md, 03_kit\campaign\CLAUDE.md, 05_build_sources\build_guide_source.html |
| `{{NEVER_MENTION}}` | a result never to mention in interviews | any result you do not want to discuss (EXAMPLE: replace or write none) | 03_kit\campaign\.claude\commands\pfe-interview-prep.md, 03_kit\campaign\CLAUDE.md, 05_build_sources\build_guide_source.html, 05_build_sources\make_runbook.py |
| `{{NOTEBOOKLM_MODEL}}` | NotebookLM prompt used as the model | the first NOTEBOOKLM_PROMPT.txt you are happy with (none yet: follow this section as written) | 03_kit\campaign\.claude\commands\pfe-interview-prep.md |
| `{{PFE_WINDOW}}` | internship window | February to August 2027 | 03_kit\campaign\.claude\commands\pfe-inbox.md, 03_kit\campaign\00_profile\FORM_ANSWERS.md, 03_kit\campaign\00_profile\interview_deck\profile_deck.json, 03_kit\campaign\03_documents\LETTER_MASTER.md, 03_kit\campaign\04_outbound\_gen\run34\specs\EXAMPLE_PFE-0001.json, 03_kit\campaign\CLAUDE.md, 05_build_sources\build_guide_source.html, 05_build_sources\make_runbook.py |
| `{{PHONE}}` | phone printed on CV and letters | +216 00 000 000 | 03_kit\campaign\00_profile\FORM_ANSWERS.md, 03_kit\campaign\00_profile\interview_deck\profile_deck.json, 03_kit\campaign\CLAUDE.md |
| `{{PREP_MODEL}}` | interview prep used as the model | the first interview prep you are happy with (none yet: follow this section as written) | 03_kit\campaign\.claude\commands\pfe-interview-prep.md |
| `{{PREP_MODEL_SHORT}}` | its short name | your best prep so far | 03_kit\campaign\.claude\commands\pfe-interview-prep.md, 05_build_sources\make_runbook.py |
| `{{PREP_NAME_EXAMPLE}}` | example of short Org, Name | (Org, Name) | 03_kit\campaign\.claude\commands\pfe-interview-prep.md |
| `{{READING_EXAMPLE}}` | interview prep: what a change in one of your typical graphs means (after S0 PROFILE) | a shift, a broader peak, a new feature, a steeper slope | 03_kit\campaign\.claude\commands\pfe-interview-prep.md |
| `{{ROOT}}` | the folder that holds campaign, interviews, my documents, guides and sniper | C:\Users\test\OneDrive\Desktop\pfe workflow | 03_kit\campaign\.claude\commands\pfe-interview-prep.md, 03_kit\campaign\CLAUDE.md, 05_build_sources\build_guide_source.html, 05_build_sources\make_runbook.py |
| `{{SCHOOL}}` | short name of your school (signs the internship agreement) | ENIS | 03_kit\campaign\.claude\commands\pfe-checker.md, 03_kit\campaign\.claude\commands\pfe-hunter.md, 03_kit\campaign\.claude\commands\pfe-inbox.md, 03_kit\campaign\00_profile\FORM_ANSWERS.md, 03_kit\campaign\00_profile\interview_deck\profile_deck.json, 03_kit\campaign\03_documents\LETTER_MASTER.md, 03_kit\campaign\04_outbound\_gen\run34\specs\EXAMPLE_PFE-0001.json, 03_kit\campaign\CLAUDE.md, 05_build_sources\build_guide_source.html, 05_build_sources\friendly_setup_and_usage.html, 05_build_sources\kit_blocks.json, 05_build_sources\make_runbook.py, 05_build_sources\one_time_prompts.py |
| `{{SEARCH_FIELDS}}` | fields the Hunter searches | Mechanical design, manufacturing, materials testing, energy, R&D | 03_kit\campaign\CLAUDE.md |
| `{{SKETCH_AXES_EXAMPLE}}` | interview prep: the axes of one of your typical graphs, with units (after S0 PROFILE) | for example x = time in s, y = signal in its unit | 03_kit\campaign\.claude\commands\pfe-interview-prep.md |
| `{{SKETCH_FEATURES_EXAMPLE}}` | interview prep: features named on a sketch (after S0 PROFILE) | a peak, a slope, a threshold | 03_kit\campaign\.claude\commands\pfe-interview-prep.md |
| `{{SKETCH_SHAPES}}` | interview prep: the typical graphs of your techniques, to sketch (after S0 PROFILE) | a spectrum with peaks or bands, a curve over time, a response curve, a calibration line | 03_kit\campaign\.claude\commands\pfe-interview-prep.md |
| `{{SOFTWARE_LINE}}` | software you use | Python, SolidWorks, MATLAB | 03_kit\campaign\CLAUDE.md |
| `{{TECHNIQUE_ABBREV_EXAMPLE}}` | interview prep: one technique abbreviation, EN / FR (after S0 PROFILE) | the English / French abbreviation of one of my techniques | 03_kit\campaign\.claude\commands\pfe-interview-prep.md |
| `{{UNIVERSITY}}` | university | University of Sfax | 03_kit\campaign\00_profile\FORM_ANSWERS.md, 03_kit\campaign\00_profile\interview_deck\profile_deck.json, 03_kit\campaign\CLAUDE.md, 05_build_sources\build_guide_source.html, 05_build_sources\make_runbook.py |
| `{{USER_HOME}}` | your Windows user folder (derived) | (derived) | 03_kit\campaign\CLAUDE.md, 05_build_sources\build_guide_source.html, 05_build_sources\make_runbook.py |
| `{{WORKSPACE}}` | ROOT\campaign (derived) | (derived) | 03_kit\campaign\CLAUDE.md, 05_build_sources\build_guide_source.html, 05_build_sources\friendly_setup_and_usage.html, 05_build_sources\make_runbook.py |
