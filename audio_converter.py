#!/usr/bin/env python3
"""
Audio Converter for Neurotec Voice Verifier

Converts audio files to the format required by Neurotec VerspeakSDK:
- WAV format
- 16-bit PCM encoding
- Mono (1 channel)
- 16 kHz sample rate
- Removes silence and normalizes audio

Author: Generated for Neurotec SDK Integration
Version: 1.0.0
"""

import os
import sys
import argparse
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class AudioConverter:
    """
    Converts audio files to Neurotec voice verifier compatible format
    
    Uses ffmpeg for audio conversion with optimal settings for voice verification
    """
    
    def __init__(self):
        """Initialize the audio converter"""
        self._check_dependencies()
        
    def _check_dependencies(self):
        """Check if required tools are available"""
        try:
            subprocess.run(['ffmpeg', '-version'], 
                         capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                "ffmpeg is required but not found. Install with:\n"
                "  Ubuntu/Debian: sudo apt install ffmpeg\n"
                "  CentOS/RHEL: sudo yum install ffmpeg\n"
                "  macOS: brew install ffmpeg"
            )
            
    def convert_file(self, input_path: str, output_path: Optional[str] = None,
                    sample_rate: int = 16000, remove_silence: bool = True,
                    normalize: bool = True, overwrite: bool = False) -> str:
        """
        Convert audio file to Neurotec compatible format
        
        Args:
            input_path: Path to input audio file
            output_path: Optional output path (auto-generated if None)
            sample_rate: Target sample rate (16000 or 22050)
            remove_silence: Remove silence from beginning/end
            normalize: Normalize audio levels
            overwrite: Overwrite existing output file
            
        Returns:
            Path to converted audio file
        """
        input_path = Path(input_path).resolve()
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
            
        # Generate output path if not provided
        if output_path is None:
            stem = input_path.stem
            output_path = input_path.parent / f"{stem}_converted.wav"
        else:
            output_path = Path(output_path).resolve()
            
        # Check if output exists and handle overwrite
        if output_path.exists() and not overwrite:
            raise FileExistsError(
                f"Output file exists: {output_path}\n"
                "Use --overwrite to replace it"
            )
            
        # Validate sample rate
        if sample_rate not in [16000, 22050]:
            logger.warning(f"Unusual sample rate: {sample_rate}. "
                          f"Recommended: 16000 or 22050")
            
        logger.info(f"Converting: {input_path.name} -> {output_path.name}")
        
        try:
            # Build ffmpeg command
            cmd = self._build_ffmpeg_command(
                str(input_path), str(output_path), 
                sample_rate, remove_silence, normalize
            )
            
            # Execute conversion
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"Conversion failed:\n{result.stderr}")
                
            # Verify output file was created
            if not output_path.exists():
                raise RuntimeError("Conversion completed but output file not found")
                
            # Get file info
            duration = self._get_audio_duration(str(output_path))
            file_size = output_path.stat().st_size
            
            logger.info(f"✅ Conversion successful:")
            logger.info(f"   Output: {output_path}")
            logger.info(f"   Duration: {duration:.2f} seconds")
            logger.info(f"   Size: {file_size / 1024:.1f} KB")
            
            return str(output_path)
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Conversion timed out after 5 minutes")
        except Exception as e:
            # Clean up partial output file
            if output_path.exists():
                output_path.unlink()
            raise RuntimeError(f"Conversion error: {e}")
            
    def _build_ffmpeg_command(self, input_path: str, output_path: str,
                             sample_rate: int, remove_silence: bool,
                             normalize: bool) -> List[str]:
        """Build ffmpeg command with appropriate filters"""
        
        cmd = ['ffmpeg', '-i', input_path]
        
        # Build audio filter chain
        filters = []
        
        # Remove silence from beginning and end
        if remove_silence:
            filters.append('silenceremove=start_periods=1:start_silence=0.1:start_threshold=-50dB')
            filters.append('areverse')
            filters.append('silenceremove=start_periods=1:start_silence=0.1:start_threshold=-50dB')
            filters.append('areverse')
            
        # Normalize audio levels
        if normalize:
            filters.append('loudnorm=I=-16:TP=-1.5:LRA=11')
            
        # Apply filters if any
        if filters:
            cmd.extend(['-af', ','.join(filters)])
            
        # Audio format settings
        cmd.extend([
            '-ac', '1',              # Mono (1 channel)
            '-ar', str(sample_rate), # Sample rate
            '-acodec', 'pcm_s16le',  # 16-bit PCM
            '-f', 'wav',             # WAV format
            '-y',                    # Overwrite output
            output_path
        ])
        
        return cmd
        
    def _get_audio_duration(self, file_path: str) -> float:
        """Get audio file duration in seconds"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-show_entries', 
                'format=duration', '-of', 'csv=p=0', file_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return float(result.stdout.strip())
        except:
            return 0.0
            
    def get_audio_info(self, file_path: str) -> dict:
        """Get detailed audio file information"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', file_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            import json
            info = json.loads(result.stdout)
            
            # Extract audio stream info
            audio_stream = None
            for stream in info.get('streams', []):
                if stream.get('codec_type') == 'audio':
                    audio_stream = stream
                    break
                    
            if not audio_stream:
                return {'error': 'No audio stream found'}
                
            format_info = info.get('format', {})
            
            return {
                'duration': float(format_info.get('duration', 0)),
                'size': int(format_info.get('size', 0)),
                'sample_rate': int(audio_stream.get('sample_rate', 0)),
                'channels': int(audio_stream.get('channels', 0)),
                'codec': audio_stream.get('codec_name', 'unknown'),
                'bit_rate': int(audio_stream.get('bit_rate', 0)),
                'format': format_info.get('format_name', 'unknown')
            }
            
        except Exception as e:
            return {'error': str(e)}
            
    def batch_convert(self, input_files: List[str], output_dir: Optional[str] = None,
                     **kwargs) -> List[Tuple[str, str]]:
        """
        Convert multiple audio files
        
        Args:
            input_files: List of input file paths
            output_dir: Output directory (uses input file directories if None)
            **kwargs: Additional arguments for convert_file
            
        Returns:
            List of (input_path, output_path) tuples
        """
        results = []
        
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
        for i, input_file in enumerate(input_files):
            try:
                input_path = Path(input_file)
                
                if output_dir:
                    output_path = output_dir / f"{input_path.stem}_converted.wav"
                else:
                    output_path = None
                    
                logger.info(f"Processing {i+1}/{len(input_files)}: {input_path.name}")
                
                converted_path = self.convert_file(
                    str(input_path), 
                    str(output_path) if output_path else None,
                    **kwargs
                )
                
                results.append((str(input_path), converted_path))
                
            except Exception as e:
                logger.error(f"Failed to convert {input_file}: {e}")
                results.append((str(input_file), None))
                
        return results
        
    def validate_for_neurotec(self, file_path: str) -> dict:
        """
        Validate if audio file meets Neurotec requirements
        
        Returns:
            Dictionary with validation results
        """
        info = self.get_audio_info(file_path)
        
        if 'error' in info:
            return {'valid': False, 'errors': [info['error']]}
            
        errors = []
        warnings = []
        
        # Check sample rate
        if info['sample_rate'] not in [16000, 22050]:
            errors.append(f"Sample rate {info['sample_rate']} not supported (need 16000 or 22050)")
            
        # Check channels
        if info['channels'] != 1:
            errors.append(f"Must be mono (1 channel), found {info['channels']} channels")
            
        # Check duration
        if info['duration'] < 3:
            warnings.append(f"Duration {info['duration']:.1f}s is short (recommend >3s)")
        elif info['duration'] > 300:
            warnings.append(f"Duration {info['duration']:.1f}s is long (may be slow to process)")
            
        # Check format
        if not file_path.lower().endswith('.wav'):
            warnings.append("WAV format is preferred for best compatibility")
            
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'info': info
        }


def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(
        description='Convert audio files for Neurotec Voice Verifier',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python audio_converter.py input.mp3
  python audio_converter.py input.wav -o output.wav --sample-rate 22050
  python audio_converter.py *.mp3 -d converted/
  python audio_converter.py --validate input.wav
        """
    )
    
    parser.add_argument('input_files', nargs='*', help='Input audio files')
    parser.add_argument('-o', '--output', help='Output file path (single file mode)')
    parser.add_argument('-d', '--output-dir', help='Output directory (batch mode)')
    parser.add_argument('--sample-rate', type=int, default=16000, 
                       choices=[16000, 22050], help='Target sample rate')
    parser.add_argument('--no-silence-removal', action='store_true',
                       help='Skip silence removal')
    parser.add_argument('--no-normalize', action='store_true',
                       help='Skip audio normalization')
    parser.add_argument('--overwrite', action='store_true',
                       help='Overwrite existing output files')
    parser.add_argument('--validate', action='store_true',
                       help='Validate files for Neurotec compatibility')
    parser.add_argument('--info', action='store_true',
                       help='Show audio file information')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        
    if not args.input_files:
        parser.error("No input files specified")
        
    try:
        converter = AudioConverter()
        
        # Handle single file operations
        if len(args.input_files) == 1 and not args.output_dir:
            input_file = args.input_files[0]
            
            if args.validate:
                result = converter.validate_for_neurotec(input_file)
                print(f"\n🔍 Validation Results for {Path(input_file).name}")
                print("=" * 50)
                print(f"Status: {'✅ VALID' if result['valid'] else '❌ INVALID'}")
                
                if result['errors']:
                    print("\n❌ Errors:")
                    for error in result['errors']:
                        print(f"  - {error}")
                        
                if result['warnings']:
                    print("\n⚠️  Warnings:")
                    for warning in result['warnings']:
                        print(f"  - {warning}")
                        
                if 'info' in result:
                    info = result['info']
                    print("\n📊 Audio Information:")
                    print(f"  Duration: {info['duration']:.2f} seconds")
                    print(f"  Sample Rate: {info['sample_rate']} Hz")
                    print(f"  Channels: {info['channels']}")
                    print(f"  Codec: {info['codec']}")
                    print(f"  Size: {info['size'] / 1024:.1f} KB")
                return
                
            if args.info:
                info = converter.get_audio_info(input_file)
                if 'error' in info:
                    print(f"❌ Error: {info['error']}")
                    return
                    
                print(f"\n📊 Audio Information for {Path(input_file).name}")
                print("=" * 50)
                print(f"Duration: {info['duration']:.2f} seconds")
                print(f"Sample Rate: {info['sample_rate']} Hz")
                print(f"Channels: {info['channels']}")
                print(f"Codec: {info['codec']}")
                print(f"Format: {info['format']}")
                print(f"Bit Rate: {info['bit_rate']} bps")
                print(f"Size: {info['size'] / 1024:.1f} KB")
                return
                
            # Convert single file
            output_path = converter.convert_file(
                input_file,
                args.output,
                sample_rate=args.sample_rate,
                remove_silence=not args.no_silence_removal,
                normalize=not args.no_normalize,
                overwrite=args.overwrite
            )
            
            print(f"\n✅ Conversion completed: {output_path}")
            
        else:
            # Batch conversion
            if args.validate:
                print("\n🔍 Batch Validation Results")
                print("=" * 50)
                for input_file in args.input_files:
                    result = converter.validate_for_neurotec(input_file)
                    status = "✅ VALID" if result['valid'] else "❌ INVALID"
                    print(f"{Path(input_file).name}: {status}")
                    if result['errors']:
                        for error in result['errors']:
                            print(f"    ❌ {error}")
                return
                
            results = converter.batch_convert(
                args.input_files,
                args.output_dir,
                sample_rate=args.sample_rate,
                remove_silence=not args.no_silence_removal,
                normalize=not args.no_normalize,
                overwrite=args.overwrite
            )
            
            print(f"\n📊 Batch Conversion Results")
            print("=" * 50)
            
            successful = 0
            for input_path, output_path in results:
                if output_path:
                    print(f"✅ {Path(input_path).name} -> {Path(output_path).name}")
                    successful += 1
                else:
                    print(f"❌ {Path(input_path).name} -> FAILED")
                    
            print(f"\nCompleted: {successful}/{len(results)} files successfully converted")
            
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()