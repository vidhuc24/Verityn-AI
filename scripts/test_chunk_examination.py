#!/usr/bin/env python3
"""
Focused Chunk Examination Test
This script examines the content of each chunk to identify chunking issues.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.services.vector_database import VectorDatabaseService

class ChunkExaminer:
    def __init__(self):
        self.vector_db = VectorDatabaseService(use_memory=True)
        # Use the document ID from the previous test
        self.document_id = "90409afb-51e1-4f67-9281-fcab7f75318d"
        
    async def examine_chunk_content(self):
        """Examine the content of each chunk to identify chunking issues."""
        print(f"\n🔍 Examining Chunk Content")
        print("=" * 80)
        
        try:
            # Get all chunks
            chunks = await self.vector_db.get_document_chunks(self.document_id)
            
            if not chunks:
                print("❌ No chunks found to examine")
                return
            
            print(f"📊 Found {len(chunks)} chunks to examine")
            print(f"📄 Document ID: {self.document_id}")
            print("=" * 80)
            
            # Search for specific information in chunks
            target_phrases = [
                "15 inactive user accounts",
                "inactive user accounts",
                "90-day timeframe",
                "User Access Management",
                "security risk",
                "unauthorized access",
                "The review identified",
                "15 inactive",
                "15"
            ]
            
            found_phrases = []
            
            for i, chunk in enumerate(chunks):
                chunk_text = chunk.get('chunk_text', '')
                chunk_metadata = chunk.get('metadata', {})
                
                print(f"\n📄 CHUNK {i+1}:")
                print(f"   ID: {chunk.get('id', 'N/A')}")
                print(f"   Index: {chunk.get('chunk_index', 'N/A')}")
                print(f"   Length: {len(chunk_text)} characters")
                print(f"   Filename: {chunk_metadata.get('filename', 'Unknown')}")
                print(f"   {'=' * 70}")
                print(f"   CONTENT:")
                print(f"   {chunk_text}")
                print(f"   {'=' * 70}")
                
                # Check for target phrases in this chunk
                chunk_found_phrases = []
                for phrase in target_phrases:
                    if phrase.lower() in chunk_text.lower():
                        chunk_found_phrases.append(phrase)
                        # Find the context around the phrase
                        phrase_pos = chunk_text.lower().find(phrase.lower())
                        start_pos = max(0, phrase_pos - 100)
                        end_pos = min(len(chunk_text), phrase_pos + len(phrase) + 100)
                        context = chunk_text[start_pos:end_pos]
                        
                        found_phrases.append({
                            'chunk': i+1,
                            'phrase': phrase,
                            'context': context,
                            'position': phrase_pos
                        })
                
                if chunk_found_phrases:
                    print(f"   🎯 FOUND PHRASES: {', '.join(chunk_found_phrases)}")
                    for phrase in chunk_found_phrases:
                        phrase_pos = chunk_text.lower().find(phrase.lower())
                        start_pos = max(0, phrase_pos - 50)
                        end_pos = min(len(chunk_text), phrase_pos + len(phrase) + 50)
                        context = chunk_text[start_pos:end_pos]
                        print(f"      • '{phrase}' at position {phrase_pos}: ...{context}...")
                else:
                    print(f"   ⚠️  NO TARGET PHRASES FOUND")
                
                print()
            
            # Summary of findings
            print("=" * 80)
            print("📋 CHUNK ANALYSIS SUMMARY")
            print("=" * 80)
            
            if found_phrases:
                print("✅ Target information found in chunks:")
                for finding in found_phrases:
                    print(f"   • Chunk {finding['chunk']}: '{finding['phrase']}'")
                    print(f"     Position: {finding['position']}")
                    print(f"     Context: ...{finding['context']}...")
                    print()
            else:
                print("❌ No target information found in any chunks!")
                print("   This indicates a serious chunking problem.")
            
            # Check for chunking issues
            print("🔍 CHUNKING ANALYSIS:")
            total_content_length = sum(len(chunk.get('chunk_text', '')) for chunk in chunks)
            avg_chunk_length = total_content_length / len(chunks) if chunks else 0
            
            print(f"   Total content length: {total_content_length:,} characters")
            print(f"   Average chunk length: {avg_chunk_length:.0f} characters")
            print(f"   Number of chunks: {len(chunks)}")
            
            # Look for potential chunking problems
            short_chunks = [chunk for chunk in chunks if len(chunk.get('chunk_text', '')) < 100]
            if short_chunks:
                print(f"   ⚠️  {len(short_chunks)} chunks are very short (<100 chars) - potential chunking issue")
            
            # Check for incomplete sentences at chunk boundaries
            incomplete_sentences = 0
            for chunk in chunks:
                chunk_text = chunk.get('chunk_text', '')
                if chunk_text and not chunk_text.strip().endswith(('.', '!', '?', ':')):
                    incomplete_sentences += 1
            
            print(f"   ⚠️  {incomplete_sentences} chunks end with incomplete sentences")
            
            # Check for the specific missing information
            print("\n🔍 MISSING INFORMATION ANALYSIS:")
            print("=" * 80)
            
            # Look for the complete sentence that should contain "15 inactive user accounts"
            missing_sentence = "User Access Management: The review identified 15 inactive user accounts"
            
            # Check if any chunk contains this sentence or parts of it
            sentence_parts = [
                "User Access Management:",
                "The review identified",
                "15 inactive user accounts",
                "that have not been removed within the required 90-day timeframe"
            ]
            
            found_parts = []
            for part in sentence_parts:
                for chunk in chunks:
                    if part.lower() in chunk.get('chunk_text', '').lower():
                        found_parts.append(part)
                        break
            
            print(f"   Looking for: '{missing_sentence}'")
            print(f"   Found parts: {found_parts}")
            print(f"   Missing parts: {[part for part in sentence_parts if part not in found_parts]}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to examine chunk content: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

async def main():
    """Main test function."""
    print("🔍 CHUNK EXAMINATION TEST")
    print("=" * 80)
    
    examiner = ChunkExaminer()
    
    # Examine chunks from the previously processed document
    await examiner.examine_chunk_content()

if __name__ == "__main__":
    asyncio.run(main())
