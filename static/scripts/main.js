const fillQuestion = (value) => {
    document.getElementById('user_message').value = value;
}

document.getElementById('clear-btn').addEventListener('click', () => {
    document.getElementById('user_message').value = '';
});

$(document).ready(() => { //
    const loader = $(".loader");
    const responseDiv = $('#response');

    const showLoader = () => {
        loader.show();
    }

    const hideLoader = () => {
        loader.hide();
    }

    const loadConversation = () => {
    $.ajax({
        url: "{{ url_for('get_response.response', user_id=user_id) }}",
        method: "POST",
        data: { user_message: "" },
        beforeSend: () => {
            showLoader();
        },
        success: (data) => {
            let conversationHTML = "";
            let conversation = data.conversation;

            for (let i = 0; i < conversation.length; i++) {
                let message = conversation[i];
                if (!(i === 0 && message.role === "user")) {
                    let messageClass = message.role === 'user' ? 'user' : 'gpt';
                    let sender = message.role === 'user' ? 'You' : 'Fitness-GPT';
                    conversationHTML += `
                        <div class="message-container ${messageClass}">
                            <p class="break-lines"><strong>${sender}:</strong> ${message.content}</p>
                        </div>
                    `;
                }
            }

            let trimmedHTML = conversationHTML.trim();
            responseDiv.html(trimmedHTML);

            if (trimmedHTML.length === 0) {
                responseDiv.hide();
            } else {
                responseDiv.show();
            }
        },
        error: function(error) {
            console.error("Error fetching conversation:", error);
        },
        complete: () => {
            hideLoader();
        }
    });
};
    // Initial conversation load
    loadConversation();
});
