const BASE = "http://localhost:8000";

// ─── Utility ────────────────────────────────────────────

// Grab the ?id=... from the URL (used on post.html)
function getIdFromUrl() {
  return new URLSearchParams(window.location.search).get("id");
}

// ─── index.html logic ───────────────────────────────────

function loadPosts() {
  fetch(`${BASE}/posts`)
    .then(r => r.json())
    .then(posts => {
      document.getElementById("posts").innerHTML = posts.map(p => `
        <div class="bg-white rounded-xl shadow p-5 flex justify-between items-start">
          <div>
            <a href="post.html?id=${p.id}" class="text-lg font-semibold text-blue-600 hover:underline">
              ${p.title}
            </a>
            <p class="text-gray-500 text-sm mt-1">${p.content.substring(0, 80)}...</p>
          </div>
          <button
            onclick="deletePost('${p.id}')"
            class="text-red-500 hover:text-red-700 text-sm ml-4 shrink-0"
          >
            Delete
          </button>
        </div>
      `).join("");
    });
}

function createPost() {
  const title = document.getElementById("title").value;
  const content = document.getElementById("content").value;

  fetch(`${BASE}/posts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, content })
  })
    .then(r => r.json())
    .then(() => {
      document.getElementById("title").value = "";
      document.getElementById("content").value = "";
      loadPosts();
    });
}

function deletePost(id) {
  fetch(`${BASE}/posts/${id}`, { method: "DELETE" })
    .then(r => {
      if (r.status === 204) loadPosts();
    });
}

// ─── post.html logic ────────────────────────────────────

function loadSinglePost() {
  const id = getIdFromUrl();

  fetch(`${BASE}/posts/${id}`)
    .then(r => r.json())
    .then(post => {
      document.getElementById("post").innerHTML = `
        <h1 class="text-2xl font-bold text-gray-900 mb-2">${post.title}</h1>
        <p class="text-gray-500 text-xs mb-4">${new Date(post.created_at).toLocaleDateString()}</p>
        <p class="text-gray-700 leading-relaxed">${post.content}</p>
      `;

      // Pre-fill the edit form with current values
      document.getElementById("edit-title").value = post.title;
      document.getElementById("edit-content").value = post.content;
    });
}

function updatePost() {
  const id = getIdFromUrl();
  const title = document.getElementById("edit-title").value;
  const content = document.getElementById("edit-content").value;

  fetch(`${BASE}/posts/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, content })
  })
    .then(r => r.json())
    .then(() => loadSinglePost()); // reload to show updated content
}

// ─── Router — detect which page we're on ────────────────

if (document.getElementById("posts")) {
  loadPosts();
}

if (document.getElementById("post")) {
  loadSinglePost();
}