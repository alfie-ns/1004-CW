document.addEventListener("DOMContentLoaded", function() {
    // If document is loaded, get the youtube-form element
    const youtubeForm = document.getElementById("youtube-form");

    // Event listener for when the form is submitted
    youtubeForm.addEventListener("submit", function(event) {
        event.preventDefault(); // Prevents the page from reloading

        const url = new URL(youtubeForm.query.value);
        console.log('URL:', url);
        const videoId = url.searchParams.get('v'); 
        console.log('Video ID:', videoId);

        // Fetch /captions to get the caption IDs
        fetch("/captions", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ video_id: videoId })
        })
        .then(response => response.json())
        .then(data => {
            console.log('English caption IDs:', data.english_caption_ids);

            // Now fetch the captions using the returned IDs
            fetch("/download_captions", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ video_id: videoId })
            })
            .then(response => response.json())
            .then(data => {
                console.log('Responses:', data.responses);

                // Populate the container with the responses
                const responseContainer = document.querySelector('.container');
                data.responses.forEach(response => {
                    const p = document.createElement('p');
                    p.innerHTML = response;
                    responseContainer.appendChild(p);
                });
                
            })
            .catch(error => console.error('Error:', error));
        })
        .catch(error => console.error('Error:', error));
    });
});
