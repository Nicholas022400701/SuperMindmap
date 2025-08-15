const API_BASE_URL = "http://localhost:8000/api";

export const getGraphData = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/graph`);
    if (!response.ok) {
      throw new Error("Network response was not ok");
    }
    return await response.json();
  } catch (error) {
    console.error("Failed to fetch graph data:", error);
    // Return a default empty graph in case of error
    return { nodes: [], links: [] };
  }
};

export const addKeyword = async (keyword) => {
  try {
    const response = await fetch(`${API_BASE_URL}/add`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ keyword }),
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Failed to add keyword");
    }
    return await response.json();
  } catch (error) {
    console.error("Failed to add keyword:", error);
    throw error; // Re-throw to be handled by the component
  }
};

export const exportNode = async (nodeId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/export/${nodeId}`);
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Failed to export node");
    }
    const data = await response.json();
    // Trigger download
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(data, null, 2));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", `mindmap_export_${nodeId}.json`);
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  } catch (error) {
    console.error("Failed to export node:", error);
    throw error;
  }
};

export const deleteNode = async (nodeId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/nodes/${nodeId}`, {
      method: "DELETE",
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Failed to delete node");
    }
    // No content expected for 204 response, so no need to return response.json()
  } catch (error) {
    console.error("Failed to delete node:", error);
    throw error;
  }
};
