// Riko Voice Assistant Client Application

document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const chatForm = document.getElementById("chat-form");
    const userInput = document.getElementById("user-input");
    const chatMessages = document.getElementById("chat-messages");
    const micBtn = document.getElementById("mic-btn");
    const themeToggle = document.getElementById("theme-toggle");
    
    // Weather Widget Elements
    const weatherContent = document.getElementById("weather-content");
    
    // Reminders Widget Elements
    const remindersList = document.getElementById("reminders-list");
    const remindersEmpty = document.getElementById("reminders-empty");
    


    // Theme state
    let activeTheme = localStorage.getItem("theme") || "dark";
    document.documentElement.setAttribute("data-theme", activeTheme);
    updateThemeIcon();

    // Load initial reminders
    fetchReminders();


    // Form submission
    chatForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const text = userInput.value.trim();
        if (!text) return;

        // Clear input and add user message
        userInput.value = "";
        appendMessage("user", text);
        
        // Add a temporary typing loader
        const loaderId = appendLoader();

        try {
            const response = await fetch("/api/command", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text })
            });

            removeLoader(loaderId);

            if (response.ok) {
                const result = await response.json();
                
                // Add assistant response message
                appendMessage("assistant", result.speech);
                
                // Process UI Actions returned by backend
                handleUIAction(result);
            } else {
                appendMessage("assistant", "Sorry, I encountered an error. Please try again.");
            }
        } catch (error) {
            console.log(error)
            removeLoader(loaderId);
            appendMessage("assistant", "I couldn't reach the server. Please verify the backend is running.");
        }
    });

    // Theme Toggle
    themeToggle.addEventListener("click", () => {
        activeTheme = activeTheme === "dark" ? "light" : "dark";
        document.documentElement.setAttribute("data-theme", activeTheme);
        localStorage.setItem("theme", activeTheme);
        updateThemeIcon();
    });

    function updateThemeIcon() {
        const icon = themeToggle.querySelector("i");
        if (activeTheme === "light") {
            icon.className = "fa-solid fa-sun";
        } else {
            icon.className = "fa-solid fa-moon";
        }
    }

    // --- Web Speech API (Voice Simulation) ---
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.lang = 'en-US';
        recognition.interimResults = false;

        micBtn.addEventListener("click", () => {
            if (micBtn.classList.contains("active")) {
                recognition.stop();
            } else {
                micBtn.classList.add("active");
                userInput.placeholder = "Listening...";
                recognition.start();
            }
        });

        recognition.onresult = (event) => {
            const speechToText = event.results[0][0].transcript;
            userInput.value = speechToText;
            micBtn.classList.remove("active");
            userInput.placeholder = "Type a command or ask a question...";
            chatForm.dispatchEvent(new Event("submit"));
        };

        recognition.onerror = () => {
            micBtn.classList.remove("active");
            userInput.placeholder = "Type a command or ask a question...";
        };

        recognition.onend = () => {
            micBtn.classList.remove("active");
            userInput.placeholder = "Type a command or ask a question...";
        };
    } else {
        micBtn.style.display = "none"; // Hide if speech recognition is not supported
    }

    function handleUIAction(result) {
        const action = result.ui_action;
        const data = result.data;

        if (action === "UPDATE_WEATHER") {
            updateWeatherCard(data.weather);
        } else if (action === "UPDATE_REMINDERS") {
            renderReminders(data.reminders);
        }
    }

    // Weather widget update
    function updateWeatherCard(weather) {
        if (!weather) return;
        
        weatherContent.classList.remove("placeholder");
        weatherContent.innerHTML = `
            <div class="weather-card-widget">
                <div class="weather-header">
                    <h4>${weather.city}</h4>
                    ${weather.simulated ? '<span class="weather-sim-badge">Simulated</span>' : ''}
                </div>
                <div class="weather-main">
                    <i class="fa-solid fa-${weather.icon} weather-icon ${weather.icon}"></i>
                    <span class="weather-temp">${weather.temperature}</span>
                </div>
                <p class="status-msg" style="margin-bottom: 6px;">${weather.condition} &bull; ${weather.description}</p>
                <div class="weather-details">
                    <div><span>Humidity:</span> <span>${weather.humidity}</span></div>
                    <div><span>Wind speed:</span> <span>${weather.wind}</span></div>
                </div>
            </div>
        `;
    }

    // Fetch and render Reminders
    async function fetchReminders() {
        try {
            const response = await fetch("/api/reminders");
            if (response.ok) {
                const reminders = await response.json();
                renderReminders(reminders);
            }
        } catch (error) {
            console.error("Failed to load reminders:", error);
        }
    }

    function renderReminders(reminders) {
        remindersList.innerHTML = "";
        if (!reminders || reminders.length === 0) {
            remindersEmpty.style.display = "block";
            return;
        }

        remindersEmpty.style.display = "none";
        reminders.forEach(rem => {
            const li = document.createElement("li");
            li.className = "reminder-item";
            li.innerHTML = `
                <div class="reminder-info">
                    <span class="reminder-text">${rem.text}</span>
                    <span class="reminder-time"><i class="fa-regular fa-clock"></i> ${rem.time}</span>
                </div>
                <button class="delete-rem-btn" data-id="${rem.id}"><i class="fa-solid fa-trash-can"></i></button>
            `;
            remindersList.appendChild(li);
        });

        // Add delete button events
        document.querySelectorAll(".delete-rem-btn").forEach(btn => {
            btn.addEventListener("click", async (e) => {
                const id = btn.getAttribute("data-id");
                await deleteReminder(id);
            });
        });
    }

    async function deleteReminder(id) {
        try {
            const response = await fetch(`/api/reminders/${id}`, { method: "DELETE" });
            if (response.ok) {
                fetchReminders();
            }
        } catch (error) {
            console.error("Failed to delete reminder:", error);
        }
    }



    // --- HELPER CHAT UTILITIES ---
    function appendMessage(sender, text) {
        const messageDiv = document.createElement("div");
        messageDiv.className = `message ${sender}`;
        
        const avatarHTML = sender === "assistant" 
            ? `<div class="avatar"><i class="fa-solid fa-robot"></i></div>`
            : `<div class="avatar"><i class="fa-solid fa-user"></i></div>`;
            
        messageDiv.innerHTML = `
            ${avatarHTML}
            <div class="message-content">
                <p>${escapeHTML(text)}</p>
                <span class="timestamp">${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
            </div>
        `;
        
        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    }

    function appendLoader() {
        const loaderId = "loader_" + Date.now();
        const loaderDiv = document.createElement("div");
        loaderDiv.className = "message assistant typing-loader";
        loaderDiv.id = loaderId;
        loaderDiv.innerHTML = `
            <div class="avatar"><i class="fa-solid fa-robot"></i></div>
            <div class="message-content" style="padding: 10px 18px;">
                <p><i class="fa-solid fa-circle-notch fa-spin"></i> Riko is thinking...</p>
            </div>
        `;
        chatMessages.appendChild(loaderDiv);
        scrollToBottom();
        return loaderId;
    }

    function removeLoader(id) {
        const loader = document.getElementById(id);
        if (loader) {
            loader.remove();
        }
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function escapeHTML(str) {
        if (str === null || str === undefined) return "";
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
});
