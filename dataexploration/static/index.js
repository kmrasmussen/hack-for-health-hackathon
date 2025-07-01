document.addEventListener('DOMContentLoaded', () => {
    const recordButton = document.getElementById('recordButton');
    const stopButton = document.getElementById('stopButton');
    const audioFileInput = document.getElementById('audioFileInput');
    const statusElement = document.getElementById('status');
    const resultsElement = document.getElementById('results');

    let mediaRecorder;
    let audioChunks = [];

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
        })
        .catch(error => {
            console.error('Error:', error);
            resultsElement.innerHTML = `<p style="color: red;">An error occurred: ${error.message}</p>`;
            statusElement.textContent = 'An error occurred.';
        });
    }
});