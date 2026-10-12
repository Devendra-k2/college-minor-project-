const form = document.querySelector('#generate-form');
const topicInput = document.querySelector('#topic');
const generateButton = document.querySelector('#generate-button');
const output = document.querySelector('#email-output');
const translationOutput = document.querySelector('#translation-output');
const translationState = document.querySelector('#translation-state');
const statusMessage = document.querySelector('#status-message');
const sendButton = document.querySelector('#send-button');
const compareButton = document.querySelector('#compare-button');
const printButton = document.querySelector('#print-button');
const toneLabel = document.querySelector('#tone-label');
const wordCount = document.querySelector('#word-count');
const recipientInput = document.querySelector('#recipient');
const ccInput = document.querySelector('#cc');
const subjectInput = document.querySelector('#subject');
const dialog = document.querySelector('#compare-dialog');
const attachmentInput = document.querySelector('#attachment-input');
const attachmentList = document.querySelector('#attachment-list');
const attachmentSummary = document.querySelector('#attachment-summary');

let selectedTone = 'Formal Keigo';
let translatedText = '';
let translationSequence = 0;
let translationTimer;
let attachments = [];

function currentEmail() {
  return output.value.trim();
}

function updateActions() {
  const isTranslated = Boolean(currentEmail() && translatedText === currentEmail());
  const validRecipient = recipientInput.value.trim() && recipientInput.validity.valid;
  const validCc = !ccInput.value.trim() || ccInput.validity.valid;
  const validSubject = subjectInput.value.trim();

  if (sendButton) sendButton.disabled = !(isTranslated && validRecipient && validCc && validSubject);
  if (compareButton) compareButton.disabled = !isTranslated;
  if (printButton) printButton.disabled = !isTranslated;
}

function clearTranslation() {
  translationSequence += 1;
  translatedText = '';

  if (translationOutput) {
    translationOutput.textContent = '';
    translationOutput.innerHTML = '<p class="translation-placeholder">Your Japanese translation will appear here as you write.</p>';
  }

  if (translationState) {
    translationState.classList.remove('ready', 'loading');
    translationState.innerHTML = '<span></span> Waiting for draft';
  }

  const readyIndicator = document.querySelector('#ready-indicator');
  if (readyIndicator) readyIndicator.classList.remove('ready');

  const keigoLabel = document.querySelector('#keigo-label');
  if (keigoLabel) keigoLabel.textContent = 'Ready to review';

  updateActions();
}

async function translateCurrentEmail() {
  const email = currentEmail();
  if (!email) {
    clearTranslation();
    return false;
  }

  const requestId = ++translationSequence;
  translationState.classList.remove('ready');
  translationState.classList.add('loading');
  translationState.innerHTML = '<span></span> Translating';
  document.querySelector('#keigo-label').textContent = 'Preparing translation';
  statusMessage.textContent = '';

  try {
    const response = await fetch('/api/translate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Translation failed.');
    if (requestId !== translationSequence || currentEmail() !== email) return false;

    translatedText = email;
    translationOutput.textContent = data.translation;
    translationState.classList.remove('loading');
    translationState.classList.add('ready');
    translationState.innerHTML = '<span></span> Translation ready';
    document.querySelector('#ready-indicator').classList.add('ready');
    document.querySelector('#keigo-label').textContent = 'Ready to send';
    updateActions();
    return true;
  } catch (error) {
    if (requestId === translationSequence) {
      translationState.classList.remove('loading', 'ready');
      translationState.innerHTML = '<span></span> Translation unavailable';
      document.querySelector('#keigo-label').textContent = 'Review translation status';
      statusMessage.textContent = error.message;
    }
    updateActions();
    return false;
  }
}

function scheduleTranslation() {
  clearTimeout(translationTimer);
  if (statusMessage) {
    statusMessage.classList.remove('success');
    statusMessage.textContent = '';
  }

  const email = currentEmail();
  if (wordCount) {
    wordCount.textContent = `${email ? email.split(/\s+/).filter(Boolean).length : 0} words`;
  }

  clearTranslation();
  if (!email) return;

  if (translationState) {
    translationState.classList.add('loading');
    translationState.innerHTML = '<span></span> Translation queued';
  }

  translationTimer = setTimeout(translateCurrentEmail, 900);
}

if (form) {
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const topic = topicInput.value.trim();
    if (!topic) return;

    if (generateButton) {
      generateButton.disabled = true;
      const generateLabel = generateButton.querySelector('span');
      if (generateLabel) generateLabel.textContent = 'Drafting...';
    }

    if (statusMessage) statusMessage.textContent = '';
    clearTimeout(translationTimer);
    clearTranslation();

    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic, tone: selectedTone }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Email generation failed.');
      output.value = data.email;
      const draftStatus = document.querySelector('#draft-status');
      if (draftStatus) draftStatus.innerHTML = '<span></span> Draft ready';
      scheduleTranslation();
    } catch (error) {
      if (statusMessage) statusMessage.textContent = error.message;
    } finally {
      if (generateButton) {
        generateButton.disabled = false;
        const generateLabel = generateButton.querySelector('span');
        if (generateLabel) generateLabel.textContent = 'Draft email';
      }
    }
  });
}

output.addEventListener('input', () => {
  document.querySelector('#draft-status').innerHTML = '<span></span> Editing draft';
  scheduleTranslation();
});

document.querySelectorAll('.tone-pill').forEach((button) => {
  button.addEventListener('click', () => {
    selectedTone = button.dataset.tone;
    document.querySelectorAll('.tone-pill').forEach((pill) => {
      const active = pill === button;
      pill.classList.toggle('active', active);
      pill.setAttribute('aria-pressed', String(active));
    });
    toneLabel.textContent = selectedTone;
  });
});

document.querySelectorAll('.message-item').forEach((item) => {
  item.addEventListener('click', () => {
    document.querySelectorAll('.message-item').forEach((row) => row.classList.toggle('selected', row === item));
    topicInput.value = item.dataset.topic;
    recipientInput.value = item.dataset.to;
    subjectInput.value = item.dataset.subject;
    output.value = '';
    scheduleTranslation();
    document.querySelector('#draft-status').innerHTML = '<span></span> Message selected';
  });
});

document.querySelectorAll('.folder').forEach((folder) => {
  folder.addEventListener('click', () => {
    document.querySelectorAll('.folder').forEach((item) => item.classList.toggle('active', item === folder));
    const title = document.querySelector('#folder-title');
    title.textContent = folder.dataset.folder;
    if (folder.dataset.folder === 'Inbox') title.innerHTML = 'Inbox <span>14</span>';
  });
});

const messageSearch = document.querySelector('#message-search');
if (messageSearch) {
  messageSearch.addEventListener('input', (event) => {
    const query = event.target.value.trim().toLowerCase();
    document.querySelectorAll('.message-item').forEach((item) => {
      item.hidden = !item.textContent.toLowerCase().includes(query);
    });
  });
}

const newMessageButton = document.querySelector('#new-message-button');
if (newMessageButton) {
  newMessageButton.addEventListener('click', () => {
    topicInput.value = '';
    recipientInput.value = '';
    ccInput.value = '';
    subjectInput.value = '';
    output.value = '';
    if (statusMessage) statusMessage.textContent = '';
    scheduleTranslation();
    const draftStatus = document.querySelector('#draft-status');
    if (draftStatus) draftStatus.innerHTML = '<span></span> New draft';
    topicInput.focus();
  });
}

document.querySelectorAll('[data-format]').forEach((button) => {
  button.addEventListener('click', () => {
    const start = output.selectionStart;
    const end = output.selectionEnd;
    const selected = output.value.slice(start, end);
    const format = button.dataset.format;
    const replacement = format === 'bold' ? `**${selected || 'bold text'}**`
      : format === 'italic' ? `_${selected || 'italic text'}_`
        : `\n• ${selected || 'List item'}`;
    output.setRangeText(replacement, start, end, 'select');
    output.focus();
    output.dispatchEvent(new Event('input', { bubbles: true }));
  });
});

document.querySelector('#attach-button').addEventListener('click', () => attachmentInput.click());
attachmentInput.addEventListener('change', () => {
  attachments = [...attachmentInput.files];
  attachmentList.replaceChildren();
  attachments.forEach((file) => {
    const chip = document.createElement('span');
    chip.className = 'attachment-chip';
    chip.textContent = file.name;
    attachmentList.append(chip);
  });
  attachmentList.hidden = attachments.length === 0;
  attachmentSummary.textContent = attachments.length ? `${attachments.length} local attachment${attachments.length > 1 ? 's' : ''} (not sent)` : '';
});

sendButton.addEventListener('click', async () => {
  if (attachments.length) {
    statusMessage.textContent = 'Attachments are shown in this draft but are not supported by SMTP sending yet.';
    return;
  }
  sendButton.disabled = true;
  sendButton.innerHTML = '<span>&#8635;</span> Sending...';
  statusMessage.textContent = '';
  try {
    const response = await fetch('/api/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        recipient: recipientInput.value.trim(),
        cc: ccInput.value.trim(),
        subject: subjectInput.value.trim(),
        english: currentEmail(),
        japanese: translationOutput.textContent.trim(),
      }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.message || data.error || 'Email could not be sent.');
    statusMessage.classList.add('success');
    statusMessage.textContent = data.message;
    document.querySelector('#draft-status').innerHTML = '<span></span> Sent';
  } catch (error) {
    statusMessage.classList.remove('success');
    statusMessage.textContent = error.message;
  } finally {
    sendButton.innerHTML = '<span>&#9993;</span> Translate &amp; Send Directly';
    updateActions();
  }
});

if (compareButton) {
  compareButton.addEventListener('click', () => {
    const compareEnglish = document.querySelector('#compare-english');
    const compareJapanese = document.querySelector('#compare-japanese');
    const compareRecipient = document.querySelector('#compare-recipient');

    if (compareEnglish) compareEnglish.textContent = currentEmail();
    if (compareJapanese) compareJapanese.textContent = translationOutput ? translationOutput.textContent : '';
    if (compareRecipient) compareRecipient.textContent = `To: ${recipientInput.value} · ${subjectInput.value}`;

    if (dialog) dialog.showModal();
  });
}

const closeDialogButton = document.querySelector('#close-dialog');
if (closeDialogButton && dialog) closeDialogButton.addEventListener('click', () => dialog.close());

const dialogPrintButton = document.querySelector('#dialog-print');
if (dialogPrintButton) dialogPrintButton.addEventListener('click', () => window.print());

if (printButton) printButton.addEventListener('click', () => window.print());

[recipientInput, ccInput, subjectInput].forEach((input) => input && input.addEventListener('input', updateActions));