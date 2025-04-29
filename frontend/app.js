// Initialize the API Gateway client
const apigClient = apigClientFactory.newClient({
  accessKey: '',
  secretKey: '',
  sessionToken: '',
  region: 'us-west-2',
  apiKey: 'OnXzfTLUJOa2LcKI4HUaB3vmGxfChsKd6OdE4E0l',
  defaultContentType: 'application/json',
  defaultAcceptType: 'application/json'
});


// SEARCH Photos
async function searchPhotos() {
  const query = document.getElementById('searchQuery').value;
  if (!query) return;

  try {
    const params = { q: query };
    const body = {};
    const additionalParams = {};

    const response = await apigClient.searchGet(params, body, additionalParams);

    const photosGrid = document.getElementById('photosGrid');
    photosGrid.innerHTML = '';

    const resp = JSON.parse(response.data.body);

    resp.results.forEach(url => {
      const img = document.createElement('img');
      img.src = url.url;
      photosGrid.appendChild(img);
    });
  } catch (error) {
    console.error('Error searching photos:', error);
    alert('Failed to search photos');
  }
}

// UPLOAD Photo
async function uploadPhoto() {
  const fileInput = document.getElementById('fileInput');
  const labelsInput = document.getElementById('customLabels');
  
  const file = fileInput.files[0];
  const customLabels = labelsInput.value;

  if (!file) {
    alert('Please select a file!');
    return;
  }

  const params = {
    object: file.name,
    "x-amz-meta-customLabels": customLabels
  };

  const additionalParams = {
    headers: {
      "Content-Type": file.type,
      "Accept": file.type,  // <-- ADD THIS
      "x-amz-meta-customLabels": customLabels
    }
  };

  try {
    const response = await apigClient.uploadPut(params, file, additionalParams);
    alert('Upload successful!');
  } catch (error) {
    console.error('Error uploading photo:', error);
    alert('Failed to upload photo');
  }
}