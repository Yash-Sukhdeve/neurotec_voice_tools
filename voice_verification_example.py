#!/usr/bin/env python3
"""
Example usage of Neurotec Voice Verification Python Wrapper

This demonstrates how to use the neurotec_voice_verifier.py script
programmatically from other Python applications.
"""

from neurotec_voice_verifier import NeurotecVoiceVerifier, VoiceVerificationResult
from pathlib import Path


def main():
    """Demonstrate voice verification usage"""
    
    # Initialize verifier (auto-discovers SDK)
    print("🔍 Initializing Neurotec Voice Verifier...")
    verifier = NeurotecVoiceVerifier()
    
    # Show SDK info
    info = verifier.get_info()
    print(f"📁 SDK Root: {info['sdk_root']}")
    print(f"🔧 Binary: {Path(info['cpp_binary']).name}")
    print()
    
    # Test files (adjust paths as needed)
    reference_file = "chunk_1_lc0.wav"
    candidate_file = "chunk_1_lc1.wav"
    
    if not Path(reference_file).exists() or not Path(candidate_file).exists():
        print("❌ Audio files not found in current directory")
        print("   Please run from directory containing chunk_1_lc0.wav and chunk_1_lc1.wav")
        return
    
    print(f"🎙️  Verifying voices...")
    print(f"   Reference: {reference_file}")
    print(f"   Candidate: {candidate_file}")
    print()
    
    # Perform verification
    result = verifier.verify_voices(reference_file, candidate_file)
    
    # Display results
    if result.success:
        print("✅ Verification completed successfully!")
        print(f"   Score: {result.score}")
        print(f"   Threshold: {result.threshold}")
        print(f"   Status: {result.verification_status.upper()}")
        print(f"   Confidence: {result.confidence_level.replace('_', ' ').title()}")
        print(f"   FAR: {result.far_percentage}%")
        
        # Interpret the result
        if result.verification_status == "succeeded":
            print(f"🎯 Result: Same speaker detected with {result.confidence_level.replace('_', ' ')} confidence")
        else:
            print(f"🚫 Result: Different speakers detected")
            
    else:
        print("❌ Verification failed!")
        if result.error_message:
            print(f"   Error: {result.error_message}")
            
    print()
    print("Raw C++ output:")
    print("-" * 50)
    print(result.raw_output)


def batch_example():
    """Demonstrate batch processing"""
    print("\n🔄 Batch Processing Example")
    print("=" * 40)
    
    verifier = NeurotecVoiceVerifier()
    
    # Example file pairs (adjust as needed)
    file_pairs = [
        ("chunk_1_lc0.wav", "chunk_1_lc1.wav"),
        # Add more pairs as needed
    ]
    
    results = verifier.batch_verify(file_pairs)
    
    print(f"\n📊 Batch Results Summary:")
    for i, result in enumerate(results):
        ref_name = Path(result.reference_file).name
        cand_name = Path(result.candidate_file).name
        status = "✅ MATCH" if result.verification_status == "succeeded" else "❌ NO MATCH"
        print(f"   {i+1}. {ref_name} vs {cand_name}: {status} (Score: {result.score})")


if __name__ == "__main__":
    main()
    batch_example()