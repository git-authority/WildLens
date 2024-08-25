document.getElementById('file-upload').addEventListener('change', function() {
    const uploadText = document.getElementById('upload_status');
    const custom_file_upload = document.querySelector('.custom-file-upload');

    uploadText.textContent = "Uploading, Please Wait...";
    custom_file_upload.style.height = "30px";
    custom_file_upload.style.width = "210px";
    custom_file_upload.style.borderRadius = "17px";

    // Simulate an upload process
    setTimeout(() => {
        let uploadSuccessful = true;

        if (uploadSuccessful) {
            uploadText.textContent = "Upload Successful";
            custom_file_upload.style.width = "180px";
            custom_file_upload.style.height = "30px";
            custom_file_upload.style.borderRadius = "14px";
        } else {
            uploadText.textContent = "Upload Image";
            alert("Upload failed. Please try again.");
        }
    }, 2000); // Simulate 2 seconds upload time
});

