document.addEventListener('DOMContentLoaded', () => {
    // --- Manuscript Elements ---
    const manuscriptTopicInput = document.getElementById('manuscriptTopic');
    const generateManuscriptButton = document.getElementById('generateManuscriptButton');
    const manuscriptOutputElement = document.getElementById('manuscriptOutput');

    // --- Transcription Elements ---
    const audioFileInput = document.getElementById('audioFileInput');
    const statusElement = document.getElementById('status');
    const jobListElement = document.getElementById('jobList');
    const detailsSection = document.getElementById('detailsSection');
    const resultsElement = document.getElementById('results');
    const improveSection = document.getElementById('improveSection');
    const improveButton = document.getElementById('improveButton');
    const improvedResultsElement = document.getElementById('improvedResults');
    const saveButtonContainer = document.getElementById('saveButtonContainer');
    const saveButton = document.getElementById('saveButton');

    let currentTranscriptId = null;
    let pollingInterval = null;

    // --- Manuscript Event Listener ---
    generateManuscriptButton.addEventListener('click', async () => {
        const topic = manuscriptTopicInput.value;
        if (!topic) {
            alert('Please enter a topic.');
            return;
        }

        manuscriptOutputElement.style.display = 'block';
        manuscriptOutputElement.innerHTML = '<div class="loader"></div><p>Generating manuscript...</p>';

        try {
            const response = await fetch('/manuscript', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ topic: topic }),
            });

            if (!response.ok) {
                throw new Error(`Server error: ${response.statusText}`);
            }

            const data = await response.json();
            manuscriptOutputElement.innerHTML = `
                <h3>${data.title}</h3>
                <p>${data.prose.replace(/\n/g, '<br>')}</p>
                <h4>Key Takeaways:</h4>
                <ul>
                    ${data.key_takeaways.map(item => `<li>${item}</li>`).join('')}
                </ul>
            `;
        } catch (error) {
            manuscriptOutputElement.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
        }
    });


    // --- Initial Load ---
    async function loadJobs() {
        const response = await fetch('/transcripts');
        const jobs = await response.json();
        jobListElement.innerHTML = '';
        jobs.forEach(job => {
            const li = document.createElement('li');
            li.textContent = `${job.original_filename} - ${job.status} - ${new Date(job.created_at).toLocaleString()}`;
            li.dataset.id = job.id;
            li.classList.add('job-item');
            if (job.status === 'processing') {
                li.style.color = 'gray';
            }
            jobListElement.appendChild(li);
        });
    }

    // --- Event Listeners ---
    audioFileInput.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            statusElement.textContent = `Uploading ${file.name}...`;
            uploadAndStartTranscription(file);
        }
    });

    jobListElement.addEventListener('click', (event) => {
        if (event.target.matches('.job-item')) {
            // Clear previous selection
            document.querySelectorAll('.job-item.selected').forEach(el => el.classList.remove('selected'));
            event.target.classList.add('selected');
            
            const id = event.target.dataset.id;
            loadTranscriptDetails(id);
        }
    });

    improveButton.addEventListener('click', handleImprove);
    saveButton.addEventListener('click', handleSave);

    // --- Core Functions ---
    async function uploadAndStartTranscription(file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/transcripts', { method: 'POST', body: formData });
        const data = await response.json();
        
        statusElement.textContent = `Job ${data.transcript_id} started. Processing...`;
        await loadJobs(); // Refresh the job list
    }

    async function loadTranscriptDetails(id) {
        if (pollingInterval) clearInterval(pollingInterval);
        currentTranscriptId = id;
        detailsSection.style.display = 'block';
        resultsElement.innerHTML = '<div class="loader"></div>';
        improveSection.style.display = 'none';

        const poll = async () => {
            const response = await fetch(`/transcripts/${id}`);
            const data = await response.json();

            if (data.status === 'completed') {
                clearInterval(pollingInterval);
                statusElement.textContent = 'Job loaded.';
                displayTranscriptDetails(data);
                await loadJobs(); // Refresh list to show completed status
            } else {
                statusElement.textContent = `Job ${id} is still processing...`;
            }
        };
        
        pollingInterval = setInterval(poll, 3000);
        poll(); // Initial call
    }

    function displayTranscriptDetails(data) {
        resultsElement.innerHTML = `
            <h3>Whisper Transcription:</h3>
            <p>${data.whisper_transcript || 'N/A'}</p>
            <hr>
            <h3>Corti Transcription:</h3>
            <p>${data.corti_transcript || 'N/A'}</p>
        `;
        improveSection.style.display = 'block';

        if (data.improved_transcript) {
            renderImprovedTranscript(data.improved_transcript);
        } else {
            improvedResultsElement.innerHTML = '';
            saveButtonContainer.style.display = 'none';
        }
    }

    async function handleImprove() {
        improvedResultsElement.innerHTML = '<div class="loader"></div><p>Asking the AI to improve the transcript...</p>';
        
        const detailsResponse = await fetch(`/transcripts/${currentTranscriptId}`);
        const transcriptData = await detailsResponse.json();

        const improveResponse = await fetch('/improve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                whisper_transcription: transcriptData.whisper_transcript,
                corti_transcription: transcriptData.corti_transcript,
            }),
        });
        const improvedData = await improveResponse.json();
        renderImprovedTranscript(improvedData);
    }

    function renderImprovedTranscript(data) {
        let html = '<ul>';
        data.sentences.forEach(sentence => {
            let sentenceText = sentence.text;
            let liClasses = [];
            if (sentence.specific_uncertain_word && sentence.specific_uncertain_word.length > 0) {
                sentence.specific_uncertain_word.forEach(word => {
                    const regex = new RegExp(`\\b(${word})\\b`, 'gi');
                    sentenceText = sentenceText.replace(regex, `<span class="uncertain-word">$1</span>`);
                });
            }
            const medicalIcon = sentence.has_medical_terminology ? '<span class="medical-icon">⚕️</span>' : '';
            if (sentence.is_uncertain) liClasses.push('uncertain-sentence');

            // --- Create Labels ---
            const medLabel = sentence.best_model_for_medical_terminology;
            const speechLabel = sentence.best_everyday_speech;
            
            const labelsHtml = `
                <div class="labels-container">
                    <span class="label ${medLabel.toLowerCase()}" data-type="med" data-value="${medLabel}">Med: ${medLabel}</span>
                    <span class="label ${speechLabel.toLowerCase()}" data-type="speech" data-value="${speechLabel}">Speech: ${speechLabel}</span>
                </div>
            `;

            html += `<li class="${liClasses.join(' ')}">
                        <div class="sentence-container">
                            <div class="sentence-text" contenteditable="true">${medicalIcon}${sentenceText}</div>
                            ${labelsHtml}
                        </div>
                     </li>`;
        });
        html += '</ul>';
        improvedResultsElement.innerHTML = html;
        saveButtonContainer.style.display = 'block';
    }

    async function handleSave() {
        const editedItems = improvedResultsElement.querySelectorAll('li');
        const sentences = [];
        editedItems.forEach(item => {
            const sentenceTextElement = item.querySelector('.sentence-text');
            const text = sentenceTextElement.innerText.trim();
            
            // --- Read Labels Back ---
            const medLabel = item.querySelector('[data-type="med"]').dataset.value;
            const speechLabel = item.querySelector('[data-type="speech"]').dataset.value;

            sentences.push({
                text: text,
                is_uncertain: sentenceTextElement.classList.contains('uncertain-sentence'),
                has_medical_terminology: !!sentenceTextElement.querySelector('.medical-icon'),
                specific_uncertain_word: Array.from(sentenceTextElement.querySelectorAll('.uncertain-word')).map(el => el.textContent),
                best_model_for_medical_terminology: medLabel,
                best_everyday_speech: speechLabel
            });
        });

        const payload = { improved_transcript: { sentences: sentences } };
        
        await fetch(`/transcripts/${currentTranscriptId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });

        const originalButtonText = saveButton.textContent;
        saveButton.textContent = 'Saved!';
        setTimeout(() => { saveButton.textContent = originalButtonText; }, 2000);
    }

    // --- Initial Load ---
    loadJobs();
});