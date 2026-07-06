// Change this variable if your backend host/port changes
const API_BASE_URL = 'https://immoran-blog-sulb.onrender.com'; 

// Auto-run layout navigation sync on every page load
document.addEventListener("DOMContentLoaded", syncNavbarView);

function getAuthToken() {
    return localStorage.getItem('access_token') || null;
}

// Global alert system
function displayAlert(message, isSuccess = false) {
    const alertBox = document.getElementById('alert-box');
    if (!alertBox) return;
    
    alertBox.textContent = message;
    alertBox.className = isSuccess 
        ? "bg-green-100 text-green-800 p-4 rounded text-center font-semibold mb-4 block" 
        : "bg-red-100 text-red-800 p-4 rounded text-center font-semibold mb-4 block";
}

// Sync global navigation across layouts
function syncNavbarView() {
    const navLinks = document.getElementById('nav-links');
    const createBtn = document.getElementById('create-post-btn');
    const token = getAuthToken();

    if (!navLinks) return;

    if (token) {
        if (createBtn) createBtn.classList.remove('hidden');
        navLinks.innerHTML = `
            <a href="index.html" class="hover:underline">Home</a>
            <button onclick="terminateSession()" class="bg-red-500 px-3 py-1 rounded text-sm hover:bg-red-700 transition font-medium">Logout</button>
        `;
    } else {
        if (createBtn) createBtn.classList.add('hidden');
        navLinks.innerHTML = `
            <a href="index.html" class="hover:underline mr-2">Home</a>
            <a href="auth.html" class="bg-blue-800 px-3 py-1 rounded text-sm hover:bg-blue-900 transition font-medium">Login</a>
        `;
    }
}

// Terminate session
function terminateSession() {
    localStorage.removeItem('access_token');
    window.location.href = 'index.html';
}

// Handle Login and Account Creation requests
async function processAuthentication(isLoginMode) {
    const identifier = document.getElementById('auth-identifier').value;
    const password = document.getElementById('auth-password').value;
    const username = document.getElementById('auth-username').value;

    try {
        if (isLoginMode) {
            // Target: @app.post("/login")
            const response = await fetch(`${API_BASE_URL}/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ identifier, password })
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || "Invalid login credentials.");

            localStorage.setItem('access_token', data.access_token);
            displayAlert("Success! Redirecting dashboard...", true);
            setTimeout(() => { window.location.href = 'index.html'; }, 1000);
        } else {
            // Target: @app.post("/new_user")
            const response = await fetch(`${API_BASE_URL}/new_user`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email: identifier, password })
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || "Registration encountered an issue.");

            displayAlert("Account created successfully! Switching to Login...", true);
            setTimeout(() => { toggleAuthMode(); }, 1500);
        }
    } catch (error) {
        displayAlert(error.message);
    }
}

// Fetch home snippets from root endpoint
async function loadFeed() {
    const container = document.getElementById('feed-container');
    if (!container) return;

    try {
        // Target: @app.get("/")
        const response = await fetch(`${API_BASE_URL}/?limit=50`);
        if (!response.ok) throw new Error("Could not download home stream data.");
        const posts = await response.json();

        if (posts.length === 0) {
            container.innerHTML = `<p class="text-gray-500 text-center py-8 bg-white rounded shadow-sm">No snippet updates live yet.</p>`;
            return;
        }

        container.innerHTML = posts.map(post => `
            <div class="bg-white p-5 rounded-lg shadow-sm border border-gray-200">
                <h3 class="text-xl font-bold text-gray-900">${escapeString(post.title)}</h3>
                <p class="text-gray-600 mt-2 italic text-sm">Snippet: ${escapeString(post.snippet || "Empty text post body...")}</p>
                <div class="mt-4 flex justify-between items-center text-xs text-gray-500">
                    <span>Published: ${new Date(post.created_at).toLocaleDateString()}</span>
                    <div class="flex space-x-2">
                        <button onclick="handleLikeToggle('${post.id}')" class="bg-blue-50 text-blue-600 px-3 py-1 rounded border border-blue-200 hover:bg-blue-100 transition font-semibold">
                            ❤️ Like / Unlike
                        </button>
                        <button onclick="handlePostDeletion('${post.id}')" class="bg-red-50 text-red-600 px-3 py-1 rounded border border-red-200 hover:bg-red-100 transition font-semibold">
                            🗑️ Delete
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        container.innerHTML = `<p class="text-red-500 text-center py-4 bg-white rounded shadow-sm">${error.message}</p>`;
    }
}

// Create a new post
async function handleCreatePost(e) {
    e.preventDefault();
    const token = getAuthToken();
    if (!token) return;

    const title = document.getElementById('post-title').value;
    const content = document.getElementById('post-content').value;
    const published = document.getElementById('post-published').checked;

    try {
        // Target: @app.post("/posts")
        const response = await fetch(`${API_BASE_URL}/posts`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ title, content, published })
        });
        
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Failed to create entry.");

        displayAlert("Post published successfully!", true);
        setTimeout(() => { window.location.href = 'index.html'; }, 1000);
    } catch (error) {
        displayAlert(error.message);
    }
}

// Delete selected post
async function handlePostDeletion(id) {
    const token = getAuthToken();
    if (!token) {
        alert("Please login first to manage posts!");
        return;
    }

    if (!confirm("Are you sure you want to drop this post?")) return;

    try {
        // Target: @app.delete("/posts/{id}")
        const response = await fetch(`${API_BASE_URL}/posts/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.status === 403) throw new Error("Unauthorized action. You do not own this post.");
        if (!response.ok) throw new Error("Could not process post removal.");

        loadFeed();
    } catch (error) {
        alert(error.message);
    }
}

// Like/Unlike dynamic switch
async function handleLikeToggle(id) {
    const token = getAuthToken();
    if (!token) {
        alert("Please login first to interact with posts!");
        return;
    }

    try {
        // Target: @app.post("/post/{id}/like")
        const response = await fetch(`${API_BASE_URL}/post/${id}/like`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await response.json();
        alert(data.detail);
        loadFeed();
    } catch (error) {
        alert("Error interacting with like module.");
    }
}

// XSS Prevention sanitizer
function escapeString(str) {
    if (!str) return '';
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}