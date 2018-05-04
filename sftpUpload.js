 var SftpUpload = require('sftp-upload'),
        fs = require('fs');
 
    var options = {
        host:'104.198.130.88',
        username:'jr_quinn96_gmail_com',
        path: '/home/jr_quinn96_gmail_com/js_source/uploadTest',
        remoteDir: '/home/jr_quinn96_gmail_com/tempDir',
        privateKey: fs.readFileSync('id_rsa_noroot')
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