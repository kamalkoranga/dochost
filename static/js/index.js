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
    alert(data.error);
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
                        <div>
                            <button class="download-btn" onclick="downloadFile('${
                              item.path
                            }', event)">Download (${formatBytes(
        item.size
      )})</button>
                            <!--<button class="delete-btn" onclick="deleteItem('${
                              item.path
                            }', event)">Delete</button>-->
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

async function uploadFile() {
  const fileInput = document.getElementById("fileInput");
  if (!fileInput.files.length) return alert("Please select file(s)");

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
    alert(result.message || "Upload successful");
    fileInput.value = "";
    fetchFiles(currentPath);
  } catch (error) {
    alert(`Upload failed: ${error.message}`);
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

    fetchFiles(currentPath);
  } catch (error) {
    alert(`Delete failed: ${error.message}`);
  }
}

async function createFolder() {
  const folderName = document.getElementById("folderName").value.trim();
  if (!folderName) return alert("Please enter a folder name");

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
    fetchFiles(currentPath);
  } catch (error) {
    alert(`Create folder failed: ${error.message}`);
  }
}

function formatBytes(bytes) {
  const sizes = ["Bytes", "KB", "MB", "GB", "TB"];
  if (bytes === 0) return "0 Byte";
  const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
  return Math.round(bytes / Math.pow(1024, i), 2) + " " + sizes[i];
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

window.onload = () => {
  loadStorageInfo();
  fetchFiles(getPathFromUrl());
};

window.addEventListener("popstate", (event) => {
  const path = event.state?.path || "";
  fetchFiles(path);
});
