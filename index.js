const exec = require('child_process').exec;
const fs = require('fs');
const path = require('path');
const storage = require('@google-cloud/storage')();
const SftpUpload = require('sftp-upload');

exports.downloadImage = (event) => {
  const object = event.data;
  const file = storage.bucket(object.bucket).file(object.name);
  const tempLocalFilename = `/tmp/${path.parse(file.name).base}`;

  // Download file from bucket.
  return file.download({ destination: tempLocalFilename })
    .catch((err) => {
      console.error('Failed to download file.', err);
      return Promise.reject(err);
    })
    .then(() => {
      console.log(`Image ${file.name} has been downloaded to ${tempLocalFilename}.`);
      //Upload from gcf environment to vm
    var options = {
        host:'104.198.130.88',
        username:'jr_quinn96_gmail_com',
        path: '/tmp',
        remoteDir: '/home/jr_quinn96_gmail_com/tempDir',
        privateKey: fs.readFileSync('gs://ecen404/id_rsa_noroot')
    },
    sftp = new SftpUpload(options);
 
    sftp.on('error', function(err) {
        throw err;
    })
    .on('uploading', function(progress) {
        console.log('Uploading', progress.file);
        console.log(progress.percent+'% completed');
    })
    .on('completed', function() {
        console.log('Upload Completed');
    })
    .upload();
    })
    
}