const qrcode = require('qrcode');

const testQRCode = async () => {
    const qr = 'YOUR_TEST_QR_CODE_STRING';  // Replace with a test QR code string
    qrcode.toDataURL(qr, (err, url) => {
        if (err) {
            console.error('Error generating QR code:', err);
        } else {
            console.log('QR code URL:', url);
        }
    });
};

testQRCode();