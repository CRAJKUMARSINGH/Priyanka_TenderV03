"""
Database Manager for Tender Processing System
Handles SQLite operations for bidder credentials
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
import os

class DatabaseManager:
    def __init__(self, db_path: str = "tender_bidders.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with bidders table"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS bidders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        contact TEXT,
                        last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()
        except Exception as e:
            print(f"Error initializing database: {str(e)}")
    
    def store_bidder(self, name: str, contact: str = "") -> bool:
        """Store or update bidder credentials"""
        try:
            name = name.strip()
            contact = contact.strip()
            
            if not name:
                return False
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if bidder already exists
                cursor.execute('SELECT id FROM bidders WHERE name = ?', (name,))
                existing = cursor.fetchone()
                
                if existing:
                    # Update last_used timestamp and contact if provided
                    if contact:
                        cursor.execute('''
                            UPDATE bidders 
                            SET contact = ?, last_used = CURRENT_TIMESTAMP 
                            WHERE name = ?
                        ''', (contact, name))
                    else:
                        cursor.execute('''
                            UPDATE bidders 
                            SET last_used = CURRENT_TIMESTAMP 
                            WHERE name = ?
                        ''', (name,))
                else:
                    # Insert new bidder
                    cursor.execute('''
                        INSERT INTO bidders (name, contact) 
                        VALUES (?, ?)
                    ''', (name, contact))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error storing bidder: {str(e)}")
            return False
    
    def get_recent_bidders(self, limit: int = 50) -> List[Dict]:
        """Get recent bidders ordered by last_used"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, name, contact, last_used, created_at
                    FROM bidders 
                    ORDER BY last_used DESC 
                    LIMIT ?
                ''', (limit,))
                
                results = cursor.fetchall()
                
                bidders = []
                for row in results:
                    bidders.append({
                        'id': row[0],
                        'name': row[1],
                        'contact': row[2] or '',
                        'last_used': row[3],
                        'created_at': row[4]
                    })
                
                return bidders
                
        except Exception as e:
            print(f"Error getting recent bidders: {str(e)}")
            return []
    
    def search_bidders(self, search_term: str) -> List[Dict]:
        """Search bidders by name"""
        try:
            search_term = f"%{search_term.strip()}%"
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, name, contact, last_used, created_at
                    FROM bidders 
                    WHERE name LIKE ? 
                    ORDER BY last_used DESC
                ''', (search_term,))
                
                results = cursor.fetchall()
                
                bidders = []
                for row in results:
                    bidders.append({
                        'id': row[0],
                        'name': row[1],
                        'contact': row[2] or '',
                        'last_used': row[3],
                        'created_at': row[4]
                    })
                
                return bidders
                
        except Exception as e:
            print(f"Error searching bidders: {str(e)}")
            return []
    
    def get_bidder_by_name(self, name: str) -> Optional[Dict]:
        """Get specific bidder by name"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, name, contact, last_used, created_at
                    FROM bidders 
                    WHERE name = ?
                ''', (name.strip(),))
                
                result = cursor.fetchone()
                
                if result:
                    return {
                        'id': result[0],
                        'name': result[1],
                        'contact': result[2] or '',
                        'last_used': result[3],
                        'created_at': result[4]
                    }
                
                return None
                
        except Exception as e:
            print(f"Error getting bidder by name: {str(e)}")
            return None
    
    def delete_bidder(self, bidder_id: int) -> bool:
        """Delete bidder by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM bidders WHERE id = ?', (bidder_id,))
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"Error deleting bidder: {str(e)}")
            return False
    
    def export_bidders(self) -> str:
        """Export all bidders as JSON"""
        try:
            bidders = self.get_recent_bidders(limit=10000)  # Get all bidders
            
            export_data = {
                'export_date': datetime.now().isoformat(),
                'bidders': bidders
            }
            
            return json.dumps(export_data, indent=2)
            
        except Exception as e:
            print(f"Error exporting bidders: {str(e)}")
            return "{}"
    
    def import_bidders(self, json_data: bytes) -> int:
        """Import bidders from JSON data"""
        try:
            data = json.loads(json_data.decode('utf-8'))
            
            if 'bidders' not in data:
                return 0
            
            imported_count = 0
            
            for bidder in data['bidders']:
                if 'name' in bidder:
                    success = self.store_bidder(
                        bidder['name'], 
                        bidder.get('contact', '')
                    )
                    if success:
                        imported_count += 1
            
            return imported_count
            
        except Exception as e:
            print(f"Error importing bidders: {str(e)}")
            return 0
    
    def get_bidder_stats(self) -> Dict:
        """Get statistics about stored bidders"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total bidders
                cursor.execute('SELECT COUNT(*) FROM bidders')
                total = cursor.fetchone()[0]
                
                # Bidders with contact info
                cursor.execute('SELECT COUNT(*) FROM bidders WHERE contact IS NOT NULL AND contact != ""')
                with_contact = cursor.fetchone()[0]
                
                # Recent bidders (last 30 days)
                cursor.execute('''
                    SELECT COUNT(*) FROM bidders 
                    WHERE last_used >= datetime('now', '-30 days')
                ''')
                recent = cursor.fetchone()[0]
                
                return {
                    'total_bidders': total,
                    'with_contact': with_contact,
                    'recent_activity': recent
                }
                
        except Exception as e:
            print(f"Error getting bidder stats: {str(e)}")
            return {
                'total_bidders': 0,
                'with_contact': 0,
                'recent_activity': 0
            }
    
    def cleanup_old_bidders(self, days: int = 365) -> int:
        """Remove bidders not used for specified days"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM bidders 
                    WHERE last_used < datetime('now', '-{} days')
                '''.format(days))
                
                conn.commit()
                return cursor.rowcount
                
        except Exception as e:
            print(f"Error cleaning up old bidders: {str(e)}")
            return 0
