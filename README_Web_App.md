# Voice Verification Web Application

A web-based interface for the Neurotec VeriSpeak voice verification system that allows users on your local network to upload audio files and calculate similarity scores.

## 🌟 Features

- **Web-based Interface**: User-friendly web interface accessible from any device
- **Local Network Access**: Access from phones, tablets, and computers on the same network  
- **Single Verification**: Compare two audio files for voice similarity
- **Batch Processing**: Compare multiple files against a reference audio
- **Real-time Results**: Get VeriSpeak scores with confidence levels
- **File Upload**: Support for WAV, MP3, FLAC, M4A, AAC, OGG formats
- **Responsive Design**: Works on desktop and mobile devices

## 🚀 Quick Start

### 1. Start the Server
```bash
cd /home/lab2208/Desktop/neurotec_voice_tools/
./start_server.sh
```

### 2. Access the Application
- **Local access**: http://localhost:5000
- **Network access**: http://YOUR_IP_ADDRESS:5000

The startup script will display the exact URLs to use.

## 🎯 How to Use

### Single Verification
1. Open the web interface in your browser
2. Click on "Single Verification" tab (default)
3. Upload a reference audio file
4. Upload a candidate audio file
5. Click "Verify Voices" to get the similarity score

### Batch Processing
1. Click on the "Batch Processing" tab
2. Upload multiple audio files (minimum 2)
3. The first file will be used as reference
4. Click "Process Batch" to compare all files against the reference

### Understanding Results
- **Score**: Similarity score (higher = more similar)
- **Threshold**: Decision boundary (typically 48)
- **Status**: MATCH (same speaker) or NO MATCH (different speakers)
- **Confidence**: 
  - Very High (score > threshold + 50)
  - High (score > threshold + 20)
  - Medium (score > threshold)
  - Low (score < threshold)

## 🔧 Configuration

### File Size Limits
- Maximum file size: 50MB per file
- Supported formats: WAV, MP3, FLAC, M4A, AAC, OGG

### Network Access
The server runs on all interfaces (0.0.0.0:5000) to allow access from:
- Local computer: http://localhost:5000
- Same network devices: http://[your-ip]:5000

### Security Notes
- The server is configured for local network use only
- Uploaded files are automatically cleaned up after processing
- No data is permanently stored on the server

## 📱 Mobile Access

To access from mobile devices:
1. Connect your phone/tablet to the same WiFi network
2. Use the network URL shown when starting the server
3. The interface is responsive and touch-friendly

## 🛠️ Technical Details

### Requirements
- Python 3.6+
- Flask 2.0+
- Neurotec VeriSpeak SDK (automatically detected)
- Linux x86_64 environment

### Architecture
- **Backend**: Flask web framework
- **Voice Processing**: Neurotec VeriSpeak SDK via Python wrapper
- **Frontend**: Bootstrap 5 + JavaScript
- **File Handling**: Temporary files with automatic cleanup

### API Endpoints
- `GET /`: Main web interface
- `POST /verify`: Single voice verification
- `POST /batch_verify`: Batch processing
- `GET /info`: SDK information

## 🐛 Troubleshooting

### Common Issues

**"Cannot locate Neurotec SDK installation"**
- Ensure the Neurotec SDK is properly installed
- Check that the voice verifier works from command line first

**"Permission denied" when starting server**
- Make sure start_server.sh is executable: `chmod +x start_server.sh`

**Cannot access from other devices**
- Check firewall settings
- Ensure devices are on the same network
- Try the IP address shown in the startup message

**File upload fails**
- Check file format is supported
- Ensure file size is under 50MB
- Try a different audio file

### Network Troubleshooting

1. **Find your IP address**:
   ```bash
   hostname -I
   ```

2. **Test local access**:
   ```bash
   curl http://localhost:5000
   ```

3. **Check if port 5000 is open**:
   ```bash
   netstat -tlnp | grep 5000
   ```

## 📊 Example Usage

1. **Record two voice samples** of the same person
2. **Upload both files** via the web interface
3. **Check the result**:
   - Score > 48: Likely same speaker
   - Score > 68: High confidence same speaker
   - Score > 98: Very high confidence same speaker

## 🔐 Security Considerations

- **Local network only**: Not designed for internet access
- **Temporary storage**: Files are deleted immediately after processing
- **No authentication**: Suitable for trusted local networks only
- **No logging**: Voice data is not logged or stored

## 📚 Related Documentation

- [Python Wrapper Documentation](README_Python_Wrapper.md)
- [Neurotec SDK Documentation](Neurotec_Biometric_SDK_Documentation.pdf)
- [Audio Converter Documentation](README_Audio_Converter.md)

---

**🎉 Ready to use!** Start the server and begin verifying voices through your web browser.