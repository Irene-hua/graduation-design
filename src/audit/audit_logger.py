"""
Audit Logger for tracking system operations
审计日志记录器，用于跟踪系统操作
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import logging
from loguru import logger


class AuditLogger:
    """Logger for auditing system operations without storing sensitive data"""
    
    def __init__(
        self,
        log_dir: str = "logs",
        log_level: str = "INFO",
        include_query_metadata: bool = True,
        exclude_sensitive_data: bool = True,
        integrity_check: bool = True
    ):
        """
        Initialize the AuditLogger
        
        Args:
            log_dir: Directory to store log files
            log_level: Logging level
            include_query_metadata: Whether to include query metadata
            exclude_sensitive_data: Whether to exclude sensitive data
            integrity_check: Whether to include integrity checksums
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.include_query_metadata = include_query_metadata
        self.exclude_sensitive_data = exclude_sensitive_data
        self.integrity_check = integrity_check
        
        # Configure loguru
        log_file = self.log_dir / f"audit_{datetime.now().strftime('%Y%m%d')}.log"
        
        logger.remove()  # Remove default handler
        logger.add(
            log_file,
            rotation="10 MB",
            retention="30 days",
            level=log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
            enqueue=True
        )
        
        # Also add console handler for important events
        logger.add(
            lambda msg: print(msg, end=""),
            level="WARNING",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}\n"
        )
        
        self.logger = logger
        self._log_system_start()
    
    def _log_system_start(self) -> None:
        """Log system startup"""
        self.logger.info("=" * 80)
        self.logger.info("Privacy-Enhanced RAG System Started")
        self.logger.info(f"Timestamp: {datetime.now().isoformat()}")
        self.logger.info("=" * 80)
    
    def log_document_ingestion(
        self,
        file_name: str,
        num_chunks: int,
        success: bool = True,
        error: Optional[str] = None
    ) -> None:
        """
        Log document ingestion event
        
        Args:
            file_name: Name of the ingested file
            num_chunks: Number of chunks created
            success: Whether ingestion was successful
            error: Error message if failed
        """
        event = {
            'event_type': 'document_ingestion',
            'timestamp': datetime.now().isoformat(),
            'file_name': file_name,
            'num_chunks': num_chunks,
            'success': success
        }
        
        if error:
            event['error'] = error
        
        if self.integrity_check:
            event['checksum'] = self._calculate_checksum(event)
        
        if success:
            self.logger.info(f"Document ingestion: {json.dumps(event)}")
        else:
            self.logger.error(f"Document ingestion failed: {json.dumps(event)}")
    
    def log_query(
        self,
        query_id: str,
        num_results: int,
        retrieval_time: float,
        generation_time: float,
        success: bool = True,
        error: Optional[str] = None
    ) -> None:
        """
        Log query event (without storing the actual query text)
        
        Args:
            query_id: Unique query identifier
            num_results: Number of retrieved documents
            retrieval_time: Time taken for retrieval (seconds)
            generation_time: Time taken for generation (seconds)
            success: Whether query was successful
            error: Error message if failed
        """
        event = {
            'event_type': 'query',
            'timestamp': datetime.now().isoformat(),
            'query_id': query_id,
            'num_results': num_results,
            'retrieval_time_seconds': round(retrieval_time, 3),
            'generation_time_seconds': round(generation_time, 3),
            'total_time_seconds': round(retrieval_time + generation_time, 3),
            'success': success
        }
        
        if error:
            event['error'] = error
        
        if self.integrity_check:
            event['checksum'] = self._calculate_checksum(event)
        
        if success:
            self.logger.info(f"Query processed: {json.dumps(event)}")
        else:
            self.logger.error(f"Query failed: {json.dumps(event)}")
    
    def log_encryption_operation(
        self,
        operation: str,
        num_items: int,
        success: bool = True
    ) -> None:
        """
        Log encryption/decryption operation
        
        Args:
            operation: Type of operation ('encrypt' or 'decrypt')
            num_items: Number of items processed
            success: Whether operation was successful
        """
        event = {
            'event_type': 'encryption_operation',
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'num_items': num_items,
            'success': success
        }
        
        if self.integrity_check:
            event['checksum'] = self._calculate_checksum(event)
        
        self.logger.info(f"Encryption operation: {json.dumps(event)}")
    
    def log_system_event(
        self,
        event_type: str,
        details: Dict[str, Any],
        level: str = "INFO"
    ) -> None:
        """
        Log generic system event
        
        Args:
            event_type: Type of event
            details: Event details
            level: Log level (INFO, WARNING, ERROR)
        """
        event = {
            'event_type': event_type,
            'timestamp': datetime.now().isoformat(),
            **details
        }
        
        if self.integrity_check:
            event['checksum'] = self._calculate_checksum(event)
        
        log_message = f"System event: {json.dumps(event)}"
        
        if level == "WARNING":
            self.logger.warning(log_message)
        elif level == "ERROR":
            self.logger.error(log_message)
        else:
            self.logger.info(log_message)
    
    def log_security_event(
        self,
        event_description: str,
        severity: str = "INFO"
    ) -> None:
        """
        Log security-related event
        
        Args:
            event_description: Description of the security event
            severity: Severity level
        """
        event = {
            'event_type': 'security',
            'timestamp': datetime.now().isoformat(),
            'description': event_description,
            'severity': severity
        }
        
        if self.integrity_check:
            event['checksum'] = self._calculate_checksum(event)
        
        if severity in ["HIGH", "CRITICAL"]:
            self.logger.error(f"Security event: {json.dumps(event)}")
        elif severity == "MEDIUM":
            self.logger.warning(f"Security event: {json.dumps(event)}")
        else:
            self.logger.info(f"Security event: {json.dumps(event)}")
    
    def _calculate_checksum(self, event: Dict[str, Any]) -> str:
        """
        Calculate checksum for log integrity
        
        Args:
            event: Event dictionary
        
        Returns:
            str: Checksum hash
        """
        # Remove checksum field if present
        event_copy = {k: v for k, v in event.items() if k != 'checksum'}
        
        # Create deterministic string representation
        event_str = json.dumps(event_copy, sort_keys=True)
        
        # Calculate SHA-256 hash
        return hashlib.sha256(event_str.encode()).hexdigest()[:16]
    
    def verify_log_integrity(self, log_entry: str) -> bool:
        """
        Verify the integrity of a log entry
        
        Args:
            log_entry: JSON log entry string
        
        Returns:
            bool: True if integrity check passes
        """
        try:
            event = json.loads(log_entry)
            if 'checksum' not in event:
                return False
            
            stored_checksum = event['checksum']
            calculated_checksum = self._calculate_checksum(event)
            
            return stored_checksum == calculated_checksum
        except (json.JSONDecodeError, KeyError):
            return False
