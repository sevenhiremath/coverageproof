# CoverageProof

A security assessment report that shows findings and unfinished checks.

[Open the application](https://coverageproof-demo.onrender.com/) · [Read the November 9 assessment report](samples/current-owned-http/assessment-nov9.pdf)

## The problem

An analyst may have several scanner reports and still not know what was actually checked. A missing result could mean a check found nothing, failed or never ran. Combining findings alone leaves that question unanswered.

CoverageProof tracks each declared check alongside its evidence and execution status. The analyst can see which checks still need work before handing over the report.

## Example

The home page has a missing security header. The same header check on the admin page has not run.

CoverageProof shows one finding candidate and an unattempted admin check. After the analyst approves the exact HTTP action, the app records the admin response. If it contains the expected header, that condition becomes `condition_not_observed`. The finding count stays one, but the unanswered check is now resolved.

This result applies to the recorded response and condition. It does not establish that the whole page or application is secure.

## Application workflow

1. Enter the assessment request and authorized scope.
2. Declare checks and import supported scanner results.
3. Inspect finding candidates, their evidence and unfinished checks.
4. Review the proposed follow-up and approve a supported action.
5. Download the assessment PDF with findings, remediation and limitations.

Findings retain source references and raw artifact hashes. Analysts can review candidates as accepted for report, false positive or needing review. New evidence invalidates earlier review decisions.

## Scanner support

| Input or action | What the application does |
| --- | --- |
| Nmap XML | Imports native discovery results |
| Nikto JSON | Imports native web findings |
| OWASP ZAP traditional JSON | Imports native web alerts |
| HTTP header check | Executes one bounded GET after exact approval |
| Nessus, OpenVAS / Greenbone, Burp Suite, Metasploit | No working adapter |

**The website does not launch Nmap, Nikto or ZAP.** Their outputs come from separately run scanners. An import preserves the source observations; missing alerts do not prove that a check completed without a finding.

## Run the current demo application

Python 3.11 or later is required. The repository's default branch contains the submission application.

```bash
git clone https://github.com/sevenhiremath/coverageproof.git
cd coverageproof
python -m venv .venv
```

Activate the environment on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Or on macOS / Linux:

```bash
source .venv/bin/activate
```

Install the application and start it:

```bash
python -m pip install -e .
python -m uvicorn coverageproof.app:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000.

These commands install application dependencies only. Configure environment variables before starting the app; settings are listed in [.env.example](https://github.com/sevenhiremath/coverageproof/blob/main/.env.example). The default local database is `data/coverageproof.sqlite`.

## Planning

Development mode uses explicitly labeled rules. It does not call an AI model.

The application supports Groq planning. Set `COVERAGEPROOF_PROVIDER=groq`, `GROQ_MODEL=openai/gpt-oss-120b` and your private `GROQ_API_KEY` before starting the application. The backend validates proposed checks and evidence references. An AI proposal is not permission to execute an action.

The submitted recording uses development planning. Groq was evaluated separately. Provider failures and rate limits remain limitations.

## Sample report and supporting details

- [Sample VAPT report](samples/current-owned-http/sample-vapt.pdf), recorded on November 2 with an owned HTTP fixture and development planning. This is separate from the November 9 video assessment.
- [Sample evidence and recording context](samples/current-owned-http/README.md)
- [Integration status](docs/INTEGRATIONS.md)
- [Current project status](docs/STATUS.md)

## Application stack

Python, FastAPI, Jinja2, HTML/CSS, SQLite, Groq and ReportLab.

## Current boundaries

- Live execution supports the bounded HTTP check.
- Coverage refers to declared checks, not all possible vulnerabilities.
- Impact and exploitability may remain unknown. Findings require analyst review.
- The hosted demo uses temporary storage.
- Testing must remain inside an explicitly authorized scope. Organizer evaluation authorization is separate from the owned development fixture.

[Hosted demo](https://coverageproof-demo.onrender.com/)  
[Application source](https://github.com/sevenhiremath/coverageproof)  
[Dependency acknowledgments](THIRD_PARTY.md)

Built by Swayam Hiremath for DataOps Innovation Hackathon 2026, PS-1. AI-assisted implementation.

