document.addEventListener('DOMContentLoaded', () => {
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
            html += `<li class="${liClasses.join(' ')}" contenteditable="true">${medicalIcon}${sentenceText}</li>`;
        });
        html += '</ul>';
        improvedResultsElement.innerHTML = html;
        saveButtonContainer.style.display = 'block';
    }

    async function handleSave() {
        const editedItems = improvedResultsElement.querySelectorAll('li');
        const sentences = [];
        editedItems.forEach(item => {
            const text = item.querySelector('.medical-icon') ? item.innerText.replace('⚕️', '').trim() : item.innerText.trim();
            // This is a simplified save; we lose the metadata. A more complex implementation would preserve it.
            sentences.push({
                text: text,
                is_uncertain: item.classList.contains('uncertain-sentence'),
                has_medical_terminology: !!item.querySelector('.medical-icon'),
                specific_uncertain_word: Array.from(item.querySelectorAll('.uncertain-word')).map(el => el.textContent)
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