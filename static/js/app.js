 function cameraApp(toggleCameraUrl, toggleRecognitionUrl, startRecognitionLoopUrl) {
        return {
            isCameraOn: false,
            isFaceRecognitionEnabled: false,
            employeeDetected: false,
            employee: {},
            toggleCamera() {
                this.isCameraOn = !this.isCameraOn;
                fetch(toggleCameraUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': '{{ csrf_token }}'
                    },
                    body: JSON.stringify({ isCameraOn: this.isCameraOn })
                });
            },
            toggleRecognition() {
                console.log("Current recognition state before toggle:", this.isFaceRecognitionEnabled);
                //this.isFaceRecognitionEnabled = !this.isFaceRecognitionEnabled;
                console.log("New recognition state after toggle:", this.isFaceRecognitionEnabled);

                fetch(toggleRecognitionUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': '{{ csrf_token }}'
                    },
                    body: JSON.stringify({ recognitionEnabled: this.isFaceRecognitionEnabled })
                }).then(() => {

                        this.startRecognitionLoop();

                });
            },
            startRecognitionLoop() {
                console.log(`Recognition_enabled: ${this.isFaceRecognitionEnabled}`)
                if (this.isFaceRecognitionEnabled && this.isCameraOn) {
                    fetch(startRecognitionLoopUrl, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': '{{ csrf_token }}'
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        console.log('data: ', data.employees)
                        if (data.success && data.employees.length > 0) {
                            this.employeeDetected = true;

                            this.employee = data.employees[0];
                            console.log('this.employee: ', this.employee)
                        } else {
                            this.employeeDetected = false;
                        }
                        if (this.isCameraOn) {
                            setTimeout(() => this.startRecognitionLoop(), 500);  // Adjust the interval as needed
                        }
                    })
                    .catch(error => console.error('Error:', error));
                }
            }
        }
    }