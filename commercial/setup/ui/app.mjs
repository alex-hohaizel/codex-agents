const $ = id => document.getElementById(id);
const text = (node, value) => { node.textContent = value ?? ''; };
const dictionaries = {
 en: {
 technicalEdition:'Technical release',
 setupLabel:'LOCAL SETUP',language:'Language',eyebrow:'YOUR TEAM, ON YOUR COMPUTER',title:'One setup.\nYour whole toolkit.',intro:'Install the skills, coordinating agent and roles. Keep your projects, local changes and recovery path.',receivedPackage:'Received package',localOnly:'Local installer · no cloud account for setup',stepCheck:'Check',stepCheckNote:'This computer',stepReview:'Review',stepReviewNote:'Exact changes',stepInstall:'Install',stepInstallNote:'Then verify',stepBegin:'Begin',stepBeginNote:'One useful task',checkEyebrow:'01 · KNOW WHAT IS READY',checkTitle:'Check this computer',checkButton:'Check now',checkHelp:'The installer checks the package, your system and Codex. Signing in to Codex is separate from installing local files.',notChecked:'Not checked yet',reviewEyebrow:'02 · YOUR FILES STAY YOURS',reviewTitle:'Review the exact plan',auditButton:'Prepare plan',reviewHelp:'An audit lists the target folders and required changes. Unknown local edits are held for review instead of overwritten.',auditEmpty:'Check this computer, then prepare a plan. Nothing is installed by an audit.',component:'Component',target:'Target folder',action:'Action',exactPlan:'Exact plan identity',planIdentityHelp:'Approval applies to these exact audited bytes. A changed plan must be audited again.',installEyebrow:'03 · APPLY, THEN OBSERVE',installTitle:'Install your reviewed toolkit',installHelp:'The existing updater saves a recovery journal. The installer preserves unrelated skills, project work and supported local settings.',approval:'I reviewed this plan and approve these installation changes.',installButton:'Install reviewed plan',verifyButton:'Verify files',discoverButton:'Check in Codex',discoveryHelp:'File verification checks the installed bytes. Discovery asks a fresh Codex host which skills it can actually see. A completed model task is a separate result.',beginEyebrow:'04 · MAKE ONE USEFUL CHANGE',beginTitle:'Start with a safe practice task',beginHelp:'Create a new, separate practice folder. Use your own Codex account to correct a heading and preserve an existing note.',practiceButton:'Create practice project',openFolder:'Open folder',practiceLocation:'New practice folder',practiceInstructions:'Open this folder with the generated Codex launcher, then paste the prompt below. Compare README.md and notes.txt before accepting the result.',copyPrompt:'Copy prompt',taskNotExecuted:'Prepared only. The installer has not run a model or claimed a completed task.',included:'THE CONNECTED TOOLKIT',teamTitle:'Keep the full system.',skills:'Core skills',skillsNote:'App · ChatBot · Game · constructors',orchestratorNote:'One coordinating conversation',roles:'Specialist roles',rolesNote:'Native profile and role registration',maintenanceNote:'Repository maintenance remains a separate owner tool. Model subscriptions and external APIs use your own accounts.',recoveryTitle:'Continue or recover',refresh:'Refresh',recoveryHelp:'The engine reads its own checked journals. No interrupted action is replayed automatically.',selectOperation:'Installation history',noOperation:'No checked operation yet',resumeButton:'Continue interrupted setup',rollbackButton:'Roll back selected install',uninstallButton:'Uninstall owned files',technicalDetails:'Details and receipts',targetHome:'Selected user home',statePath:'Journals and recovery',source:'Source commit',independent:'Independent toolkit compatible with Codex.',footerNote:'This installer stays on this computer. Your acquired license, model account and project data have separate scopes.',closeSetup:'Close local setup',reviewAction:'REVIEW THIS ACTION',cancel:'Cancel',confirm:'Confirm',checking:'Checking this computer',auditing:'Preparing a real audit',installing:'Applying your reviewed plan',verifying:'Verifying installed files',discovering:'Asking a fresh Codex host',resuming:'Continuing the checked journal',rollingback:'Rolling back the selected installation',uninstalling:'Removing owned files',refreshing:'Reading installation journals',preparing:'Preparing a separate practice project',opening:'Opening the practice folder',working:'The engine is running this operation. Its actual receipt will appear when it finishes; no estimated percentage is shown.',ready:'Ready',needsAction:'Needs attention',host:'Codex host',localSkills:'Local skills',profileRoles:'Profile and roles',workbench:'Workbench',includedSeparate:'Included separately; use its launcher',includedReady:'Resources included',supported:'Supported local platform',signedOut:'Sign-in or host setup required',hostReady:'Host and account ready',unknown:'Not yet observed',fresh:'New installation',knownCurrent:'Already current',update:'Update',partial:'Partial installation',auditReady:'Ready for your review',auditBlocked:'Resolve the listed conflicts first',planCount:'33 skills + Orchestrator + profile and 12 roles',conflictsTitle:'Installation is held:',preservedTitle:'Preserved local changes:',completed:'Operation finished',blocked:'Needs your attention',filesVerified:'Files verified',installed:'Toolkit installed',nativeVerified:'Native discovery verified',skillsSeen:'skills found from the expected installed paths',notModelRun:'A model task has not been executed by setup.',copied:'Prompt copied',copyFallback:'Select and copy the prompt below.',sessionFailed:'Reopen the local installer launcher to authorize this browser window.',closed:'Local setup stopped. You can close this tab.',rollbackTitle:'Roll back this installation?',rollbackCopy:'The engine will use the selected checked journal. Later unknown changes block the operation. Existing projects are preserved.',uninstallTitle:'Uninstall owned toolkit files?',uninstallCopy:'The engine removes only files owned by this installation. Your projects, unrelated skills and later local changes remain protected.',resumeTitle:'Continue this interrupted operation?',resumeCopy:'The engine resumes the exact retained plan and journal. It does not start a new installation or blindly replay an unknown external effect.',installedHistory:'Selected operation',noAutoReplay:'A retained operation needs review; nothing was resumed automatically.',operationPhase:'Phase',firstTaskPrepared:'Practice project prepared',sourceNotVerified:'Package identity will be checked by the engine.',installCheck:'Review and approve the current plan first.',privateHelp:'Use the generated Codex launcher so the recorded role configuration is active.',openCodex:'Open Codex for this project',openingCodex:'Opening the owned project launcher',codexHelp:'Install Codex or sign in with your own account',includedStatus:'Included',separateStatus:'Separate launch',allActions:'All component actions',action_install:'install',action_noop:'keep unchanged',action_upgrade:'update',action_update:'update',action_merge:'merge approved profile',genericFailure:'The local request could not be completed. Refresh the checked journals before retrying a change.',
 },
 uk: {
 technicalEdition:'Технічний випуск',
 setupLabel:'ЛОКАЛЬНИЙ МАЙСТЕР',language:'Мова',eyebrow:'ВАША КОМАНДА НА ВАШОМУ КОМП’ЮТЕРІ',title:'Одне встановлення.\nЦілий інструментарій.',intro:'Установіть навички, координатора й ролі. Збережіть власні проєкти, локальні зміни та шлях відновлення.',receivedPackage:'Отриманий комплект',localOnly:'Локальний майстер · без cloud-акаунта для setup',stepCheck:'Перевірити',stepCheckNote:'Цей комп’ютер',stepReview:'Переглянути',stepReviewNote:'Точні зміни',stepInstall:'Установити',stepInstallNote:'Потім звірити',stepBegin:'Почати',stepBeginNote:'Корисна задача',checkEyebrow:'01 · З’ЯСУЙТЕ ГОТОВНІСТЬ',checkTitle:'Перевірте цей комп’ютер',checkButton:'Перевірити',checkHelp:'Майстер перевіряє пакет, систему й Codex. Вхід у Codex відокремлений від встановлення локальних файлів.',notChecked:'Ще не перевірено',reviewEyebrow:'02 · ВАШІ ФАЙЛИ ЗАЛИШАЮТЬСЯ ВАШИМИ',reviewTitle:'Перегляньте точний план',auditButton:'Підготувати план',reviewHelp:'Аудит показує цільові папки й потрібні зміни. Незнайомі локальні правки залишаються для розгляду, а не перезаписуються.',auditEmpty:'Перевірте комп’ютер, потім підготуйте план. Сам аудит не встановлює компоненти.',component:'Компонент',target:'Цільова папка',action:'Дія',exactPlan:'Точний ідентифікатор плану',planIdentityHelp:'Підтвердження стосується саме цих перевірених байтів. Змінений план потрібно перевірити знову.',installEyebrow:'03 · ЗАСТОСУЙТЕ ТА ПЕРЕВІРТЕ',installTitle:'Установіть перевірений комплект',installHelp:'Чинний updater зберігає журнал відновлення. Майстер зберігає сторонні навички, проєкти й підтримувані локальні налаштування.',approval:'Я переглянув цей план і підтверджую зазначені зміни встановлення.',installButton:'Установити за планом',verifyButton:'Звірити файли',discoverButton:'Перевірити в Codex',discoveryHelp:'Звірка файлів перевіряє встановлені байти. Discovery запитує свіжий Codex, які навички він фактично бачить. Виконана модельна задача — окремий результат.',beginEyebrow:'04 · ОДНА КОРИСНА ЗМІНА',beginTitle:'Почніть із безпечної пробної задачі',beginHelp:'Створіть нову окрему пробну папку. Через власний акаунт Codex виправте заголовок і збережіть наявну нотатку.',practiceButton:'Створити пробний проєкт',openFolder:'Відкрити папку',practiceLocation:'Нова пробна папка',practiceInstructions:'Відкрийте цю папку згенерованим launcher Codex і вставте запит нижче. Звірте README.md та notes.txt перед прийняттям результату.',copyPrompt:'Копіювати запит',taskNotExecuted:'Лише підготовлено. Майстер не запускав модель і не заявляє завершення задачі.',included:'ПОВ’ЯЗАНИЙ ІНСТРУМЕНТАРІЙ',teamTitle:'Збережіть усю систему.',skills:'Основні навички',skillsNote:'App · ChatBot · Game · конструктори',orchestratorNote:'Одна координуюча розмова',roles:'Ролі спеціалістів',rolesNote:'Профіль і native-реєстрація ролей',maintenanceNote:'Maintenance залишається окремим інструментом власника репозиторію. Моделі й зовнішні API використовують ваші акаунти.',recoveryTitle:'Продовжити або відновити',refresh:'Оновити',recoveryHelp:'Двигун читає власні перевірені журнали. Перервана дія не повторюється автоматично.',selectOperation:'Історія встановлення',noOperation:'Перевірених операцій ще немає',resumeButton:'Продовжити перерву',rollbackButton:'Відкотити вибрану установку',uninstallButton:'Видалити керовані файли',technicalDetails:'Деталі та квитанції',targetHome:'Вибраний home користувача',statePath:'Журнали та відновлення',source:'Source commit',independent:'Незалежний інструмент, сумісний із Codex.',footerNote:'Майстер працює на цьому комп’ютері. Придбана ліцензія, модельний акаунт і дані проєкту мають окремі межі.',closeSetup:'Закрити локальний майстер',reviewAction:'ПЕРЕГЛЯНЬТЕ ЦЮ ДІЮ',cancel:'Скасувати',confirm:'Підтвердити',checking:'Перевіряємо цей комп’ютер',auditing:'Готуємо фактичний аудит',installing:'Застосовуємо перевірений план',verifying:'Звіряємо встановлені файли',discovering:'Запитуємо свіжий Codex',resuming:'Продовжуємо перевірений журнал',rollingback:'Відкочуємо вибрану установку',uninstalling:'Видаляємо керовані файли',refreshing:'Читаємо журнали встановлення',preparing:'Готуємо окремий пробний проєкт',opening:'Відкриваємо пробну папку',working:'Двигун виконує цю операцію. Фактична квитанція з’явиться після завершення; вигаданий відсоток не показується.',ready:'Готово',needsAction:'Потрібна увага',host:'Хост Codex',localSkills:'Локальні навички',profileRoles:'Профіль і ролі',workbench:'Робоча панель',includedSeparate:'Включено окремо; використайте її launcher',includedReady:'Ресурси включені',supported:'Локальна платформа підтримується',signedOut:'Потрібен вхід або налаштування хоста',hostReady:'Хост і акаунт готові',unknown:'Ще не спостерігалося',fresh:'Нова установка',knownCurrent:'Уже актуально',update:'Оновлення',partial:'Часткова установка',auditReady:'Готово до вашого перегляду',auditBlocked:'Спершу усуньте зазначені конфлікти',planCount:'33 навички + Orchestrator + профіль і 12 ролей',conflictsTitle:'Установлення призупинено:',preservedTitle:'Збережені локальні зміни:',completed:'Операція завершена',blocked:'Потрібна ваша увага',filesVerified:'Файли звірені',installed:'Комплект установлено',nativeVerified:'Native discovery перевірено',skillsSeen:'навичок знайдено за очікуваними шляхами',notModelRun:'Майстер не виконував модельної задачі.',copied:'Запит скопійовано',copyFallback:'Виділіть і скопіюйте запит нижче.',sessionFailed:'Відкрийте локальний launcher майстра знову, щоб авторизувати це вікно браузера.',closed:'Локальний майстер зупинено. Цю вкладку можна закрити.',rollbackTitle:'Відкотити цю установку?',rollbackCopy:'Двигун використає вибраний перевірений журнал. Пізніші незнайомі зміни блокують дію. Наявні проєкти зберігаються.',uninstallTitle:'Видалити керовані файли комплекту?',uninstallCopy:'Двигун видаляє лише файли цієї установки. Проєкти, сторонні навички та пізніші локальні правки залишаються захищеними.',resumeTitle:'Продовжити цю перервану дію?',resumeCopy:'Двигун продовжує точний збережений план і журнал. Він не створює нову установку та не повторює сліпо невизначену зовнішню дію.',installedHistory:'Вибрана операція',noAutoReplay:'Збережена операція потребує перегляду; нічого не продовжувалося автоматично.',operationPhase:'Фаза',firstTaskPrepared:'Пробний проєкт підготовлено',sourceNotVerified:'Ідентифікатор пакета перевірить двигун.',installCheck:'Спершу перегляньте й підтвердьте актуальний план.',privateHelp:'Використайте згенерований launcher Codex, щоб працювала записана конфігурація ролей.',openCodex:'Відкрити Codex для цього проєкту',openingCodex:'Відкриваємо власний launcher проєкту',codexHelp:'Установіть Codex або увійдіть у свій акаунт',includedStatus:'Включено',separateStatus:'Окремий запуск',allActions:'Усі дії з компонентами',action_install:'установити',action_noop:'зберегти без змін',action_upgrade:'оновити',action_update:'оновити',action_merge:'об’єднати перевірений профіль',genericFailure:'Локальний запит не завершено. Перечитайте перевірені журнали перед повторенням змін.',
 },
};
Object.assign(dictionaries.en,{
 purchaseTitle:'Keep your purchase document · optional',purchaseHelp:'If you received a purchase confirmation or entitlement JSON from trusted delivery, choose it before preparing the plan. The original document stays private on this computer. Updates keep an existing purchase document automatically.',purchaseChoose:'Choose purchase document',purchaseTrust:'Keeping a document does not verify its signature, activate a purchase or grant new rights.',purchaseEmpty:'No document selected here. The technical installer works without one.',purchaseReady:'Document ready for the next plan',purchaseSelecting:'Keeping the selected document',purchaseInvalid:'Use a JSON purchase document of up to 256 KiB.',purchaseReview:'A new document clears the previous plan and approval. Prepare and review a new plan.'
});
Object.assign(dictionaries.uk,{
 purchaseTitle:'Збережіть документ покупки · необов’язково',purchaseHelp:'Якщо довірена доставка видала JSON підтвердження покупки або entitlement, виберіть його перед підготовкою плану. Оригінал залишається приватним на цьому комп’ютері. Під час оновлення наявний документ покупки зберігається автоматично.',purchaseChoose:'Вибрати документ покупки',purchaseTrust:'Збереження документа не перевіряє його підпис, не активує покупку й не надає нових прав.',purchaseEmpty:'У цьому вікні документ ще не вибрано. Технічний установник працює без нього.',purchaseReady:'Документ готовий для нового плану',purchaseSelecting:'Зберігаємо вибраний документ',purchaseInvalid:'Виберіть JSON документа покупки обсягом до 256 КіБ.',purchaseReview:'Новий документ скасовує попередній план і підтвердження. Підготуйте та перегляньте новий план.'
});
const LOCALES = new Set(['en', 'uk']);
let legacyLocale;
try { legacyLocale = localStorage.getItem('agent-system-setup-locale'); } catch {}
let locale = LOCALES.has(legacyLocale) ? legacyLocale : 'en';
let savingLocale = false;
let csrf, state, selectedPlan, selectedOperation = '', busy = true, lastReceipt, lastJobStatus, practiceId, currentJob;
const SESSION_CSRF_KEY = 'codex-agent-system-setup-csrf';
try { csrf = sessionStorage.getItem(SESSION_CSRF_KEY) || undefined; } catch {}
const actionLabel = action => dictionaries[locale]['action_'+action] || action || '—';
const t = key => dictionaries[locale][key] ?? dictionaries.en[key] ?? key;
const receiptSummary = receipt => receipt?.status === 'prepared' && receipt?.execution_performed === false && receipt?.project ? t('practiceInstructions') : receipt?.reason || receipt?.next || receipt?.status;
const phases = { 'purchase-document':'purchaseSelecting',doctor:'checking',audit:'auditing',install:'installing',verify:'verifying',discover:'discovering',resume:'resuming',rollback:'rollingback',uninstall:'uninstalling',refresh:'refreshing',practice:'preparing','first-task':'preparing','open-practice':'opening','open-codex':'openingCodex' };
const actionNames = { skills:'skills',orchestrator:'Atelier Orchestrator','profile-and-roles':'profileRoles',profile:'profileRoles',roles:'roles' };
const create = (tag, value, className) => { const node = document.createElement(tag); if (value !== undefined) text(node, value); if (className) node.className = className; return node; };
function translated() {
 document.documentElement.lang = locale; $('locale').value = locale;
 $('locale').setAttribute('aria-label', t('language'));
 for (const node of document.querySelectorAll('[data-t]')) {
  const value = t(node.dataset.t); node.replaceChildren();
  const lines = value.split('\n'); lines.forEach((line, index) => { if (index) node.append(document.createElement('br')); node.append(document.createTextNode(line)); });
 }
 if (state) render();
}
async function request(path, options = {}) {
 const response = await fetch(path, { credentials:'same-origin',...options,headers:{...(options.body ? {'Content-Type':'application/json'} : {}),...(csrf ? {'X-Setup-Csrf':csrf} : {}),...options.headers} });
 let result; try { result = await response.json(); } catch { throw new Error(t('genericFailure')); }
 if (!response.ok) throw Object.assign(new Error(result.reason || result.message || t('genericFailure')), { result, status:response.status });
 return result;
}
function showError(error) { $('result-banner').hidden = false; $('result-banner').className = 'notice danger'; text($('result-banner'), error.message || t('genericFailure')); }
function card(title, description, ready = true, statusLabel) { const node = create('div',undefined,'readiness'+(ready?'':' needs')); node.append(create('strong',title),create('span',description),create('span',statusLabel || (ready?t('ready'):t('needsAction')),'status')); return node; }
function operation() { return state?.operations?.find(row => row.id === selectedOperation); }
function renderReadiness() {
 const doctor = state.results?.doctor; if (!doctor) return;
 const rows = [card(t('localSkills'),doctor.platform?.supported_skills?t('supported'):doctor.next,doctor.platform?.supported_skills === true),card(t('host'),doctor.host?.ready?t('hostReady'):(doctor.host?.next || t('signedOut')),doctor.host?.ready === true),card(t('profileRoles'),t('includedReady'),doctor.components?.profile_and_roles?.included === true,t('includedStatus')),card(t('workbench'),doctor.components?.workbench?.next || t('includedSeparate'),false,t('separateStatus'))];
 $('readiness').replaceChildren(...rows); text($('doctor-next'),doctor.next); text($('computer'),[doctor.platform?.os,doctor.platform?.architecture,'Python '+(doctor.platform?.python || '')].filter(Boolean).join(' · '));
}
function renderAudit() {
 const receipt = state.results?.audit;
 $('audit-empty').hidden = !!receipt?.plan_id; $('audit-preview').hidden = !receipt?.plan_id;
 if (!receipt?.plan_id) return;
 if (selectedPlan !== receipt.plan_id) { selectedPlan = receipt.plan_id; $('install-approval').checked = false; }
 text($('plan-sha'),receipt.plan_sha256); text($('plan-mode'),t(({fresh:'fresh','known-current':'knownCurrent',update:'update',partial:'partial'})[receipt.mode] || receipt.mode));
 text($('plan-summary'),receipt.status === 'ready' ? t('auditReady') : t('auditBlocked'));
 const components = receipt.preview?.components || [];
 const core = components.filter(row => !['atelier-orchestrator','orchestrator','profile-and-roles','profile','roles'].includes(row.id));
 const overview = [];
 if (core.length) {
  const counts = new Map(); for (const row of core) counts.set(row.action,(counts.get(row.action)||0)+1);
  overview.push(cardReceipt(`${core.length} ${t('skills').toLowerCase()}`, `${receipt.destination || ''} · ${[...counts].map(([action,count])=>`${count} ${actionLabel(action)}`).join(', ')}`));
 }
 for (const row of components.filter(row => !core.includes(row))) overview.push(cardReceipt(row.id==='atelier-orchestrator'?'Atelier Orchestrator':t(actionNames[row.id]||row.id), `${row.target || ''} · ${actionLabel(row.action)}`));
 $('plan-overview').replaceChildren(...overview); text($('component-actions-label'),`${t('allActions')} (${components.length})`);
 $('plan-components').replaceChildren(...components.map(row => { const tr = create('tr'); tr.append(create('td',t(actionNames[row.id] || row.id)),create('td',row.target || '—'),create('td',actionLabel(row.action))); return tr; }));
 const conflicts = receipt.preview?.conflicts || receipt.blockers || []; $('conflicts').hidden = !conflicts.length;
 if (conflicts.length) { $('conflicts').replaceChildren(create('div',t('conflictsTitle')),...conflicts.map(row => create('p',typeof row === 'string'?row:JSON.stringify(row)))); }
 const preserved = receipt.preview?.preserved_changes || []; $('preserved').hidden = !preserved.length;
 if (preserved.length) $('preserved').replaceChildren(create('div',t('preservedTitle')),...preserved.map(row => create('p',typeof row === 'string'?row:JSON.stringify(row))));
}
function renderOperations() {
 const rows = state.operations || [];
 if (!rows.some(row => row.id === selectedOperation)) selectedOperation = rows.find(row => row.can_resume || row.resumable)?.id || rows.find(row => row.status === 'complete')?.id || rows.at(-1)?.id || '';
 const select = $('operation-select'); select.replaceChildren();
 if (!rows.length) { const empty = create('option',t('noOperation')); empty.value = ''; select.append(empty); }
 for (const row of rows) { const node = create('option',`${row.status || row.state || t('unknown')} · ${(row.source_commit || '').slice(0,8)}`); node.value = row.id; select.append(node); }
 select.value = selectedOperation;
 const selected = operation(); text($('operation-state'),selected ? `${t('operationPhase')}: ${selected.phase || selected.status}. ${selected.can_resume || selected.resumable ? t('noAutoReplay') : ''}` : '');
}
function renderReceipts() {
 const cards = [];
 const install = state.results?.install || state.results?.resume;
 if (install?.status === 'installed') cards.push(cardReceipt(t('installed'),t('privateHelp')));
 const verify = state.results?.verify || install?.verification;
 if (verify?.status === 'verified-files') cards.push(cardReceipt(t('filesVerified'),`${verify.skills ?? ''} ${t('skills').toLowerCase()} + Orchestrator`));
 const discovery = state.results?.discover;
 if (discovery?.status === 'native-discovery-verified') cards.push(cardReceipt(t('nativeVerified'),`${discovery.skills} ${t('skillsSeen')}. ${t('notModelRun')}`));
 $('installation-result').replaceChildren(...cards);
 const practice = state.results?.practice;
 if (practice?.project) {
  practiceId = practice.practice_id; $('practice-result').hidden = false; $('open-practice-button').hidden = false; $('open-codex-button').hidden = !practice.launcher;
  text($('practice-path'),practice.project); $('practice-prompt').value = `${locale === 'uk' ? 'Проєкт' : 'Project'}: ${practice.project}\n\n${practice.prompt || ''}`;
 }
}
function cardReceipt(title, description) { const node = create('div',undefined,'receipt-card'); node.append(create('strong',title),create('p',description)); return node; }
function enabled() {
 const known = operation(); const complete = known?.status === 'complete'; const audit = state?.results?.audit;
 $('check-button').disabled = busy; $('audit-button').disabled = busy || !state?.results?.doctor?.platform?.supported_skills;
 $('install-approval').disabled = busy || audit?.status !== 'ready' || !audit?.plan_id;
 $('install-button').disabled = busy || audit?.status !== 'ready' || !$('install-approval').checked;
 $('verify-button').disabled = busy || !complete; $('discover-button').disabled = busy || !complete;
 $('practice-button').disabled = busy || !complete; $('open-practice-button').disabled = busy || !practiceId; $('open-codex-button').disabled = busy || !complete || !state?.results?.practice?.launcher;
 $('resume-button').disabled = busy || !(known?.can_resume || known?.resumable);
 $('rollback-button').disabled = busy || !known; $('uninstall-button').disabled = busy || !known;
 $('refresh-button').disabled = busy; $('shutdown-button').disabled = busy; $('operation-select').disabled = busy;
 $('purchase-document-file').disabled = busy;
 $('purchase-document-choose').disabled = busy;
 $('locale').disabled = savingLocale || !state;
}
function render() {
 text($('package-version'),state.product?.version?`Codex Agent System ${state.product.version}`:'Codex Agent System'); text($('edition'),state.product?.edition === 'unassigned' ? t('technicalEdition') : state.product?.edition || '');
 text($('home-path'),state.home); text($('state-path'),state.state); text($('source-commit'),state.product?.source_commit || t('sourceNotVerified'));
 renderReadiness(); renderAudit(); renderOperations(); renderReceipts();
 const documentReady=state.purchase_document;
 text($('purchase-document-status'),documentReady?.status==='document-ready'?`${t('purchaseReady')} · ${documentReady.edition} · ${documentReady.purchased_product_major}.x`:t('purchaseEmpty'));
 const active = state.active_job; busy = !!active;
 $('job-banner').hidden = !active;
 if (active) { text($('job-title'),t(phases[active.action] || active.action)); text($('job-description'),active.attention || t('working')); }
 for (const id of ['check','review','install','begin']) $('step-'+id).classList.remove('active','complete');
 const stage = active ? ({doctor:'check',audit:'review',install:'install',resume:'install',verify:'install',discover:'install',practice:'begin','first-task':'begin'})[active.action] || 'check' : state.results?.practice ? 'begin' : state.results?.install || state.results?.verify ? 'install' : state.results?.audit ? 'review' : 'check';
 $('step-'+stage).classList.add('active'); if (state.results?.doctor) $('step-check').classList.add('complete'); if (state.results?.audit?.status==='ready') $('step-review').classList.add('complete'); if (state.results?.verify?.status==='verified-files' || state.results?.install?.verification?.status==='verified-files') $('step-install').classList.add('complete');
 $('result-banner').hidden = !!active || !lastReceipt;
 if (lastReceipt && !active) {
  text($('receipt-json'),JSON.stringify(lastReceipt,null,2));
  const needs = lastJobStatus === 'blocked' || ['blocked','action-required'].includes(lastReceipt.status);
  $('result-banner').hidden = false; $('result-banner').className = 'notice '+(needs?'warning':'success');
  text($('result-banner'),[needs?t('blocked'):t('completed'),receiptSummary(lastReceipt)].filter(Boolean).join(' — '));
 }
 enabled();
}
async function watch(jobId) {
 while (true) {
  await new Promise(ok => setTimeout(ok,450)); state = await request('/api/state'); render();
  const job = state.jobs.find(row => row.id === jobId);
  if (!job || job.status === 'running') continue;
  currentJob = undefined; lastReceipt = job.result; lastJobStatus = job.status; render();
  const receipt = job.result || {};
  $('result-banner').hidden = false;
  const blocked = job.status === 'blocked' || ['blocked','action-required'].includes(receipt.status);
  $('result-banner').className = 'notice '+(blocked?'warning':'success');
  text($('result-banner'),[blocked?t('blocked'):t('completed'),receiptSummary(receipt)].filter(Boolean).join(' — '));
  return receipt;
 }
}
async function action(name, extras = {}) {
 if (busy) return;
 $('result-banner').hidden = true; busy = true; enabled();
 try {
  const body = { action:name, locale,...extras };
  if (name === 'install') { body.plan_id = selectedPlan; body.approved = $('install-approval').checked; }
  if (['verify','discover','resume','rollback','uninstall'].includes(name)) body.operation_id = selectedOperation;
  if (['resume','rollback','uninstall'].includes(name)) body.approved = true;
  if (['open-practice','open-codex'].includes(name)) body.practice_id = practiceId;
  const reply = await request('/api/action',{method:'POST',body:JSON.stringify(body)});
  if (reply.status === 'stopped') { $('result-banner').hidden = false; $('result-banner').className = 'notice success'; text($('result-banner'),t('closed')); for(const button of document.querySelectorAll('button')) button.disabled = true; return; }
  currentJob = reply.job_id; state = await request('/api/state'); render(); return await watch(reply.job_id);
 } catch (error) { busy = false; enabled(); showError(error); }
}
async function keepPurchaseDocument() {
 if(busy)return;
 const file=$('purchase-document-file').files?.[0];if(!file)return;
 $('install-approval').checked=false;selectedPlan=undefined;busy=true;enabled();
 text($('purchase-document-status'),t('purchaseSelecting'));
 try{
  if(file.size<2||file.size>256*1024)throw Error(t('purchaseInvalid'));
  const bytes=new Uint8Array(await file.arrayBuffer());
  new TextDecoder('utf-8',{fatal:true}).decode(bytes);
  // Encode selected bytes, never a client filesystem path or filename.
  let binary='';for(let i=0;i<bytes.length;i+=8192)binary+=String.fromCharCode(...bytes.subarray(i,i+8192));
  const reply=await request('/api/purchase-document',{method:'POST',body:JSON.stringify({document_base64:btoa(binary)})});
  state=await request('/api/state');lastReceipt=reply;lastJobStatus='complete';render();
  $('result-banner').hidden=false;$('result-banner').className='notice success';text($('result-banner'),t('purchaseReview'));
 }catch(error){showError(error);try{state=await request('/api/state');render();showError(error)}catch{busy=false;enabled()}}
 finally{$('purchase-document-file').value='';busy=!!state?.active_job;enabled();}
}
$('purchase-document-file').addEventListener('change',()=>keepPurchaseDocument());
$('purchase-document-choose').addEventListener('click',()=>{$('purchase-document-file').click();});
function confirmAction(name) {
 const dialog = $('confirmation');
 text($('confirmation-title'),t(name+'Title')); text($('confirmation-copy'),t(name+'Copy')); text($('confirmation-target'),operation()?.journal_display || '');
 dialog.returnValue = ''; dialog.showModal(); dialog.addEventListener('close',()=>{if(dialog.returnValue==='confirm')action(name);},{once:true});
}
async function saveLocale(selected) {
 if (!LOCALES.has(selected)) return;
 savingLocale = true; enabled();
 try {
  const result = await request('/api/locale-preference',{method:'POST',body:JSON.stringify({locale:selected})});
  locale = result.preferred_locale; state.preferred_locale = locale;
  try { localStorage.removeItem('agent-system-setup-locale'); } catch {}
 } catch (error) { showError(error); }
 finally { savingLocale = false; translated(); }
}
$('locale').disabled = true;
$('locale').addEventListener('change',event=>saveLocale(event.target.value));
$('install-approval').addEventListener('change',enabled);
$('operation-select').addEventListener('change',event=>{selectedOperation=event.target.value;renderOperations();enabled();});
for(const button of document.querySelectorAll('[data-action]'))button.addEventListener('click',()=>{const name=button.dataset.action;if(['resume','rollback','uninstall'].includes(name))confirmAction(name);else action(name);});
$('copy-prompt').addEventListener('click',async()=>{try{await navigator.clipboard.writeText($('practice-prompt').value);text($('copy-status'),t('copied'))}catch{$('practice-prompt').focus();$('practice-prompt').select();text($('copy-status'),t('copyFallback'))}});
translated();
try {
 const params = new URLSearchParams(location.hash.slice(1)); const launch = params.get('launch');
 if(launch)history.replaceState(null,'',location.pathname);
 const result = launch ? await request('/api/session',{method:'POST',body:JSON.stringify({launch_token:launch})}) : await request('/api/session');
 csrf=result.csrf_token;try{sessionStorage.setItem(SESSION_CSRF_KEY,csrf)}catch{}state=await request('/api/state');
 if (LOCALES.has(state.preferred_locale)) locale = state.preferred_locale;
 else if (LOCALES.has(legacyLocale)) await saveLocale(legacyLocale);
 document.body.dataset.setupSession='ready';translated();
 if(state.active_job)watch(state.active_job.id).catch(showError);else await action('refresh');
} catch(error){$('session-error').hidden=false;text($('session-error'),`${t('sessionFailed')} ${error.message||''}`);for(const button of document.querySelectorAll('button[data-action]'))button.disabled=true;}
