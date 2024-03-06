document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('browseBtn').addEventListener('click', function() {
        document.getElementById('fileInput').click();
    });

    document.getElementById('fileInput').addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                const img = new Image();
                img.onload = function() {
                    document.getElementById('imagePreview').style.width = img.naturalWidth + 'px';
                    document.getElementById('imagePreview').style.height = img.naturalHeight + 'px';
                    document.getElementById('imagePreview').style.backgroundImage = `url(${e.target.result})`;
                };
                img.src = e.target.result;
            }
            reader.readAsDataURL(file);
        }
    });

    document.getElementById('detectBtn').addEventListener('click', function() {
        const formData = new FormData();
        formData.append('image', document.getElementById('fileInput').files[0]);

        document.getElementById('loader').style.display = 'block'; // Show loader

        fetch('/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            displayFlashMessages(data.flash_messages);
            const file_path = data.file_path;
            const filename = data.filename;
            fetch(`/detect_disease/${file_path}/${filename}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('loader').style.display = 'none'; // Hide loader
                displayFlashMessages(data.flash_messages);
                const output_path = data.output_path;
                const diseases = data.diseases;
                document.getElementById('imagePreview').style.backgroundImage = `url(${output_path})`;
                document.getElementById('diseaseName').textContent = "Disease Name: " + diseases.join(', ');
                document.getElementById('medicinesBtn').dataset.diseases = diseases.join(',');
                document.getElementById('medicinesBtn').dataset.filename = filename;
                document.getElementById('result').style.display = 'block';
            })
            .catch(error => {
                console.error('Error:', error);
                document.getElementById('loader').style.display = 'none'; // Hide loader
            });
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('loader').style.display = 'none'; // Hide loader
        });
    });

    document.getElementById('medicinesBtn').addEventListener('click', function() {
        const diseases = this.dataset.diseases;
        const filename = this.dataset.filename;

        document.getElementById('loader').style.display = 'block'; // Show loader

        fetch(`/get_medicines/${diseases}/${filename}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('loader').style.display = 'none'; // Hide loader
            displayFlashMessages(data.flash_messages);
            const medicines = data.medicines;
            const medicinesContainer = document.getElementById('medicinesContainer');
            medicinesContainer.innerHTML = ''; // Clear previous content

            const heading = document.createElement('h3');
            heading.textContent = 'Recommended Medicines';
            medicinesContainer.appendChild(heading);

            const medicinesList = document.createElement('ul');
            for (const [disease, medicine] of Object.entries(medicines)) {
                const listItem = document.createElement('li');
                listItem.textContent = `${disease}: ${medicine}`;
                medicinesList.appendChild(listItem);
            }
            medicinesContainer.appendChild(medicinesList);
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('loader').style.display = 'none'; // Hide loader
        });
    });

    document.getElementById('resetBtn').addEventListener('click', function() {
        document.getElementById('imagePreview').style.backgroundImage = 'none';
        document.getElementById('result').style.display = 'none';
        document.getElementById('fileInput').value = '';
        document.getElementById('imagePreview').style.width = 'auto';
        document.getElementById('imagePreview').style.height = 'auto';
        document.getElementById('diseaseName').textContent = '';
        document.getElementById('medicinesContainer').innerHTML = ''; // Clear medicines container
    });

    function displayFlashMessages(messages) {
        const flashContainer = document.getElementById('flash-messages');
        flashContainer.innerHTML = '';  // Clear previous flash messages
        messages.forEach(msg => {
            const flashMessage = document.createElement('div');
            flashMessage.className = `alert alert-${msg.category}`;  // Adjust the class name based on your CSS
            flashMessage.textContent = msg.message;
            flashContainer.appendChild(flashMessage);
        });
    }

    document.getElementById('liveBtn').addEventListener('click', function() {
    var videoPreview = document.getElementById('videoPreview');
    var videoFeedUrl = this.getAttribute('data-video-feed-url');
    if (!videoPreview) {
        videoPreview = document.createElement('img');
        videoPreview.id = 'videoPreview';
        document.getElementById('imagePreview').appendChild(videoPreview);
        document.getElementById('videoPreview').style.display = 'none';
    }
    if (videoPreview.getAttribute('src') === null || videoPreview.getAttribute('src') === "") {
        videoPreview.setAttribute('src', videoFeedUrl);
        videoPreview.style.display = "block";
        // document.getElementById('videoPreview').style.display = 'none';
        this.textContent = "Stop Live Detection";
    } else {
        videoPreview.removeAttribute('src');
        videoPreview.style.display = "none";
        this.textContent = "Live Detect";
    }
});

});
