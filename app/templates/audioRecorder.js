document.addEventListener('DOMContentLoaded', () => {
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const audioPlayback = document.getElementById('audioPlayback');

    let mediaRecorder;
    let audioChunks = [];
    let startTime;

    startBtn.addEventListener('click', async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);

            mediaRecorder.ondataavailable = (event) => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                audioChunks = [];
                
                audioPlayback.src = URL.createObjectURL(audioBlob);

                // Calculate audio duration
                const duration = (Date.now() - startTime) / 1000; // in seconds
                console.log(`Audio Duration: ${duration} seconds`);


                // Send audioBlob to backend
                const formData = new FormData();
                formData.append('audio', audioBlob, 'recording.webm');
                await fetch('/upload-audio', {
                    method: 'POST',
                    body: formData,
                });
            };

            mediaRecorder.start();
            startTime = Date.now(); 
            startBtn.disabled = true;
            stopBtn.disabled = false;
        } catch (error) {
            console.error('Error accessing microphone:', error);
        }
    });

    stopBtn.addEventListener('click', () => {
        mediaRecorder.stop();
        startBtn.disabled = false;
        stopBtn.disabled = true;
    });
});
