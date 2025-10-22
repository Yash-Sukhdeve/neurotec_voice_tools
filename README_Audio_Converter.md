# Audio Converter for Neurotec Voice Verifier

Converts audio files to the exact format required by `neurotec_voice_verifier.py`:
- **WAV format** with 16-bit PCM encoding
- **Mono (1 channel)** audio
- **16 kHz or 22.05 kHz** sample rate
- **Optimized for voice** with silence removal and normalization

## ✅ Features

- 🎵 **Universal Input** - Supports MP3, WAV, M4A, FLAC, and most audio formats
- 🔧 **Smart Processing** - Removes silence, normalizes levels, converts to mono
- ✅ **Validation** - Check if files already meet Neurotec requirements
- 📊 **Batch Processing** - Convert multiple files at once
- 🔍 **Audio Analysis** - Get detailed file information
- 🎯 **Optimized Output** - Perfect format for voice verification

## 🚀 Quick Start

### Convert Single File
```bash
python3 audio_converter.py input.mp3
# Creates: input_converted.wav
```

### Convert with Custom Output
```bash
python3 audio_converter.py speech.m4a -o clean_speech.wav
```

### Batch Convert Multiple Files
```bash
python3 audio_converter.py *.mp3 -d converted_files/
```

### Validate Files for Neurotec
```bash
python3 audio_converter.py --validate audio1.wav audio2.mp3
```

## 📖 Detailed Usage

### Validation Mode
Check if files meet Neurotec requirements without converting:
```bash
python3 audio_converter.py --validate *.wav
```
**Output:**
```
🔍 Batch Validation Results
==================================================
reference.wav: ✅ VALID
stereo_file.wav: ❌ INVALID
    ❌ Must be mono (1 channel), found 2 channels
```

### Audio Information
Get detailed technical information:
```bash
python3 audio_converter.py --info speech.mp3
```
**Output:**
```
📊 Audio Information for speech.mp3
==================================================
Duration: 45.23 seconds
Sample Rate: 44100 Hz
Channels: 2
Codec: mp3
Format: mp3
Bit Rate: 320000 bps
Size: 1845.7 KB
```

### Conversion Options
```bash
# Use 22.05 kHz instead of 16 kHz
python3 audio_converter.py input.mp3 --sample-rate 22050

# Skip silence removal (keep original duration)
python3 audio_converter.py input.wav --no-silence-removal

# Skip normalization (keep original levels)  
python3 audio_converter.py input.mp3 --no-normalize

# Overwrite existing output files
python3 audio_converter.py input.mp3 --overwrite
```

## 🎯 Perfect for These Scenarios

### 1. **Different Input Formats**
```bash
# Convert from various formats
python3 audio_converter.py interview.m4a    # iPhone recording
python3 audio_converter.py call.mp3         # Phone call
python3 audio_converter.py meeting.flac     # High-quality recording
```

### 2. **Stereo to Mono Conversion**
```bash
# Converts stereo recordings to mono
python3 audio_converter.py stereo_interview.wav
```

### 3. **Sample Rate Conversion**
```bash
# Convert 44.1kHz music to 16kHz voice
python3 audio_converter.py music_with_speech.wav
```

### 4. **Noise Cleanup**
```bash
# Removes silence and normalizes levels
python3 audio_converter.py noisy_recording.mp3
```

## ⚙️ Advanced Processing

The converter automatically applies these optimizations:

### **Silence Removal**
- Removes quiet sections from beginning and end
- Threshold: -50dB
- Keeps speech content intact

### **Audio Normalization**  
- Loudness: -16 LUFS (optimal for speech)
- True Peak: -1.5 dBFS (prevents clipping)
- Dynamic range: 11 LU (preserves speech clarity)

### **Format Conversion**
- Converts to WAV with PCM encoding
- Downmixes stereo/surround to mono
- Resamples to 16kHz or 22.05kHz

## 🔧 Requirements

- **Python 3.6+**
- **ffmpeg** (for audio processing)

### Install ffmpeg:
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# CentOS/RHEL  
sudo yum install ffmpeg

# macOS
brew install ffmpeg
```

## 📊 Before/After Examples

### Example 1: MP3 to Neurotec Format
**Input:** `interview.mp3` (44.1kHz, stereo, 5.2MB)
```bash
python3 audio_converter.py interview.mp3
```
**Output:** `interview_converted.wav` (16kHz, mono, 1.8MB)

### Example 2: Validation Check
**Input:** Mixed file formats
```bash
python3 audio_converter.py --validate *.wav *.mp3
```
**Output:**
```
reference.wav: ✅ VALID
stereo_music.mp3: ❌ INVALID
    ❌ Must be mono (1 channel), found 2 channels  
    ❌ Sample rate 44100 not supported (need 16000 or 22050)
```

## 🔄 Integration with Neurotec Verifier

### Workflow Example
```bash
# 1. Convert audio files to compatible format
python3 audio_converter.py speaker1.mp3 speaker2.m4a

# 2. Verify the converted files  
python3 neurotec_voice_verifier.py speaker1_converted.wav speaker2_converted.wav
```

### Batch Processing Pipeline
```bash
# Convert all files in a directory
python3 audio_converter.py audio_samples/*.mp3 -d converted/

# Run verification on all converted pairs
for file in converted/*.wav; do
    python3 neurotec_voice_verifier.py reference.wav "$file"
done
```

## 🎵 Supported Input Formats

- **Audio:** MP3, WAV, FLAC, AAC, M4A, OGG, WMA
- **Video:** MP4, AVI, MOV, MKV (extracts audio track)
- **Professional:** AIFF, AU, CAF, BWF

## ✅ Output Guarantees

Every converted file will have:
- ✅ **WAV format** (PCM 16-bit)  
- ✅ **Mono channel** (1 channel)
- ✅ **16kHz or 22.05kHz** sample rate
- ✅ **Optimized for speech** processing
- ✅ **Compatible** with Neurotec voice verifier

## 🐛 Error Handling

The converter handles common issues:
- ❌ **Missing ffmpeg** → Clear installation instructions
- ❌ **Corrupted files** → Detailed error messages  
- ❌ **Unsupported formats** → Format recommendations
- ❌ **Large files** → Progress indication and timeout protection
- ❌ **Existing outputs** → Overwrite protection

## 🚀 Ready to Use

The audio converter is ready to process your files for Neurotec voice verification!

```bash
# Quick test
python3 audio_converter.py --validate reference.wav
# Result: ✅ VALID

# Convert any audio file
python3 audio_converter.py your_audio.mp3
# Creates: your_audio_converted.wav (ready for Neurotec)
```