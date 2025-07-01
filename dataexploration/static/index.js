document.addEventListener('DOMContentLoaded', () => {
    const recordButton = document.getElementById('recordButton');
    const stopButton = document.getElementById('stopButton');
    const audioFileInput = document.getElementById('audioFileInput');
    const statusElement = document.getElementById('status');
    const resultsElement = document.getElementById('results');
    const improveSection = document.getElementById('improveSection');
    const improveButton = document.getElementById('improveButton');
    const improvedResultsElement = document.getElementById('improvedResults');
    const saveButtonContainer = document.getElementById('saveButtonContainer');
    const saveButton = document.getElementById('saveButton');

    let mediaRecorder;
    let audioChunks = [];
    let currentTranscripts = {}; // To store transcripts for the improve call

    // --- Recording Logic ---
    recordButton.addEventListener('click', async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            
            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                sendAudioForTranscription(audioBlob, 'recording.wav');
                audioChunks = [];
            };

            mediaRecorder.start();
            statusElement.textContent = 'Recording...';
            recordButton.disabled = true;
            stopButton.disabled = false;
        } catch (error) {
            statusElement.textContent = 'Error accessing microphone: ' + error.message;
            console.error('Error accessing microphone:', error);
        }
    });

    stopButton.addEventListener('click', () => {
        mediaRecorder.stop();
        statusElement.textContent = 'Recording stopped. Transcribing...';
        recordButton.disabled = false;
        stopButton.disabled = true;
    });

    // --- File Upload Logic ---
    audioFileInput.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            statusElement.textContent = `File selected: ${file.name}. Transcribing...`;
            sendAudioForTranscription(file, file.name);
        }
    });

    // --- API Communication ---
    function sendAudioForTranscription(audioData, fileName) {
        const formData = new FormData();
        formData.append('file', audioData, fileName);

        resultsElement.innerHTML = '<div class="loader"></div><p>Processing... this may take a moment.</p>';
        improveSection.style.display = 'none'; // Hide improve section during new transcription
        improvedResultsElement.innerHTML = '';

        fetch('/transcribe', {
            method: 'POST',
            body: formData,
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            resultsElement.innerHTML = `
                <h3>Whisper Transcription:</h3>
                <p>${data.whisper_transcription}</p>
                <hr>
                <h3>Corti Transcription:</h3>
                <p>${data.corti_transcription}</p>
            `;
            statusElement.textContent = 'Transcription complete.';
            
            // Store results and show the improve button
            currentTranscripts = data;
            improveSection.style.display = 'block';
        })
        .catch(error => {
            console.error('Error:', error);
            resultsElement.innerHTML = `<p style="color: red;">An error occurred: ${error.message}</p>`;
            statusElement.textContent = 'An error occurred.';
        });
    }

    // --- Improve Transcript Logic ---
    improveButton.addEventListener('click', () => {
        improvedResultsElement.innerHTML = '<div class="loader"></div><p>Asking the AI to improve the transcript...</p>';
        saveButtonContainer.style.display = 'none'; // Hide save button during processing
        
        fetch('/improve', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(currentTranscripts),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            
            let html = '<ul>';
            data.sentences.forEach(sentence => {
                let sentenceText = sentence.text;
                let liClasses = [];

                // Highlight specific uncertain words by wrapping them in a span with a class
                if (sentence.specific_uncertain_word && sentence.specific_uncertain_word.length > 0) {
                    sentence.specific_uncertain_word.forEach(word => {
                        const regex = new RegExp(`\\b(${word})\\b`, 'gi');
                        sentenceText = sentenceText.replace(regex, `<span class="uncertain-word">$1</span>`);
                    });
                }

                // Add a medical icon span if applicable
                const medicalIcon = sentence.has_medical_terminology ? '<span class="medical-icon">⚕️</span>' : '';
                
                // Add a class to the whole <li> if it's generally uncertain
                if (sentence.is_uncertain) {
                    liClasses.push('uncertain-sentence');
                }

                // Add contenteditable="true" to make the list item editable
                html += `<li class="${liClasses.join(' ')}" contenteditable="true">${medicalIcon}${sentenceText}</li>`;
            });
            html += '</ul>';
            
            improvedResultsElement.innerHTML = html;
            saveButtonContainer.style.display = 'block'; // Show the save button
        })
        .catch(error => {
            console.error('Error improving transcript:', error);
            improvedResultsElement.innerHTML = `<p style="color: red;">An error occurred: ${error.message}</p>`;
        });
    });

    // --- Save Edits Logic ---
    saveButton.addEventListener('click', () => {
        const editedItems = improvedResultsElement.querySelectorAll('li');
        const finalTranscripts = [];

        console.log("--- User's Final Edits (Saved at " + new Date().toLocaleTimeString() + ") ---");
        editedItems.forEach(item => {
            // We no longer make the item non-editable.
            
            // Log the final text content, stripping out the icon if present
            const text = item.querySelector('.medical-icon') 
                ? item.innerText.replace('⚕️', '').trim() 
                : item.innerText.trim();
            
            finalTranscripts.push(text);
            console.log(text);
        });

        // Provide temporary feedback instead of disabling the button
        const originalButtonText = saveButton.textContent;
        saveButton.textContent = 'Saved!';
        statusElement.textContent = 'Current edits saved to console.';

        // Revert the button back to its original state after 2 seconds
        setTimeout(() => {
            saveButton.textContent = originalButtonText;
            statusElement.textContent = 'Ready to save again.';
        }, 2000);
    });
});