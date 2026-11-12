# Open questions — gaps and contradictions

Format: **gap → default assumed → evidence → how to change it.** Nothing here blocks a run. Every default is
marked `[assumed]` in `me.md` and never stated as fact in an application. To fix one: write the answer under it
(or drop a document in `profile/inbox/`) and run `/get-to-know-me`.

## Contradictions between your own documents

- **Q-01 MIP project: lab work or literature case studies?** → default: CVs may reuse your newest wording
  ("Synthèse et caractérisation …") verbatim; letters/emails never call it hands-on and never use it as proof of
  UV-Vis/Soxhlet/polymerisation practice. → CV13 (17 Sep) "Reviewed … Evaluated three drug delivery case studies";
  CV11 "validated on human bronchial cells" (unlikely in a student lab); CV02/CV03/CV05 (Nov) "Synthesis and
  characterization …". → Answer "lab" or "literature", and which steps you did yourself.
- **Q-02 "Hands-on" claims in letters that the CVs don't support.** CL03 (CEA Saclay): "hands-on experience with
  sol-gel-type nanomaterial synthesis and structural characterization (XRD, SEM/TEM)"; CL02 (UTC): "hands-on
  experience with Raman spectroscopy and SEM, developed during a literature review project" and "solid practice
  with FTIR and NMR". → default: treated as **studied** (§5c of me.md); the writing-style skill forbids repeating
  these claims (rule NV-02). → Tell me which instruments you really operated (TP sessions count — say which).
- **Q-09 AGIL dates.** → default 07/2025–08/2025 (newest CV01). → CV07/CV12 say 07/2025–07/2025. → Confirm.
- **Q-14 Availability in old letters.** → default: the standing rule (1 Feb 2027, 6 months, 3–9 possible). →
  CL04 says "janvier/février 2026" (typo), CL05 "5 à 6 mois", CL02 "February/March 2027". → Nothing to do unless
  the rule is wrong.
- **Q-15 Name order.** → default: FR documents "Moumen Nermine" in the CV header, EN "Nermine Moumen"; letters
  header "Moumen Nermine", signature "Nermine Moumen" (newest letters). → Tell me if you want one order everywhere.

## Missing information

- **Q-03 Domain priorities.** → default: batteries/electrochemistry ≈ hydrogen/PtX ≈ process simulation+TEA/LCA >
  materials/catalysis > water/waste > analytical > nuclear (used in `strategic_value`). → order of your CV
  versions and of your 8 applications (5 of 8 are battery/energy). → Edit `config/scoring.yaml: strategic_sectors`.
- **Q-04 Preferred countries.** → default: France first, then BE/CH/LU, DE/NL, rest of Europe, Canada; Tunisia as
  fallback. → all 8 applications are France (7) or Germany (1). → Edit `config/search.yaml: countries`.
- **Q-05 Nationality / visa.** → default: Tunisian, non-EU, needs a visa and an INSAT convention; no existing
  EU residence permit. → Tunisian phone, studies in Tunisia. → Write your nationality and any permit you hold.
- **Q-06 Grades / rank.** → default: never mention grades. → no transcript provided. → Drop your relevés de notes
  in `profile/inbox/`.
- **Q-07 SEGULA location.** → default: not stated in any application. → no document. → Add city/country.
- **Q-08 Supervisors and referees** (SEGULA tutor, INSAT project supervisors, Control Union/AGIL/ETAP tutors). →
  default: no referee is ever named. → none in the documents. → Add name, role, and what they can vouch for.
- **Q-10 Certificates "Aspen HYSYS – MATLAB".** → default: written exactly so, no issuer/date. → all CVs. → Add
  issuer (e.g. AspenTech / MathWorks Onramp?) and date, or drop the certificates in the inbox.
- **Q-11 Language certificates** (TOEIC/TOEFL/IELTS/DELF). → default: none; levels as on your newest CVs. → none.
- **Q-12 Enactus PhosphAct** (dates, your role beyond "led"). → default: mentioned only in letters as "with Enactus
  INSAT, I led PhosphAct, a project valorizing phosphogypsum waste into paint", never on a CV. → CL01 only.
- **Q-13 Domains or companies to avoid.** → default: none (`config/search.yaml: exclusions` empty). → none stated.
- **Q-16 Aspen Process Economic Analyzer.** → default: may be cited for P3 only in letters for TEA roles (single
  source CL01). → Confirm you used it.
- **Q-17 Dates you sent the 8 letters / outcomes.** → default: `config/applied.csv` rows carry `date_applied`
  = unknown and status = applied. → Fill dates and any answers there.
- **Q-18 Diploma title & graduation date.** → default: Diplôme National d'Ingénieur en Chimie Industrielle,
  graduation 2027 (after the PFE). → seed context. → Confirm the exact diploma wording.
