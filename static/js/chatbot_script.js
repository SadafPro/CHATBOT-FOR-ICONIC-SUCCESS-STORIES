function displayMessageWithTypingEffect(message, className) {
    var ul = document.getElementById("messages");

    function typeWriterEffect(text, element, callback) {
        var index = 0;
        function type() {
            if (index < text.length) {
                element.append(text.charAt(index));
                index++;
                setTimeout(type, 15); // Adjust typing speed here
                scrollToBottom();
            } else if (callback) {
                callback();
            }
        }
        type();
    }

    function displaySection(index, sections, li, callback) {
        if (index < sections.length) {
            var subtopic = sections[index].subtopic;
            var paragraphs = sections[index].paragraphs;
    
            var subtopicNode = document.createElement('div');
            subtopicNode.className = 'subtopic';
            subtopicNode.innerHTML = (index + 1) + ". " + subtopic; // Adding numbers to subtopics
            li.appendChild(subtopicNode);
    
            var paragraphList = document.createElement('ul');
            paragraphList.className = 'paragraph-list';
            li.appendChild(paragraphList);
    
            var paragraphIndex = 0;
    
            function typeWriterEffectForParagraph(paragraph, paragraphNode, callback) {
                var index = 0;
                function type() {
                    if (index < paragraph.length) {
                        if (index === 0) {
                            paragraphNode.innerHTML += "&#8226; "; // Adding bullet point at the beginning of the paragraph
                        }
                        paragraphNode.innerHTML += paragraph.charAt(index);
                        index++;
                        setTimeout(type, 15); // Adjust typing speed here
                        scrollToBottom();
                    } else {
                        if (callback) {
                            callback(); // Call the callback function after the paragraph has finished typing
                        }
                    }
                }
                type();
            }
    
            function displayNextParagraph() {
                if (paragraphIndex < paragraphs.length) {
                    var paragraph = paragraphs[paragraphIndex];
                    var paragraphNode = document.createElement('li');
                    paragraphNode.className = 'paragraph';
                    paragraphList.appendChild(paragraphNode);
    
                    typeWriterEffectForParagraph(paragraph, paragraphNode, function() {
                        paragraphIndex++;
                        displayNextParagraph(); // Call the next paragraph after the current one finishes typing
                    });
                } else {
                    // Call the next section after all paragraphs have finished typing
                    displaySection(index + 1, sections, li, callback);
                }
            }
    
            displayNextParagraph();
        } else {
            if (callback) {
                callback(); // Call the callback function after the current section has finished typing
            }
        }
    }
    
    
    // Create a new li element for the bot response
    var li = document.createElement("li");
    li.className = className;

    // Append the bot image
    var img = document.createElement('img');
    img.src = 'static/images/wall-e-waving.gif'; // Adjust the path as needed
    img.className = 'bot-image';
    li.appendChild(img);

    // Add line breaks after the image
    li.appendChild(document.createElement('br'));
    li.appendChild(document.createElement('br'));

    // Append the li to the ul
    ul.appendChild(li);

    try {
        var response = JSON.parse(message);
        var sections = response.response;

        // Check if response is an array (structured JSON response)
        if (Array.isArray(sections)) {
            // Call displaySection to display the bot response content
            displaySection(0, sections, li);
        } else {
            // For a simple string response
            typeWriterEffect(sections, li);
        }
    } catch (e) {
        // If it's not a JSON object, treat it as a plain text message
        typeWriterEffect(message, li);
    }
}


function sendMessage() {
    var userInput = document.getElementById("userInput").value;

    displayMessage("You: " + userInput, "user-message");

    fetch('/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: 'user_input=' + encodeURIComponent(userInput)
    })
    .then(response => response.json())
    .then(data => {
        var botMessage = JSON.stringify(data);
        displayMessageWithTypingEffect(botMessage, "bot-message");
        scrollToBottom();
    })
    .catch(error => console.error('Error:', error));

    document.getElementById("userInput").value = "";
}

function displayMessage(message, className) {
    var ul = document.getElementById("messages");
    var li = document.createElement("li");
    li.className = className; // Add the specified class

    // Add message content
    li.appendChild(document.createTextNode(message));
    ul.appendChild(li);

    // Scroll to bottom
    scrollToBottom();
}

function scrollToBottom() {
    var chatWindow = document.getElementById("messages");
    chatWindow.scrollTop = chatWindow.scrollHeight;
}
