# From your first Codex task to a handoff

Start with the checklist repair in a practice folder. Run it from a
Codex chat, then use the same example to learn how to brief and verify a
reusable specialist. [First task and copyable request](../START_HERE.md#install-and-verify)

## Start from the ready installer

Use the [ready Universal or matching-platform Release asset](INSTALL.md#recommended-local-browser-installer). Extract it and open `Start.cmd` on Windows, `Start.command` on macOS, or `Start.sh` on Linux. The English/Ukrainian local wizard guides you through **Check → Prepare plan → review and approve → Install → Verify files → Check in Codex**. Its Python, Node and built interface are included. Codex and your own account remain separate prerequisites for actual agent work.

After installation, choose **Create practice project**, inspect it with **Open folder**, and request **Open Codex**. Copy the supplied prompt into that session. The generated launcher registers the installed roles and opens the exact new practice folder. Check that `README.md` becomes `# Checklist` and that `notes.txt` retains its contents. Setup has prepared files; the useful result exists only after your Codex session performs and verifies the task. Preserve a working project/venv interpreter; `AGENT_SYSTEM_PYTHON` identifies the toolkit's own helper interpreter.

If opening a terminal is unavailable on your desktop, open the returned practice folder in your normal Codex client and use the returned launcher instructions. Keep the installer journal for recovery. The conversational and source routes below remain available.

Personal discovery uses `CODEX_HOME/skills` on Windows (normally `<selected-home>/.codex/skills`) and `<selected-home>/.agents/skills` on macOS/Linux. Project-local `<project>/.agents/skills` stays unchanged. If an earlier Windows personal suite is still in the old `.agents/skills` tree, use the current installer’s reviewed migration plan and original rollback journal; do not move or delete it manually. Check the resolved path in a fresh Codex session. [Personal roots and migration](INSTALL.md#personal-skill-roots)

## Set up with guidance from Codex

If someone already installed the core skills, open a fresh project chat
and try `$agent-foundry`. Compare the loaded path and version with your
installation receipt or ask your administrator. A matching name in a
catalog is a useful discovery check. The checklist edit then lets you
inspect how the chat works with the actual folder.

If you are installing the system, give Codex the official installation
guide and ask it to explain and show the result of each setup step in
your language. Have it check the existing installation before choosing a
fresh install or an update. Review the destination and the ready audit
before applying. Codex can help run the documented steps when the chat
has the local tools and access they require.
[Signed installation and recovery](INSTALL.md) · [Guides in seven languages](../START_HERE.md#use-another-language)

Open a new chat in the practice folder after setup. Run the small
checklist edit and compare both files with their original contents.
If the chat reports a missing file or writes to a different folder,
reopen the intended folder and check the actual workspace before trying
again.

## Extend the task into a project workflow

Use this example when checklist review becomes recurring work. The
specialist's job is to check a proposed release against written criteria
and show missing evidence. For the exercise, use only local files in
the practice folder.

1. **Brief the work.** Start the request with `$atelier-orchestrator`
   if you installed it, or use `$agent-foundry` and ask for **BRIEF**.
   Explain who owns the checklist, which file contains the requirements
   and which files can prove each entry. For this exercise, require an
   exact candidate version and a recorded rollback verification. The
   expected output is a short review naming the evidence for each
   decision and leaving any incomplete item open. Explain that the
   exercise covers local review and its written result. If you only
   need a single checklist edit, the direct task on the start page
   already covers it. [Agent Foundry briefing](../kit/skills/agent-foundry/references/briefing-protocol.md)
2. **Create a specialist when you will reuse it.** Ask `$agent-foundry`
   for a project-local release checklist reviewer. Review the exact
   passport it produces. A passport is the proposal that names the
   specialist, its source files, permissions, expected result and tests.
   If it suits the job, approve the actual revision and digest for the
   stated project scope. Review the project-local installation plan, then
   verify the installed files against its receipt. Open a fresh chat in
   that project and select the generated skill by its passport name.
   Check its loaded source and try it first on a case with complete
   evidence and a case missing the rollback verification.
   [Construction and adoption](../kit/skills/agent-foundry/SKILL.md#design-and-approve-the-passport)
3. **Bring in real teammates for a material review.** Ask
   `$atelier-orchestrator` to coordinate, or ask the parent Codex
   session to assign the work. With the optional role profile installed
   on a host that supports subagents, give a `foundry-architecture` role
   the checklist structure and a separate `foundry-qa` role the actual
   evidence and pass criteria. Keep one writer for the checklist and
   have the QA role examine the result independently. Ask the parent to
   return which roles actually ran, what each found, and the output paths
   or results you can open. If the host cannot start a requested role,
   finish the work the parent can verify and keep independent review
   open. [Role installation](INSTALL.md#profile-and-roles) ·
   [Team deliberation](../optional-skills/atelier-orchestrator/references/team-deliberation.md)
4. **Review the evidence.** Open the review itself and the files it
   cites. Confirm which exact release version it evaluated, whether a
   rollback was actually observed, and whether the reviewer left the
   incomplete case open. Check that unrelated project files retained
   their contents. Record the independent result and then make the
   owner decision. [Validation](../governance/VALIDATION.md)
5. **Hand the work to a fresh chat.** Keep the project folder, candidate
   revision, review path, accepted decisions, open criteria, permissions,
   and one next action in the handoff. In your next chat, reopen that
   same folder and ask `$agent-foundry` to **RESUME** from the handoff,
   or open `$atelier-orchestrator` if it is your normal entry point.
   Check that the receiving chat found the exact sources and still
   reports the same unresolved items before giving it more work.
   [Handoff template](../templates/HANDOFF.md)

## Find your project in the local workbench

Use the workbench if you prefer to browse your local Codex projects
and inspect task inputs and results in a browser. Ready distributions provide
`Start-Workbench.cmd` (Windows), `Start-Workbench.command` (macOS), and `Start-Workbench.sh` (Linux);
the bundled interface needs no buyer build. For the retained source-build route,
follow the documented build and use `launcher/Agent Atelier.command` on Mac. Refresh the
project portfolio, pick your actual folder, and inspect the binding
preview. Open a source or a saved next action to start preparing a task.
Review the objective, source references, scope and acceptance checks
before dispatch. After a job, open the actual result and its receipt.
[Build and launch](../apps/agent-atelier/README.md#build-and-launch) ·
[First workbench task](../apps/agent-atelier/README.md#first-useful-task)

## Precision path

1. **Pin the source and inspect the install.** Use the exact stable
   release tag, commit, signed `CODEX` archive and manifest. Keep the
   audit and recovery directory so the recorded plan and journal stay
   available. Follow the core and optional profile procedures for the
   tools you actually use. Preserve the older observed state if the audit
   reports a conflict. [Stage the official archive](INSTALL.md#stage-the-official-archive) ·
   [Review and apply](INSTALL.md#review-and-apply)
2. **Run a bounded canary from the reviewed source checkout.** Use the
   documented Python and native Codex prerequisites. The direct repair
   uses a signed-in Codex host and a disposable fixture.

   ```bash
   python3 -B kit/verify_release.py
   python3 -B scripts/materialize_standards.py --check
   python3 -B scripts/check_repository.py
   receipt_dir="$(mktemp -d)"
   python3 -B evaluations/native_canary.py --case p01-direct \
     --output "$receipt_dir/direct.jsonl"
   cat "$receipt_dir/direct.jsonl"
   ```

   Read the artifact checks in the receipt. Run `p02-handoff` at a new
   receipt path to check a named native role. The `p03-passport` case
   produces a passport for exact review before you continue the proposed
   construction. Follow the documented consumer case once the kit has
   been approved. [Canary modes and receipts](../evaluations/README.md#run-a-focused-native-codex-canary)
3. **Bind the actual project.** Record the project identity, branch or
   worktree, accepted sources, applicable decisions, task owner, allowed
   paths, and verification test. Give each independent writer its own
   worktree when their changes need isolation. Recheck the sources in the
   receiving session before resuming or applying a reviewed boundary.
   [Working context](OPERATING_MODEL.md#project-context-and-handoffs) ·
   [Worktree assignments and recovery](technical/TICKET_WORKTREES.md)
4. **Keep recovery tied to the original operation.** Use the exact
   installation or task journal and inspect the current destination
   before repeating an interrupted effect. After restoring a component,
   verify its files, open a fresh chat to check discovery, and run its
   representative task. [Installation rollback](INSTALL.md#rollback) ·
   [Tools, evidence, and recovery](OPERATING_MODEL.md#tools-evidence-and-recovery)
