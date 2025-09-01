#!/usr/bin/env python3
"""
Script to ingest notes into the yak-hole vector database
"""
import asyncio
import argparse
import sys
from pathlib import Path

# Add backend to path for imports
sys.path.append(str(Path(__file__).parent))

from services.rag_service import RAGService
from config import NOTES_DIR

async def main():
    parser = argparse.ArgumentParser(description="Ingest notes into yak-hole")
    parser.add_argument(
        "--notes-dir", 
        type=str, 
        default=str(NOTES_DIR),
        help="Directory containing notes to ingest"
    )
    parser.add_argument(
        "--incremental", 
        action="store_true", 
        default=True,
        help="Only process new or modified files"
    )
    parser.add_argument(
        "--force", 
        action="store_true",
        help="Force reprocess all files"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true",
        help="Show what would be processed without actually doing it"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Initialize RAG service
    rag_service = RAGService()
    
    notes_path = Path(args.notes_dir)
    if not notes_path.exists():
        print(f"Error: Notes directory '{notes_path}' does not exist")
        sys.exit(1)
    
    print(f"🕳️  Yak Hole Note Ingestion")
    print(f"Notes directory: {notes_path}")
    print(f"Incremental: {'Yes' if args.incremental and not args.force else 'No'}")
    
    if args.dry_run:
        print("DRY RUN - No files will actually be processed")
        # TODO: Implement dry run logic
        return
    
    try:
        # Start ingestion
        await rag_service.ingest_documents(
            path=str(notes_path), 
            incremental=args.incremental and not args.force
        )
        
        # Monitor progress
        while True:
            status = await rag_service.get_ingestion_status()
            
            if args.verbose:
                print(f"Status: {status['status']} - {status['message']} ({status['progress']}%)")
            
            if status["status"] in ["completed", "error"]:
                break
                
            await asyncio.sleep(1)
        
        # Final status
        final_status = await rag_service.get_ingestion_status()
        print(f"\n✅ Ingestion completed: {final_status['message']}")
        
        # Show stats
        stats = await rag_service.get_stats()
        print(f"\n📊 Database Statistics:")
        print(f"   Total chunks: {stats.get('total_chunks', 0)}")
        print(f"   Unique files: {stats.get('unique_files', 0)}")
        print(f"   File types: {stats.get('file_types', {})}")
        
    except KeyboardInterrupt:
        print("\n🛑 Ingestion interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during ingestion: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())