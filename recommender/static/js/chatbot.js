$(document).ready(function () {
    function toggleChat() {
        $("#chat-box").toggleClass("hidden");
    }

    window.toggleChat = toggleChat;  // Expose globally

    function addMessage(sender, text) {
        const msg = $("<div>").addClass("chat-message " + sender).text(text);
        $("#chat-body").append(msg);
        $("#chat-body").scrollTop($("#chat-body")[0].scrollHeight);
    }

    function addImage(url) {
        const img = $("<img>").attr("src", url).css({
            maxWidth: "100%",
            borderRadius: "6px",
            margin: "5px 0"
        });
        $("#chat-body").append(img);
        $("#chat-body").scrollTop($("#chat-body")[0].scrollHeight);
    }

    function sendMessage() {
        const input = $("#userInput");
        const message = input.val().trim();
        if (!message) return;

        addMessage("user", message);
        input.val("");

        axios.post("http://localhost:5005/webhooks/rest/webhook", {
            sender: "user",
            message: message
        })
        .then(response => {
            const data = response.data;
            data.forEach(item => {
                if (item.text) addMessage("bot", item.text);
                if (item.image) addImage(item.image);
            });
        })
        .catch(console.error);
    }

    window.sendMessage = sendMessage;  // Expose globally
});
