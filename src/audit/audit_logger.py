"""Audit logging system without sensitive data."""
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger


class AuditLogger:
    """Audit logger for tracking system operations without sensitive data."""
    
    def __init__(
        self,
        log_file: str = "logs/audit.log",
        enable: bool = True,
        log_sensitive_data: bool = False,
        integrity_check: bool = True
    ):
        """
        Initialize audit logger.
        
        Args:
            log_file: Path to audit log file
            enable: Enable logging
            log_sensitive_data: Whether to log sensitive data (should be False)
            integrity_check: Enable integrity checking
        """
        self.log_file = Path(log_file)
        self.enable = enable
        self.log_sensitive_data = log_sensitive_data
        self.integrity_check = integrity_check
        
        # Create log directory
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Configure loguru
        if self.enable:
            logger.add(
                self.log_file,
                rotation="10 MB",
                retention="30 days",
                format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {message}",
                enqueue=True
            )
        
        self.log_event("system", "audit_logger_initialized", {
            "log_file": str(self.log_file),
            "log_sensitive_data": self.log_sensitive_data,
            "integrity_check": self.integrity_check
        })
    
    def log_event(
        self,
        category: str,
        event_type: str,
        metadata: Dict[str, Any],
        user_id: Optional[str] = None
    ):
        """
        Log an audit event.
        
        Args:
            category: Event category (e.g., 'query', 'document', 'system')
            event_type: Specific event type
            metadata: Event metadata (non-sensitive)
            user_id: Optional user identifier
        """
        if not self.enable:
            return
        
        # Filter sensitive data from metadata
        filtered_metadata = self._filter_sensitive_data(metadata)
        
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "category": category,
            "event_type": event_type,
            "user_id": user_id,
            "metadata": filtered_metadata
        }
        
        # Add integrity hash if enabled
        if self.integrity_check:
            event["integrity_hash"] = self._compute_hash(event)
        
        # Log as JSON
        logger.info(json.dumps(event, ensure_ascii=False))
    
    def log_query(self, query_hash: str, num_results: int, response_time: float):
        """
        Log a query event.
        
        Args:
            query_hash: Hash of the query (not the actual query text)
            num_results: Number of results retrieved
            response_time: Response time in seconds
        """
        self.log_event("query", "search_executed", {
            "query_hash": query_hash,
            "num_results": num_results,
            "response_time_seconds": response_time
        })
    
    def log_document_operation(
        self,
        operation: str,
        document_id: str,
        success: bool
    ):
        """
        Log a document operation.
        
        Args:
            operation: Operation type ('upload', 'delete', 'encrypt', 'decrypt')
            document_id: Document identifier (hash, not filename)
            success: Whether operation succeeded
        """
        self.log_event("document", operation, {
            "document_id": document_id,
            "success": success
        })
    
    def log_retrieval(
        self,
        query_hash: str,
        num_chunks_retrieved: int,
        top_k: int
    ):
        """
        Log a retrieval operation.
        
        Args:
            query_hash: Hash of the query
            num_chunks_retrieved: Number of chunks retrieved
            top_k: K parameter used
        """
        self.log_event("retrieval", "chunks_retrieved", {
            "query_hash": query_hash,
            "num_chunks_retrieved": num_chunks_retrieved,
            "top_k": top_k
        })
    
    def log_generation(
        self,
        query_hash: str,
        model_name: str,
        generation_time: float,
        success: bool
    ):
        """
        Log a text generation operation.
        
        Args:
            query_hash: Hash of the query
            model_name: Name of the LLM model
            generation_time: Time taken to generate response
            success: Whether generation succeeded
        """
        self.log_event("generation", "text_generated", {
            "query_hash": query_hash,
            "model_name": model_name,
            "generation_time_seconds": generation_time,
            "success": success
        })
    
    def log_encryption(self, operation: str, num_chunks: int):
        """
        Log an encryption operation.
        
        Args:
            operation: 'encrypt' or 'decrypt'
            num_chunks: Number of chunks processed
        """
        self.log_event("encryption", operation, {
            "num_chunks": num_chunks
        })
    
    def _filter_sensitive_data(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter sensitive data from metadata.
        
        Args:
            metadata: Original metadata
            
        Returns:
            Filtered metadata without sensitive fields
        """
        if self.log_sensitive_data:
            return metadata
        
        # List of sensitive keys to remove
        sensitive_keys = [
            'query', 'text', 'content', 'plaintext', 'password',
            'key', 'token', 'secret', 'encrypted_text', 'decrypted_text'
        ]
        
        filtered = {}
        for key, value in metadata.items():
            if key.lower() not in sensitive_keys:
                filtered[key] = value
        
        return filtered
    
    def _compute_hash(self, event: Dict[str, Any]) -> str:
        """
        Compute integrity hash for an event.
        
        Args:
            event: Event dictionary
            
        Returns:
            SHA-256 hash
        """
        # Create a copy without the hash field
        event_copy = {k: v for k, v in event.items() if k != 'integrity_hash'}
        event_str = json.dumps(event_copy, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(event_str.encode()).hexdigest()
    
    def verify_log_integrity(self, log_line: str) -> bool:
        """
        Verify the integrity of a log line.
        
        Args:
            log_line: JSON log line
            
        Returns:
            True if integrity check passes
        """
        if not self.integrity_check:
            return True
        
        try:
            # Extract JSON from log line
            json_start = log_line.find('{')
            if json_start == -1:
                return False
            
            event = json.loads(log_line[json_start:])
            
            if 'integrity_hash' not in event:
                return False
            
            stored_hash = event['integrity_hash']
            computed_hash = self._compute_hash(event)
            
            return stored_hash == computed_hash
        
        except Exception:
            return False
