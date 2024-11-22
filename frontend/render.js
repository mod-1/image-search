document.getElementById('displaytext').style.display = 'none';

function searchPhoto() {
  const apigClient = apigClientFactory.newClient();

  const user_message = document.getElementById('note-textarea').value;

  const body = {};
  const params = { q: user_message };
  const additionalParams = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  apigClient
    .searchGet(params, body, additionalParams)
    .then(function (res) {
      resp_data = res.data;
      length_of_response = resp_data.length;
      if (length_of_response == 0) {
        document.getElementById('displaytext').innerHTML =
          'Sorry could not find the image. Try again!' ;
        document.getElementById('displaytext').style.display = 'block';
      }

      resp_data?.keys?.forEach(function (obj) {
        const img = new Image();
        img.src = "https://image-search-data.s3.us-east-1.amazonaws.com/" + obj;
        img.setAttribute('class', 'banner-img');
        img.setAttribute('alt', 'effy');
        document.getElementById('displaytext').innerHTML =
          'Images returned are : ';
        document.getElementById('img-container').appendChild(img);
        document.getElementById('displaytext').style.display = 'block';
      });
    })
    .catch(function (err) {
      console.log(err);
    });
}

function getBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => {
      let encoded = reader.result.replace(/^data:(.*;base64,)?/, '');
      if (encoded.length % 4 > 0) {
        encoded += '='.repeat(4 - (encoded.length % 4));
      }
      resolve(encoded);
    };
    reader.onerror = (error) => reject(error);
  });
}

function uploadPhoto() {
    const file = document.getElementById('file_path').files[0];
    const customLabels = document.getElementById('note_customtag').value;
    const params = {
        bucket: 'image-search-data',
        key: `${Date.now()}-${file.name}`
    };
  
  getBase64(file).then((data) => {
    const apigClient = apigClientFactory.newClient();

    const file_type = file.type + ';base64';
    const additionalParams = {
      headers: {
        'Accept': 'image/*',
        'Content-Type': file_type,
        'x-amz-meta-customlabels': customLabels
      }
    };

    const body = data;
    apigClient
      .uploadBucketKeyPut(params, body, additionalParams)
      .then(function (res) {
        if (res.status == 200) {
          document.getElementById('uploadText').innerHTML =
            ':) Your image is uploaded successfully!';
          document.getElementById('uploadText').style.display = 'block';
        }
      });
  });
}