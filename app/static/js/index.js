// /*

document.addEventListener("contextmenu", (event) => event.preventDefault());
document.addEventListener("keydown", function (e) {
  if (
    e.key === "F12" ||
    (e.ctrlKey &&
      e.shiftKey &&
      (e.key === "I" || e.key === "J" || e.key === "C")) ||
    (e.ctrlKey && e.key === "U") ||
    (e.ctrlKey && e.key === "u") ||
    (e.ctrlKey && e.key === "s") ||
    (e.ctrlKey && e.key === "S")
  ) {
    e.preventDefault();
  }
});

// */

let currentPath = "";

function getPathFromUrl() {
  const params = new URLSearchParams(window.location.search);
  const path = params.get("path");
  return path ? decodeURIComponent(path) : "";
}

async function fetchFiles(path = "") {
  currentPath = path;

  // Update URL with current path
  const newUrl = path
    ? `${window.location.pathname}?path=${encodeURIComponent(path)}`
    : window.location.pathname;
  window.history.pushState({ path }, "", newUrl);

  updateBreadcrumb();

  const url = path ? `/files/${path}` : "/files";
  const response = await fetch(url);
  const data = await response.json();

  if (data.error) {
    window.location.href = "/";
    // alert(data.error);
    return;
  }

  const fileList = document.getElementById("fileList");
  fileList.innerHTML = "";

  // Add ".." for navigation to parent folder (except root)
  if (path) {
    const li = document.createElement("li");
    li.className = "folder";
    li.innerHTML = `<span>.. (⬅️ Back)</span>`;
    li.onclick = () => {
      const parentPath = path.split("/").slice(0, -1).join("/");
      fetchFiles(parentPath);
    };
    fileList.appendChild(li);
  }

  data.files.forEach((item) => {
    item.path = item.path.replace(/\\/g, "/");
    const li = document.createElement("li");
    if (item.is_dir) {
      li.className = "folder";
      li.setAttribute("data-path", item.path);
      li.innerHTML = `
              <span class="file">📁 ${item.name}</span>
              <span class="file-size">${formatBytes(item.size)}</span>
            `;
      li.onclick = () => fetchFiles(item.path);
    } else {
      // Check if it's a video file
      const isVideo = item.name.match(/\.(mp4|mov|avi|mkv)$/i);
      const thumbnail = item.thumbnail
        ? `<img src="${item.thumbnail}" class="thumbnail" alt="${item.name}">`
        : "📄";
      li.innerHTML = `
                        <span class="file">${item.name}</span>
                        <div style="display: flex; align-items: center;">
                            <button class="download-btn" onclick="downloadFile('${
                              item.path
                            }', event)"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-download" viewBox="0 0 16 16">
  <path d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5"/>
  <path d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708z"/>
</svg> <span>|</span> ${formatBytes(item.size)}</button>
                            <button class="delete-btn" onclick="deleteItem('${
                              item.path
                            }', event)"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-trash3" viewBox="0 0 16 16">
  <path d="M6.5 1h3a.5.5 0 0 1 .5.5v1H6v-1a.5.5 0 0 1 .5-.5M11 2.5v-1A1.5 1.5 0 0 0 9.5 0h-3A1.5 1.5 0 0 0 5 1.5v1H1.5a.5.5 0 0 0 0 1h.538l.853 10.66A2 2 0 0 0 4.885 16h6.23a2 2 0 0 0 1.994-1.84l.853-10.66h.538a.5.5 0 0 0 0-1zm1.958 1-.846 10.58a1 1 0 0 1-.997.92h-6.23a1 1 0 0 1-.997-.92L3.042 3.5zm-7.487 1a.5.5 0 0 1 .528.47l.5 8.5a.5.5 0 0 1-.998.06L5 5.03a.5.5 0 0 1 .47-.53Zm5.058 0a.5.5 0 0 1 .47.53l-.5 8.5a.5.5 0 1 1-.998-.06l.5-8.5a.5.5 0 0 1 .528-.47M8 4.5a.5.5 0 0 1 .5.5v8.5a.5.5 0 0 1-1 0V5a.5.5 0 0 1 .5-.5"/>
</svg></button>
                        </div>
                    `;
    }
    fileList.appendChild(li);
  });
}

function updateBreadcrumb() {
  const breadcrumb = document.getElementById("breadcrumb");
  breadcrumb.innerHTML = "";

  const parts = currentPath.split("/");
  let pathSoFar = "";

  // Add root link
  const rootLi = document.createElement("li");
  rootLi.innerHTML = `<a href="#" onclick="fetchFiles('')">Drive</a>`;
  breadcrumb.appendChild(rootLi);

  // Add path parts
  parts.forEach((part) => {
    if (!part) return;
    pathSoFar = pathSoFar ? `${pathSoFar}/${part}` : part;
    const li = document.createElement("li");
    li.innerHTML = `<a href="#" onclick="fetchFiles('${pathSoFar}')">${part}</a>`;
    breadcrumb.appendChild(li);
  });
}

// Toast notification system
function showToast(message, type = "success") {
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;
  document.getElementById("toastContainer").appendChild(toast);

  // Show toast
  setTimeout(() => toast.classList.add("show"), 10);

  // Auto-remove after 5 seconds
  setTimeout(() => {
    toast.classList.remove("show");
    setTimeout(() => toast.remove(), 300);
  }, 5000);
}

async function uploadFile() {
  const fileInput = document.getElementById("fileInput");
  const uploadBtn = document.getElementById("uploadBtn");
  const btnText = document.getElementById("btnText");
  const btnSpinner = document.getElementById("btnSpinner");

  if (!fileInput.files.length) {
    showToast("Please select file(s) first", "error");
    return;
  }

  // UI Loading state
  uploadBtn.disabled = true;
  btnText.style.display = "none";
  btnSpinner.style.display = "inline";

  const formData = new FormData();
  for (let i = 0; i < fileInput.files.length; i++) {
    const file = fileInput.files[i];
    // Preserve the relative path for folder uploads
    const webkitRelativePath = file.webkitRelativePath || file.name;
    const uploadPath = currentPath
      ? `${currentPath}/${webkitRelativePath}`
      : webkitRelativePath;
    formData.append("files[]", file);
    // Add path information as separate form data
    formData.append(`${file.name}_path`, uploadPath);
  }

  try {
    const response = await fetch("/upload", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || "Upload failed");
    }

    const result = await response.json();
    showToast(result.message || "Files uploaded successfully!");
  } catch (error) {
    showToast(`Upload failed: ${error.message}`, "error");
  } finally {
    // Reset UI
    fileInput.value = "";
    updateSelectedFilesList();
    fetchFiles(currentPath);
    loadStorageInfo();
    uploadBtn.disabled = false;
    btnText.style.display = "inline";
    btnSpinner.style.display = "none";
  }
}

function downloadFile(path, event) {
  event.stopPropagation();
  const encodedPath = encodeURIComponent(path);
  window.location.href = `/download/${encodedPath}`;
}

async function deleteItem(path, event) {
  event.stopPropagation();
  if (!confirm("Are you sure you want to delete this item?")) return;

  try {
    const response = await fetch(`/delete/${path}`, {
      method: "DELETE",
    });
    const result = await response.json();
    if (result.error) throw new Error(result.error);
    showToast(result.message || "Item deleted successfully!");
    fetchFiles(currentPath);
    loadStorageInfo();
  } catch (error) {
    showToast(`Delete failed: ${error.message}`, "error");
  } 
}

async function createFolder() {
  const folderName = document.getElementById("folderName").value.trim();
  if (!folderName) return showToast("Please enter a folder name", "error");

  try {
    const response = await fetch("/create-folder", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        folderName: currentPath ? `${currentPath}/${folderName}` : folderName,
      }),
    });
    const result = await response.json();
    if (result.error) throw new Error(result.error);

    document.getElementById("folderName").value = "";
    showToast(result.message || "Folder created successfully!");
    fetchFiles(currentPath);
  } catch (error) {
    showToast(`Create folder failed: ${error.message}`, "error");
  }
}

function formatBytes(bytes) {
  const sizes = ["Bytes", "KB", "MB", "GB", "TB"];
  if (bytes === 0) return "0 Byte";
  const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
  const value = bytes / Math.pow(1024, i);
  return (i === 0 ? value : value.toFixed(2)) + " " + sizes[i];
}

async function loadStorageInfo() {
  const res = await fetch("/storage-info");
  const data = await res.json();

  document.getElementById("storage-bar").innerHTML = `
            <strong>Used:</strong> ${formatBytes(data.used)} /
            <strong>Total:</strong> ${formatBytes(data.total)}<br>
            <progress value="${data.used}" max="${
    data.total
  }" style="width: 100%; margin-top: 10px;"></progress>
            `;
}

if (window.location.pathname === "/") {
  loadStorageInfo();
  fetchFiles(getPathFromUrl());
}


window.addEventListener("popstate", (event) => {
  const path = event.state?.path || "";
  fetchFiles(path);
});


function customContextMenu() {

  let folderContextMenu = document.getElementById("folderContextMenu");
  let deleteFolderBtn = document.getElementById("deleteFolderBtn");
  let rightClickedFolderPath = null;
  
  // Delegate right-click event for folders
  document.getElementById("fileList").addEventListener("contextmenu", function(e) {
    const folderLi = e.target.closest(".folder");
    if (folderLi) {
      e.preventDefault();
      // Find the folder's path from the data
      const folderName = folderLi.querySelector(".file")?.textContent.replace(/^📁\s*/, "") || "";
      // Find the folder's path from the loaded data
      const folderItem = Array.from(folderLi.parentNode.children).indexOf(folderLi);
      // Get the path from the data attribute if you add it, or reconstruct from currentPath and folderName
      rightClickedFolderPath = folderLi.dataset.path || (currentPath ? `${currentPath}/${folderName}` : folderName);
  
      // Show context menu at mouse position
      folderContextMenu.style.top = `${e.pageY}px`;
      folderContextMenu.style.left = `${e.pageX}px`;
      folderContextMenu.style.display = "block";
    } else {
      folderContextMenu.style.display = "none";
    }
  });
  
  // Hide menu on click elsewhere
  document.addEventListener("click", function() {
    folderContextMenu.style.display = "none";
  });
  
  // Delete folder on menu click
  deleteFolderBtn.addEventListener("click", function() {
    folderContextMenu.style.display = "none";
    if (rightClickedFolderPath) {
      deleteItem(rightClickedFolderPath, { stopPropagation: () => {} });
    }
  });
}

if (window.location.pathname === "/") {
  customContextMenu()
  const uploadDropArea = document.getElementById("uploadDropArea");
  const fileInput = document.getElementById("fileInput");
  const selectedFilesList = document.getElementById("selectedFilesList");
  
  // Drag & drop events
  ["dragenter", "dragover"].forEach(eventName => {
    uploadDropArea.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      uploadDropArea.classList.add("dragover");
    });
  });
  ["dragleave", "drop"].forEach(eventName => {
    uploadDropArea.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      uploadDropArea.classList.remove("dragover");
    });
  });
  uploadDropArea.addEventListener("drop", (e) => {
    fileInput.files = e.dataTransfer.files;
    updateSelectedFilesList();
  });
  
  // Update file list preview
  fileInput.addEventListener("change", updateSelectedFilesList);
}


function updateSelectedFilesList() {
  selectedFilesList.innerHTML = "";
  for (let i = 0; i < fileInput.files.length; i++) {
    const file = fileInput.files[i];
    const li = document.createElement("li");
    li.textContent = file.name;
    selectedFilesList.appendChild(li);
  }
}