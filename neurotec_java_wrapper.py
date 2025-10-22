#!/usr/bin/env python3
"""
Neurotec Voice Verification Java Wrapper
Uses the working Java implementation with proper licensing
"""

import os
import sys
import subprocess
import json
import argparse
import re
from pathlib import Path
from typing import Dict, Optional, NamedTuple
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class VoiceVerificationResult(NamedTuple):
    """Structured result from voice verification"""
    success: bool
    score: Optional[int]
    threshold: int
    verification_status: str
    reference_file: str
    candidate_file: str
    raw_output: str
    error_message: Optional[str] = None

class NeurotecJavaVoiceVerifier:
    """Java-based Neurotec voice verifier with proper licensing"""

    def __init__(self, sdk_root: Optional[str] = None):
        self.sdk_root = sdk_root or self._find_sdk_root()
        if not self.sdk_root:
            raise RuntimeError("Cannot locate Neurotec SDK installation")

        self.java_dir = Path(self.sdk_root) / "Tutorials" / "Biometrics" / "Java" / "verify-voice"
        self.lib_dir = Path(self.sdk_root) / "Lib" / "Linux_x86_64"
        self.java_lib_dir = Path(self.sdk_root) / "Bin" / "Java"

        if not self.java_dir.exists():
            raise RuntimeError(f"Java verify-voice directory not found: {self.java_dir}")
        if not self.lib_dir.exists():
            raise RuntimeError(f"Native library directory not found: {self.lib_dir}")
        if not self.java_lib_dir.exists():
            raise RuntimeError(f"Java library directory not found: {self.java_lib_dir}")

        # Ensure SimpleVerifyVoice is compiled
        self._ensure_compiled()

    def _find_sdk_root(self) -> Optional[str]:
        """Find SDK root directory"""
        search_paths = [
            Path.cwd(),
            Path.cwd().parent,
            Path.cwd().parent.parent,
            Path("/home/lab2208/Desktop"),
            *[p for p in Path.cwd().parents if "neurotec" in str(p).lower()]
        ]

        for search_path in search_paths:
            for sdk_candidate in search_path.rglob("*Neurotec_Biometric*SDK*"):
                if sdk_candidate.is_dir():
                    if (sdk_candidate / "Tutorials" / "Biometrics" / "Java").exists():
                        return str(sdk_candidate)
        return None

    def _ensure_compiled(self):
        """Ensure SimpleVerifyVoice.class exists"""
        class_file = self.java_dir / "SimpleVerifyVoice.class"
        java_file = self.java_dir / "SimpleVerifyVoice.java"

        if not class_file.exists() or not java_file.exists():
            logger.info("Compiling SimpleVerifyVoice...")
            try:
                result = subprocess.run([
                    "javac", "-cp", f"{self.java_lib_dir}/*", str(java_file)
                ], cwd=str(self.java_dir), capture_output=True, text=True, timeout=60)

                if result.returncode != 0:
                    raise RuntimeError(f"Java compilation failed: {result.stderr}")

            except FileNotFoundError:
                raise RuntimeError("Java compiler (javac) not found")
            except subprocess.TimeoutExpired:
                raise RuntimeError("Java compilation timed out")

    def verify_voices(self, reference_file: str, candidate_file: str) -> VoiceVerificationResult:
        """Perform voice verification using Java implementation"""
        ref_path = Path(reference_file).resolve()
        cand_path = Path(candidate_file).resolve()

        if not ref_path.exists():
            raise FileNotFoundError(f"Reference file not found: {ref_path}")
        if not cand_path.exists():
            raise FileNotFoundError(f"Candidate file not found: {cand_path}")

        # Setup environment
        env = os.environ.copy()
        current_ld_path = env.get('LD_LIBRARY_PATH', '')
        env['LD_LIBRARY_PATH'] = f"{self.lib_dir}:{current_ld_path}" if current_ld_path else str(self.lib_dir)

        # Java command
        cmd = [
            "java",
            f"-Djava.library.path={self.lib_dir}",
            "-cp", f"{self.java_lib_dir}/*:.",
            "SimpleVerifyVoice",
            str(ref_path),
            str(cand_path)
        ]

        logger.info(f"Executing Java verification...")

        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.java_dir),
                capture_output=True,
                text=True,
                env=env,
                timeout=120
            )

            return self._parse_result(result, str(ref_path), str(cand_path))

        except subprocess.TimeoutExpired:
            return VoiceVerificationResult(
                success=False,
                score=None,
                threshold=48,
                verification_status='error',
                reference_file=str(ref_path),
                candidate_file=str(cand_path),
                raw_output='',
                error_message='Verification timed out'
            )
        except Exception as e:
            return VoiceVerificationResult(
                success=False,
                score=None,
                threshold=48,
                verification_status='error',
                reference_file=str(ref_path),
                candidate_file=str(cand_path),
                raw_output='',
                error_message=str(e)
            )

    def _parse_result(self, result: subprocess.CompletedProcess, ref_file: str, cand_file: str) -> VoiceVerificationResult:
        """Parse Java output"""
        output = result.stdout
        stderr = result.stderr

        if result.returncode != 0:
            return VoiceVerificationResult(
                success=False,
                score=None,
                threshold=48,
                verification_status='error',
                reference_file=ref_file,
                candidate_file=cand_file,
                raw_output=output + stderr,
                error_message=f"Process failed with return code {result.returncode}"
            )

        # Parse for score and status
        score_match = re.search(r'Voice scored (\d+)', output)
        status_match = re.search(r'verification (succeeded|failed)', output)

        if not score_match:
            return VoiceVerificationResult(
                success=False,
                score=None,
                threshold=48,
                verification_status='error',
                reference_file=ref_file,
                candidate_file=cand_file,
                raw_output=output,
                error_message="Failed to parse verification score"
            )

        score = int(score_match.group(1))
        status = status_match.group(1) if status_match else 'unknown'

        return VoiceVerificationResult(
            success=True,
            score=score,
            threshold=48,
            verification_status=status,
            reference_file=ref_file,
            candidate_file=cand_file,
            raw_output=output,
            error_message=None
        )

def main():
    parser = argparse.ArgumentParser(description='Neurotec Java Voice Verification Wrapper')
    parser.add_argument('reference_file', help='Reference audio file')
    parser.add_argument('candidate_file', help='Candidate audio file')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        verifier = NeurotecJavaVoiceVerifier()
        result = verifier.verify_voices(args.reference_file, args.candidate_file)

        if args.json:
            print(json.dumps(result._asdict(), indent=2, default=str))
        else:
            print(f"\n🎙️  Voice Verification Results")
            print(f"{'='*50}")
            print(f"Reference File: {Path(result.reference_file).name}")
            print(f"Candidate File: {Path(result.candidate_file).name}")
            print(f"")
            print(f"Verification Score: {result.score}")
            print(f"Threshold: {result.threshold}")
            print(f"Status: {'✅ MATCH' if result.verification_status == 'succeeded' else '❌ NO MATCH'}")

            if result.error_message:
                print(f"❌ Error: {result.error_message}")
            else:
                print(f"✅ Success: Voice verification completed")

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()