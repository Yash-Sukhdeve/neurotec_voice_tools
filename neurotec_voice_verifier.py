#!/usr/bin/env python3
"""
Neurotec VerspeakSDK Voice Verification Python Wrapper

This script provides a portable Python interface to the Neurotec VerspeakSDK 
C++ voice verification application. It can be run from any location and 
automatically handles SDK discovery, library paths, and result parsing.

Author: Generated for Neurotec SDK Integration
Version: 1.0.0
"""

import os
import sys
import subprocess
import json
import argparse
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, NamedTuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class VoiceVerificationResult(NamedTuple):
    """Structured result from voice verification"""
    success: bool
    score: Optional[int]
    threshold: int
    verification_status: str  # 'succeeded', 'failed', 'error'
    far_percentage: float
    confidence_level: str  # 'low', 'medium', 'high', 'very_high'
    reference_file: str
    candidate_file: str
    raw_output: str
    error_message: Optional[str] = None


class NeurotecVoiceVerifier:
    """
    Portable wrapper for Neurotec VerspeakSDK C++ voice verification
    
    Automatically discovers SDK installation, handles library paths,
    and provides clean Python interface for voice verification tasks.
    """
    
    def __init__(self, sdk_root: Optional[str] = None):
        """
        Initialize the voice verifier
        
        Args:
            sdk_root: Optional path to SDK root. If None, auto-discovers.
        """
        self.sdk_root = sdk_root or self._find_sdk_root()
        self.cpp_binary_path = None
        self.library_path = None
        
        if not self.sdk_root:
            raise RuntimeError("Cannot locate Neurotec SDK installation")
            
        logger.info(f"Using SDK root: {self.sdk_root}")
        
        # Setup paths
        self._setup_paths()
        
    def _find_sdk_root(self) -> Optional[str]:
        """
        Automatically discover Neurotec SDK installation
        
        Searches common locations and current directory tree
        """
        search_paths = [
            # Current directory and parents
            Path.cwd(),
            Path.cwd().parent,
            Path.cwd().parent.parent,
            
            # Common installation locations
            Path("/opt/neurotec"),
            Path("/usr/local/neurotec"), 
            Path.home() / "neurotec",
            Path.home() / "Desktop",
            
            # Check if we're inside the SDK
            *[p for p in Path.cwd().parents if "neurotec" in str(p).lower()]
        ]
        
        for search_path in search_paths:
            for sdk_candidate in search_path.rglob("*Neurotec_Biometric*SDK*"):
                if sdk_candidate.is_dir():
                    # Verify it's a valid SDK by checking for key directories
                    if (sdk_candidate / "Tutorials" / "Biometrics" / "CPP").exists():
                        return str(sdk_candidate)
                        
        logger.warning("SDK auto-discovery failed. Searched paths:")
        for path in search_paths:
            logger.warning(f"  - {path}")
        return None
        
    def _setup_paths(self):
        """Setup binary and library paths"""
        sdk_path = Path(self.sdk_root)
        
        # Find C++ binary
        cpp_tutorial_dir = sdk_path / "Tutorials" / "Biometrics" / "CPP" / "VerifyVoiceCPP"
        if not cpp_tutorial_dir.exists():
            raise RuntimeError(f"VerifyVoiceCPP directory not found: {cpp_tutorial_dir}")
            
        # Check for compiled binary
        binary_candidates = [
            cpp_tutorial_dir / "VerifyVoiceCPP",
            cpp_tutorial_dir / ".obj" / "release" / "Linux_x86_64" / "VerifyVoiceCPP" / "VerifyVoiceCPP"
        ]
        
        for binary_path in binary_candidates:
            if binary_path.exists() and os.access(binary_path, os.X_OK):
                self.cpp_binary_path = str(binary_path)
                break
        
        if not self.cpp_binary_path:
            logger.warning("Compiled binary not found. Attempting to compile...")
            self._compile_cpp_binary(cpp_tutorial_dir)
            
        # Setup library path
        lib_dir = sdk_path / "Lib" / "Linux_x86_64"
        if lib_dir.exists():
            self.library_path = str(lib_dir)
        else:
            logger.warning(f"Library directory not found: {lib_dir}")
            
    def _compile_cpp_binary(self, cpp_dir: Path):
        """Attempt to compile the C++ binary"""
        logger.info("Compiling VerifyVoiceCPP...")
        
        # Ensure we have the trial flag
        self._setup_trial_flag()
        
        try:
            result = subprocess.run(
                ["make"],
                cwd=str(cpp_dir),
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                # Check for the binary again
                binary_path = cpp_dir / "VerifyVoiceCPP"
                if binary_path.exists():
                    self.cpp_binary_path = str(binary_path)
                    logger.info("Compilation successful")
                else:
                    raise RuntimeError("Compilation succeeded but binary not found")
            else:
                raise RuntimeError(f"Compilation failed:\n{result.stderr}")
                
        except subprocess.TimeoutExpired:
            raise RuntimeError("Compilation timed out after 2 minutes")
        except FileNotFoundError:
            raise RuntimeError("Make command not found. Please install build tools.")
            
    def _setup_trial_flag(self):
        """Ensure trial flag is properly set up for relative paths"""
        sdk_path = Path(self.sdk_root)
        cpp_tutorial_dir = sdk_path / "Tutorials" / "Biometrics" / "CPP" / "VerifyVoiceCPP"
        
        # Create relative path structure expected by the C++ app
        licenses_dir = cpp_tutorial_dir / ".." / ".." / ".." / ".." / "Lib" / "Licenses"
        licenses_dir = licenses_dir.resolve()
        
        if not licenses_dir.exists():
            licenses_dir.mkdir(parents=True, exist_ok=True)
            
        trial_flag_file = licenses_dir / "TrialFlag.txt"
        source_trial_flag = sdk_path / "Bin" / "Licenses" / "TrialFlag.txt"
        
        if source_trial_flag.exists() and not trial_flag_file.exists():
            import shutil
            shutil.copy2(source_trial_flag, trial_flag_file)
            logger.info(f"Copied trial flag to: {trial_flag_file}")
            
    def verify_voices(self, reference_file: str, candidate_file: str, 
                     custom_threshold: Optional[int] = None) -> VoiceVerificationResult:
        """
        Perform voice verification between two audio files
        
        Args:
            reference_file: Path to reference audio file
            candidate_file: Path to candidate audio file  
            custom_threshold: Optional custom threshold (default: 48)
            
        Returns:
            VoiceVerificationResult with detailed results
        """
        if not self.cpp_binary_path:
            raise RuntimeError("C++ binary not available")
            
        # Resolve file paths to absolute paths
        ref_path = Path(reference_file).resolve()
        cand_path = Path(candidate_file).resolve()
        
        if not ref_path.exists():
            raise FileNotFoundError(f"Reference file not found: {ref_path}")
        if not cand_path.exists():
            raise FileNotFoundError(f"Candidate file not found: {cand_path}")
            
        # Setup environment
        env = os.environ.copy()
        if self.library_path:
            current_ld_path = env.get('LD_LIBRARY_PATH', '')
            env['LD_LIBRARY_PATH'] = f"{self.library_path}:{current_ld_path}" if current_ld_path else self.library_path
            
        # Execute verification
        cmd = [self.cpp_binary_path, str(ref_path), str(cand_path)]
        
        logger.info(f"Executing: {' '.join(cmd)}")
        logger.info(f"Library path: {env.get('LD_LIBRARY_PATH', 'Not set')}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
                timeout=60
            )
            
            return self._parse_result(result, str(ref_path), str(cand_path))
            
        except subprocess.TimeoutExpired:
            return VoiceVerificationResult(
                success=False,
                score=None,
                threshold=48,
                verification_status='error',
                far_percentage=0.01,
                confidence_level='low',
                reference_file=str(ref_path),
                candidate_file=str(cand_path),
                raw_output='',
                error_message='Verification timed out after 60 seconds'
            )
        except Exception as e:
            return VoiceVerificationResult(
                success=False,
                score=None,
                threshold=48,
                verification_status='error',
                far_percentage=0.01,
                confidence_level='low',
                reference_file=str(ref_path),
                candidate_file=str(cand_path),
                raw_output='',
                error_message=str(e)
            )
            
    def _parse_result(self, result: subprocess.CompletedProcess, 
                     ref_file: str, cand_file: str) -> VoiceVerificationResult:
        """Parse C++ application output into structured result"""
        
        output = result.stdout
        stderr = result.stderr
        
        if result.returncode != 0:
            return VoiceVerificationResult(
                success=False,
                score=None,
                threshold=48,
                verification_status='error',
                far_percentage=0.01,
                confidence_level='low',
                reference_file=ref_file,
                candidate_file=cand_file,
                raw_output=output + stderr,
                error_message=f"Process failed with return code {result.returncode}"
            )
            
        # Parse output for score and status
        score_match = re.search(r'Voice score:\s*(\d+)', output)
        status_match = re.search(r'verification\s+(succeeded|failed)', output)
        threshold_match = re.search(r'Trial mode:\s*1', output)  # Indicates success
        
        if not score_match or not status_match:
            return VoiceVerificationResult(
                success=False,
                score=None,
                threshold=48,
                verification_status='error',
                far_percentage=0.01,
                confidence_level='low',
                reference_file=ref_file,
                candidate_file=cand_file,
                raw_output=output,
                error_message="Failed to parse verification output"
            )
            
        score = int(score_match.group(1))
        status = status_match.group(1)
        threshold = 48  # Default threshold used by the C++ app
        
        # Calculate confidence level based on score relative to threshold
        if score < threshold:
            confidence = 'low'
        elif score < threshold + 20:
            confidence = 'medium'
        elif score < threshold + 50:
            confidence = 'high'
        else:
            confidence = 'very_high'
            
        return VoiceVerificationResult(
            success=True,
            score=score,
            threshold=threshold,
            verification_status=status,
            far_percentage=0.01,  # Default 0.01% FAR for threshold 48
            confidence_level=confidence,
            reference_file=ref_file,
            candidate_file=cand_file,
            raw_output=output,
            error_message=None
        )
        
    def batch_verify(self, file_pairs: List[Tuple[str, str]]) -> List[VoiceVerificationResult]:
        """
        Perform batch voice verification on multiple file pairs
        
        Args:
            file_pairs: List of (reference_file, candidate_file) tuples
            
        Returns:
            List of VoiceVerificationResult objects
        """
        results = []
        
        for i, (ref_file, cand_file) in enumerate(file_pairs):
            logger.info(f"Processing pair {i+1}/{len(file_pairs)}: {Path(ref_file).name} vs {Path(cand_file).name}")
            result = self.verify_voices(ref_file, cand_file)
            results.append(result)
            
        return results
        
    def get_info(self) -> Dict[str, str]:
        """Get information about the SDK and binary"""
        return {
            'sdk_root': self.sdk_root,
            'cpp_binary': self.cpp_binary_path,
            'library_path': self.library_path,
            'binary_exists': os.path.exists(self.cpp_binary_path) if self.cpp_binary_path else False,
            'library_exists': os.path.exists(self.library_path) if self.library_path else False
        }


def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(
        description='Neurotec VerspeakSDK Voice Verification Python Wrapper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python neurotec_voice_verifier.py audio1.wav audio2.wav
  python neurotec_voice_verifier.py -s /path/to/sdk audio1.wav audio2.wav
  python neurotec_voice_verifier.py --info
        """
    )
    
    parser.add_argument('reference_file', nargs='?', help='Reference audio file')
    parser.add_argument('candidate_file', nargs='?', help='Candidate audio file') 
    parser.add_argument('-s', '--sdk-root', help='Path to Neurotec SDK root directory')
    parser.add_argument('--info', action='store_true', help='Show SDK information and exit')
    parser.add_argument('--json', action='store_true', help='Output results in JSON format')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        
    try:
        verifier = NeurotecVoiceVerifier(args.sdk_root)
        
        if args.info:
            info = verifier.get_info()
            if args.json:
                print(json.dumps(info, indent=2))
            else:
                print("Neurotec SDK Information:")
                for key, value in info.items():
                    print(f"  {key}: {value}")
            return
            
        if not args.reference_file or not args.candidate_file:
            parser.error("Reference and candidate files are required")
            
        result = verifier.verify_voices(args.reference_file, args.candidate_file)
        
        if args.json:
            print(json.dumps(result._asdict(), indent=2, default=str))
        else:
            print(f"\n🎙️  Voice Verification Results")
            print(f"={'='*50}")
            print(f"Reference File: {Path(result.reference_file).name}")
            print(f"Candidate File: {Path(result.candidate_file).name}")
            print(f"")
            print(f"Verification Score: {result.score}")
            print(f"Threshold: {result.threshold} (FAR: {result.far_percentage}%)")
            print(f"Status: {'✅ MATCH' if result.verification_status == 'succeeded' else '❌ NO MATCH'}")
            print(f"Confidence: {result.confidence_level.replace('_', ' ').title()}")
            print(f"")
            if result.error_message:
                print(f"❌ Error: {result.error_message}")
            else:
                print(f"✅ Success: Voice verification completed")
                
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()