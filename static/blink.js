
const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const imageDataInput = document.getElementById("imageData");

Promise.all([
    faceapi.nets.tinyFaceDetector.loadFromUri('/static/models'),
    faceapi.nets.faceLandmark68TinyNet.loadFromUri('/static/models')
]).then(startCamera);

function startCamera() {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => video.srcObject = stream);
}

// Eye Aspect Ratio calculation
function eyeAspectRatio(eye) {
    const A = faceapi.euclideanDistance(eye[1], eye[5]);
    const B = faceapi.euclideanDistance(eye[2], eye[4]);
    const C = faceapi.euclideanDistance(eye[0], eye[3]);
    return (A + B) / (2.0 * C);
}

let blinkDetected = false;

video.addEventListener("play", () => {
    const interval = setInterval(async () => {
        const detection = await faceapi
            .detectSingleFace(video, new faceapi.TinyFaceDetectorOptions())
            .withFaceLandmarks(true);

        if (!detection) return;

        const leftEye = detection.landmarks.getLeftEye();
        const rightEye = detection.landmarks.getRightEye();

        const leftEAR = eyeAspectRatio(leftEye);
        const rightEAR = eyeAspectRatio(rightEye);
        const ear = (leftEAR + rightEAR) / 2;

        if (ear < 0.22 && !blinkDetected) {
            blinkDetected = true;
            capturePhoto();
            clearInterval(interval);
        }
    }, 200);
});

function capturePhoto() {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d").drawImage(video, 0, 0);

    const dataURL = canvas.toDataURL("image/jpeg");
    imageDataInput.value = dataURL;

    document.getElementById("captureForm").submit();
}
