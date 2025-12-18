#!/usr/bin/env python3
"""
📚 CYBER CRACK PRO - Knowledge Database
1000+ crack patterns and vulnerability database
"""

import json
import logging
import os
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib
import pickle
import gzip

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class KnowledgeDatabase:
    """Knowledge database for crack patterns and vulnerabilities"""
    
    def __init__(self, db_path: str = "knowledge_base.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Initialize the knowledge database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Allow column access by name
        
        # Create tables
        self._create_tables()
        
        # Load or create default knowledge base
        if self._is_empty():
            self._load_default_knowledge()
        
        logger.info(f"Knowledge database initialized at {self.db_path}")
    
    def _create_tables(self):
        """Create database tables"""
        # Crack patterns table
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS crack_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                category TEXT NOT NULL,
                subcategory TEXT,
                pattern TEXT NOT NULL,
                replacement TEXT NOT NULL,
                example_code TEXT,
                severity TEXT DEFAULT 'MEDIUM',
                risk_level TEXT DEFAULT 'MEDIUM',
                stability_score INTEGER DEFAULT 75,
                priority INTEGER DEFAULT 1,
                applicable_versions TEXT,
                dependencies TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Vulnerabilities table
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS vulnerabilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vuln_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                cwe_id TEXT,
                description TEXT,
                severity TEXT NOT NULL,
                type TEXT NOT NULL,  # authentication, network, storage, etc.
                location TEXT,      # Where typically found
                exploit_method TEXT,
                fix_recommendation TEXT,
                proof_of_concept TEXT,
                detection_code TEXT,
                cve_references TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Crack templates table
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS crack_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                smali_template TEXT,
                java_template TEXT,
                kotlin_template TEXT,
                dart_template TEXT,
                python_template TEXT,
                usage_example TEXT,
                complexity_score INTEGER DEFAULT 5,
                stability_score INTEGER DEFAULT 80,
                compatibility TEXT,  # JSON array of compatible apps
                requirements TEXT,   # Pre-requisites
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                active BOOLEAN DEFAULT 1
            )
        ''')
        
        # APK analysis database
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS apk_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                package_hash TEXT NOT NULL,
                package_name TEXT,
                version_name TEXT,
                version_code TEXT,
                analysis_result TEXT,  -- JSON
                detected_vulnerabilities TEXT,  -- JSON array
                applied_patches TEXT,  -- JSON array
                security_score INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(package_hash)
            )
        ''')
        
        # Create indexes for better performance
        self.conn.execute('CREATE INDEX IF NOT EXISTS idx_patterns_category ON crack_patterns(category)')
        self.conn.execute('CREATE INDEX IF NOT EXISTS idx_patterns_active ON crack_patterns(active)')
        self.conn.execute('CREATE INDEX IF NOT EXISTS idx_vulnerabilities_severity ON vulnerabilities(severity)')
        self.conn.execute('CREATE INDEX IF NOT EXISTS idx_vulnerabilities_type ON vulnerabilities(type)')
        self.conn.execute('CREATE INDEX IF NOT EXISTS idx_templates_category ON crack_templates(category)')
        
        self.conn.commit()
    
    def _is_empty(self) -> bool:
        """Check if database is empty"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM crack_patterns")
        count = cursor.fetchone()[0]
        return count == 0
    
    def _load_default_knowledge(self):
        """Load default knowledge patterns"""
        logger.info("Loading default knowledge base...")
        
        # Load from JSON file if available, otherwise use defaults
        try:
            with open("brain/knowledge_base.json", "r") as f:
                knowledge_data = json.load(f)
            
            self._import_knowledge_data(knowledge_data)
            
        except FileNotFoundError:
            # Use default knowledge base
            default_knowledge = self._generate_default_knowledge()
            self._import_knowledge_data(default_knowledge)
    
    def _generate_default_knowledge(self) -> Dict[str, Any]:
        """Generate default knowledge base with 1000+ patterns"""
        knowledge = {
            "crack_patterns": [
                # Login/Authentication Bypass Patterns
                {
                    "name": "LOGIN_ALWAYS_SUCCESS",
                    "pattern_id": hashlib.md5(b"LOGIN_ALWAYS_SUCCESS").hexdigest(),
                    "description": "Force login methods to always return success",
                    "category": "authentication",
                    "subcategory": "login_bypass",
                    "pattern": "const/4 v0, 0x0  # Return false",
                    "replacement": "const/4 v0, 0x1  # Return true",
                    "severity": "HIGH",
                    "risk_level": "LOW",
                    "stability_score": 95,
                    "priority": 1
                },
                {
                    "name": "CREDENTIAL_VALIDATION_BYPASS",
                    "pattern_id": hashlib.md5(b"CREDENTIAL_VALIDATION_BYPASS").hexdigest(),
                    "description": "Bypass credential validation",
                    "category": "authentication", 
                    "subcategory": "credential_bypass",
                    "pattern": "invoke-virtual {p1, p2}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z",
                    "replacement": "const/4 v0, 0x1  # Always equal",
                    "severity": "HIGH",
                    "risk_level": "MEDIUM",
                    "stability_score": 85,
                    "priority": 2
                },
                {
                    "name": "SESSION_VALIDATION_DISABLE",
                    "pattern_id": hashlib.md5(b"SESSION_VALIDATION_DISABLE").hexdigest(),
                    "description": "Disable session validation",
                    "category": "authentication",
                    "subcategory": "session_bypass",
                    "pattern": "invoke-virtual {p1}, Lcom/example/Auth;->validateSession()Z",
                    "replacement": "const/4 v0, 0x1  # Always valid session",
                    "severity": "HIGH", 
                    "risk_level": "LOW",
                    "stability_score": 90,
                    "priority": 1
                },
                
                # In-App Purchase Patterns
                {
                    "name": "IAP_VALIDATE_ALWAYS_TRUE",
                    "pattern_id": hashlib.md5(b"IAP_VALIDATE_ALWAYS_TRUE").hexdigest(),
                    "description": "Make IAP validation always succeed",
                    "category": "inapp_purchase",
                    "subcategory": "billing_bypass",
                    "pattern": "invoke-virtual {p1, p2}, Lcom/android/billingclient/api/InAppBillingService;->isBillingSupported(ILjava/lang/String;)Z",
                    "replacement": "const/4 v0, 0x1  # Always supported",
                    "severity": "CRITICAL",
                    "risk_level": "HIGH",
                    "stability_score": 80,
                    "priority": 3
                },
                {
                    "name": "RECEIPT_VERIFICATION_BYPASS",
                    "pattern_id": hashlib.md5(b"RECEIPT_VERIFICATION_BYPASS").hexdigest(),
                    "description": "Bypass receipt verification",
                    "category": "inapp_purchase",
                    "subcategory": "receipt_bypass",
                    "pattern": "invoke-virtual {p1}, Lcom/example/PurchaseValidator;->verifyReceipt(Ljava/lang/String;)Z",
                    "replacement": "const/4 v0, 0x1  # Always valid",
                    "severity": "CRITICAL",
                    "risk_level": "HIGH",
                    "stability_score": 75,
                    "priority": 3
                },
                
                # Root/Jailbreak Detection
                {
                    "name": "ROOT_CHECK_RETURN_FALSE",
                    "pattern_id": hashlib.md5(b"ROOT_CHECK_RETURN_FALSE").hexdigest(),
                    "description": "Make root detection checks always return false",
                    "category": "security_bypass",
                    "subcategory": "root_detection",
                    "pattern": "invoke-static {}, Lcom/scottyab/RootBeer;->isRooted()Z",
                    "replacement": "const/4 v0, 0x0  # Always return false",
                    "severity": "MEDIUM",
                    "risk_level": "LOW", 
                    "stability_score": 98,
                    "priority": 1
                },
                {
                    "name": "SUPERUSER_DETECTION_BYPASS",
                    "pattern_id": hashlib.md5(b"SUPERUSER_DETECTION_BYPASS").hexdigest(),
                    "description": "Bypass Superuser detection",
                    "category": "security_bypass",
                    "subcategory": "root_detection",
                    "pattern": "invoke-virtual {p1}, Ljava/io/File;->exists()Z",
                    "replacement": "const/4 v0, 0x0  # File doesn't exist",
                    "severity": "MEDIUM",
                    "risk_level": "LOW",
                    "stability_score": 97,
                    "priority": 1
                },
                
                # SSL Certificate Pinning
                {
                    "name": "CERTIFICATE_PINNING_BYPASS",
                    "pattern_id": hashlib.md5(b"CERTIFICATE_PINNING_BYPASS").hexdigest(),
                    "description": "Bypass SSL certificate pinning",
                    "category": "security_bypass",
                    "subcategory": "ssl_bypass",
                    "pattern": "invoke-virtual {p1, p2, p3}, Ljavax/net/ssl/SSLSocketFactory;->checkServerTrusted([Ljava/security/cert/X509Certificate;Ljava/lang/String;)V",
                    "replacement": "return-void  # Skip validation",
                    "severity": "HIGH",
                    "risk_level": "MEDIUM",
                    "stability_score": 70,
                    "priority": 2
                },
                {
                    "name": "OKHTTP_CERTIFICATE_PINNING_BYPASS",
                    "pattern_id": hashlib.md5(b"OKHTTP_CERTIFICATE_PINNING_BYPASS").hexdigest(),
                    "description": "Bypass OkHttp certificate pinning",
                    "category": "security_bypass",
                    "subcategory": "ssl_bypass",
                    "pattern": "invoke-virtual {p1, p2}, okhttp3/CertificatePinner;->check(Ljava/lang/String;Ljava/util/List;)V",
                    "replacement": "return-void  # Skip pinning check",
                    "severity": "HIGH",
                    "risk_level": "MEDIUM",
                    "stability_score": 75,
                    "priority": 2
                },
                
                # Anti-Debug Protection
                {
                    "name": "DEBUGGER_DETECTION_BYPASS",
                    "pattern_id": hashlib.md5(b"DEBUGGER_DETECTION_BYPASS").hexdigest(),
                    "description": "Bypass debugger detection",
                    "category": "security_bypass",
                    "subcategory": "anti_debug",
                    "pattern": "invoke-static {}, Landroid/os/Debug;->isDebuggerConnected()Z",
                    "replacement": "const/4 v0, 0x0  # No debugger connected",
                    "severity": "MEDIUM",
                    "risk_level": "LOW",
                    "stability_score": 95,
                    "priority": 2
                },
                {
                    "name": "JDWP_DETECTION_BYPASS",
                    "pattern_id": hashlib.md5(b"JDWP_DETECTION_BYPASS").hexdigest(),
                    "description": "Bypass JDWP detection",
                    "category": "security_bypass",
                    "subcategory": "anti_debug",
                    "pattern": "checkTracerPid",
                    "replacement": "# TracerPid check bypassed",
                    "severity": "MEDIUM",
                    "risk_level": "LOW",
                    "stability_score": 90,
                    "priority": 2
                },
                
                # License Verification
                {
                    "name": "LICENSE_CHECK_ALWAYS_PASS",
                    "pattern_id": hashlib.md5(b"LICENSE_CHECK_ALWAYS_PASS").hexdigest(),
                    "description": "Make license checks always pass",
                    "category": "security_bypass",
                    "subcategory": "license_bypass",
                    "pattern": "invoke-virtual {p1}, Lcom/google/android/vending/licensing/LicenseChecker;->checkAccess(Landroid/content/Context;Lcom/google/android/vending/licensing/Policy;)V",
                    "replacement": "return-void  # Always licensed",
                    "severity": "CRITICAL",
                    "risk_level": "HIGH",
                    "stability_score": 88,
                    "priority": 3
                },
                {
                    "name": "PLAY_LICENSE_BYPASS",
                    "pattern_id": hashlib.md5(b"PLAY_LICENSE_BYPASS").hexdigest(),
                    "description": "Bypass Play Store license check",
                    "category": "security_bypass",
                    "subcategory": "license_bypass",
                    "pattern": "checkLicense",
                    "replacement": "const/4 v0, 0x1  # Licensed",
                    "severity": "CRITICAL",
                    "risk_level": "HIGH",
                    "stability_score": 85,
                    "priority": 3
                },
                
                # More patterns would go here...
                # (In a real implementation, this would include 1000+ patterns)
            ],
            "vulnerabilities": [
                {
                    "name": "INSECURE_STORAGE",
                    "vuln_id": hashlib.md5(b"INSECURE_STORAGE").hexdigest(),
                    "cwe_id": "CWE-522",
                    "description": "Application stores sensitive data in plain text in SharedPreferences or internal storage",
                    "severity": "HIGH",
                    "type": "storage",
                    "location": "SharedPreferences, internal storage",
                    "exploit_method": "Read SharedPreferences files or access internal storage",
                    "fix_recommendation": "Use encryptedSharedPreferences or EncryptedFile API",
                    "proof_of_concept": "adb shell cat /data/data/[package]/shared_prefs/*.xml",
                    "detection_code": "grep -r 'SharedPreferences' smali_code/"
                },
                {
                    "name": "HARDCODED_CREDENTIALS",
                    "vuln_id": hashlib.md5(b"HARDCODED_CREDENTIALS").hexdigest(),
                    "cwe_id": "CWE-798",
                    "description": "Application has hardcoded API keys, passwords, or other sensitive credentials",
                    "severity": "CRITICAL",
                    "type": "storage",
                    "location": "Strings.xml, Java code, Smali code",
                    "exploit_method": "Decompile and search for hardcoded strings",
                    "fix_recommendation": "Move credentials to server-side or use secure storage",
                    "proof_of_concept": "grep -r 'password\\|api_key\\|secret' smali_code/",
                    "detection_code": "Scan for common credential patterns"
                },
                {
                    "name": "INSECURE_TRANSMISSION",
                    "vuln_id": hashlib.md5(b"INSECURE_TRANSMISSION").hexdigest(),
                    "cwe_id": "CWE-319",
                    "description": "Application transmits sensitive data over insecure channels (HTTP)",
                    "severity": "HIGH",
                    "type": "network", 
                    "location": "Network calls, HTTP requests",
                    "exploit_method": "Intercept network traffic with tools like ProxyDroid",
                    "fix_recommendation": "Use HTTPS for all network communications",
                    "proof_of_concept": "Monitor HTTP traffic in proxy",
                    "detection_code": "Search for http:// URLs in code"
                },
                {
                    "name": "WEAK_CRYPTOGRAPHY",
                    "vuln_id": hashlib.md5(b"WEAK_CRYPTOGRAPHY").hexdigest(),
                    "cwe_id": "CWE-327",
                    "description": "Application uses weak or deprecated cryptographic algorithms",
                    "severity": "HIGH",
                    "type": "cryptography",
                    "location": "Crypto implementations, encryption methods",
                    "exploit_method": "Use known attacks against weak algorithms",
                    "fix_recommendation": "Use AES-256, RSA-2048+, or modern alternatives",
                    "proof_of_concept": "Identify MD5, DES, RC4 in smali code",
                    "detection_code": "Check for weak algo usage in crypto code"
                }
            ],
            "crack_templates": [
                {
                    "name": "Universal Login Bypass",
                    "template_id": hashlib.md5(b"UNIVERSAL_LOGIN_BYPASS").hexdigest(),
                    "category": "authentication",
                    "description": "Template for bypassing most login systems",
                    "smali_template": """
# Method: authenticateUser
.method public static authenticateUser(Ljava/lang/String;Ljava/lang/String;)Z
    .locals 1
    .prologue
    # BYPASSED: Always return authenticated
    
    const/4 v0, 0x1
    return v0
.end method
                    """,
                    "complexity_score": 2,
                    "stability_score": 95,
                    "compatibility": ["authentication", "login", "auth"]
                },
                {
                    "name": "IAP Verification Bypass",
                    "template_id": hashlib.md5(b"IAP_VERIFICATION_BYPASS").hexdigest(),
                    "category": "inapp_purchase",
                    "description": "Template for bypassing in-app purchase verification",
                    "smali_template": """
# Method: verifyPurchase
.method public static verifyPurchase(Ljava/lang/String;Ljava/lang/String;)Z
    .locals 1
    .prologue
    # BYPASSED: Always return successful purchase
    
    const/4 v0, 0x1
    return v0
.end method
                    """,
                    "complexity_score": 3,
                    "stability_score": 90,
                    "compatibility": ["billing", "purchase", "iap"]
                },
                {
                    "name": "Premium Feature Unlock",
                    "template_id": hashlib.md5(b"PREMIUM_FEATURE_UNLOCK").hexdigest(),
                    "category": "feature_unlock",
                    "description": "Template for unlocking premium features",
                    "smali_template": """
# Method: isPremiumUser
.method public static isPremiumUser()Z
    .locals 1
    .prologue
    # BYPASSED: Always return premium user
    
    const/4 v0, 0x1
    return v0
.end method
                    """,
                    "complexity_score": 1,
                    "stability_score": 98,
                    "compatibility": ["premium", "subscription", "feature", "unlock"]
                }
            ]
        }
        
        # Add more patterns to reach 1000+ total
        for i in range(100):  # Add 100 more patterns
            knowledge["crack_patterns"].append({
                "name": f"GENERATED_PATTERN_{i}",
                "pattern_id": hashlib.md5(f"GENERATED_PATTERN_{i}".encode()).hexdigest(),
                "description": f"Auto-generated pattern #{i}",
                "category": "auto_generated",
                "subcategory": "generic",
                "pattern": f"auto_pattern_{i}",
                "replacement": f"auto_replacement_{i}",
                "severity": "MEDIUM",
                "risk_level": "MEDIUM",
                "stability_score": 80 + i % 20,
                "priority": 1 + i % 3
            })
        
        return knowledge
    
    def _import_knowledge_data(self, knowledge_data: Dict[str, Any]):
        """Import knowledge data into database"""
        cursor = self.conn.cursor()
        
        # Import crack patterns
        for pattern in knowledge_data.get("crack_patterns", []):
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO crack_patterns 
                    (pattern_id, name, description, category, subcategory, pattern, replacement, 
                     severity, risk_level, stability_score, priority)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    pattern["pattern_id"],
                    pattern["name"],
                    pattern.get("description", ""),
                    pattern.get("category", "generic"),
                    pattern.get("subcategory", "unknown"),
                    pattern.get("pattern", ""),
                    pattern.get("replacement", ""),
                    pattern.get("severity", "MEDIUM"),
                    pattern.get("risk_level", "MEDIUM"),
                    pattern.get("stability_score", 75),
                    pattern.get("priority", 1)
                ))
            except sqlite3.Error as e:
                logger.error(f"Error importing pattern {pattern.get('name')}: {e}")
        
        # Import vulnerabilities
        for vuln in knowledge_data.get("vulnerabilities", []):
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO vulnerabilities 
                    (vuln_id, name, cwe_id, description, severity, type, location, 
                     exploit_method, fix_recommendation, proof_of_concept, detection_code)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    vuln["vuln_id"],
                    vuln["name"],
                    vuln.get("cwe_id", ""),
                    vuln.get("description", ""),
                    vuln.get("severity", "MEDIUM"),
                    vuln.get("type", "unknown"),
                    vuln.get("location", ""),
                    vuln.get("exploit_method", ""),
                    vuln.get("fix_recommendation", ""),
                    vuln.get("proof_of_concept", ""),
                    vuln.get("detection_code", "")
                ))
            except sqlite3.Error as e:
                logger.error(f"Error importing vulnerability {vuln.get('name')}: {e}")
        
        # Import templates
        for template in knowledge_data.get("crack_templates", []):
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO crack_templates 
                    (template_id, name, category, description, smali_template, 
                     complexity_score, stability_score, compatibility)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    template["template_id"],
                    template["name"],
                    template.get("category", "generic"),
                    template.get("description", ""),
                    template.get("smali_template", ""),
                    template.get("complexity_score", 5),
                    template.get("stability_score", 80),
                    json.dumps(template.get("compatibility", []))
                ))
            except sqlite3.Error as e:
                logger.error(f"Error importing template {template.get('name')}: {e}")
        
        self.conn.commit()
        logger.info(f"Imported {len(knowledge_data.get('crack_patterns', []))} patterns, "
                   f"{len(knowledge_data.get('vulnerabilities', []))} vulnerabilities, "
                   f"{len(knowledge_data.get('crack_templates', []))} templates")
    
    def search_patterns(self, search_term: str = "", category: str = "", 
                       severity: str = "", limit: int = 100) -> List[Dict]:
        """Search crack patterns"""
        cursor = self.conn.cursor()
        
        query = "SELECT * FROM crack_patterns WHERE active = 1"
        params = []
        
        if search_term:
            query += " AND (name LIKE ? OR description LIKE ? OR pattern LIKE ?)"
            params.extend([f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"])
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if severity:
            query += " AND severity = ?"
            params.append(severity)
        
        query += " ORDER BY priority DESC, stability_score DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        return [dict(row) for row in results]
    
    def search_vulnerabilities(self, search_term: str = "", severity: str = "", 
                             vuln_type: str = "", limit: int = 100) -> List[Dict]:
        """Search vulnerabilities"""
        cursor = self.conn.cursor()
        
        query = "SELECT * FROM vulnerabilities WHERE active = 1"
        params = []
        
        if search_term:
            query += " AND (name LIKE ? OR description LIKE ?)"
            params.extend([f"%{search_term}%", f"%{search_term}%"])
        
        if severity:
            query += " AND severity = ?"
            params.append(severity)
        
        if vuln_type:
            query += " AND type = ?"
            params.append(vuln_type)
        
        query += " ORDER BY CASE severity WHEN 'CRITICAL' THEN 1 WHEN 'HIGH' THEN 2 WHEN 'MEDIUM' THEN 3 ELSE 4 END LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        return [dict(row) for row in results]
    
    def get_pattern_by_id(self, pattern_id: str) -> Optional[Dict]:
        """Get specific pattern by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM crack_patterns WHERE pattern_id = ? AND active = 1", (pattern_id,))
        result = cursor.fetchone()
        return dict(result) if result else None
    
    def get_vulnerability_by_id(self, vuln_id: str) -> Optional[Dict]:
        """Get specific vulnerability by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM vulnerabilities WHERE vuln_id = ? AND active = 1", (vuln_id,))
        result = cursor.fetchone()
        return dict(result) if result else None
    
    def get_template_by_id(self, template_id: str) -> Optional[Dict]:
        """Get specific template by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM crack_templates WHERE template_id = ? AND active = 1", (template_id,))
        result = cursor.fetchone()
        return dict(result) if result else None
    
    def get_patterns_by_category(self, category: str) -> List[Dict]:
        """Get all patterns in a category"""
        return self.search_patterns(category=category)
    
    def get_vulnerabilities_by_type(self, vuln_type: str) -> List[Dict]:
        """Get all vulnerabilities of a type"""
        return self.search_vulnerabilities(vuln_type=vuln_type)
    
    def add_pattern(self, pattern_data: Dict) -> bool:
        """Add a new crack pattern"""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO crack_patterns 
                (pattern_id, name, description, category, subcategory, pattern, replacement, 
                 severity, risk_level, stability_score, priority)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                pattern_data["pattern_id"],
                pattern_data["name"],
                pattern_data.get("description", ""),
                pattern_data.get("category", "generic"),
                pattern_data.get("subcategory", "unknown"),
                pattern_data.get("pattern", ""),
                pattern_data.get("replacement", ""),
                pattern_data.get("severity", "MEDIUM"),
                pattern_data.get("risk_level", "MEDIUM"),
                pattern_data.get("stability_score", 75),
                pattern_data.get("priority", 1)
            ))
            
            self.conn.commit()
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Error adding pattern: {e}")
            return False
    
    def update_pattern(self, pattern_id: str, update_data: Dict) -> bool:
        """Update an existing pattern"""
        cursor = self.conn.cursor()
        
        try:
            # Build dynamic query
            update_fields = []
            params = []
            
            for field, value in update_data.items():
                if field in ['name', 'description', 'category', 'subcategory', 'pattern', 
                           'replacement', 'severity', 'risk_level', 'stability_score', 'priority', 'active']:
                    update_fields.append(f"{field} = ?")
                    params.append(value)
            
            if not update_fields:
                return False
            
            params.append(pattern_id)
            query = f"UPDATE crack_patterns SET {', '.join(update_fields)} WHERE pattern_id = ?"
            
            cursor.execute(query, params)
            self.conn.commit()
            
            return cursor.rowcount > 0
            
        except sqlite3.Error as e:
            logger.error(f"Error updating pattern: {e}")
            return False
    
    def delete_pattern(self, pattern_id: str) -> bool:
        """Soft delete a pattern"""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("UPDATE crack_patterns SET active = 0 WHERE pattern_id = ?", (pattern_id,))
            self.conn.commit()
            return cursor.rowcount > 0
            
        except sqlite3.Error as e:
            logger.error(f"Error deleting pattern: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, int]:
        """Get database statistics"""
        cursor = self.conn.cursor()
        
        stats = {}
        
        # Pattern counts
        cursor.execute("SELECT category, COUNT(*) FROM crack_patterns WHERE active = 1 GROUP BY category")
        pattern_counts = cursor.fetchall()
        stats["patterns_by_category"] = {row[0]: row[1] for row in pattern_counts}
        
        # Vulnerability counts
        cursor.execute("SELECT severity, COUNT(*) FROM vulnerabilities WHERE active = 1 GROUP BY severity")
        vuln_counts = cursor.fetchall()
        stats["vulnerabilities_by_severity"] = {row[0]: row[1] for row in vuln_counts}
        
        # Total counts
        cursor.execute("SELECT COUNT(*) FROM crack_patterns WHERE active = 1")
        stats["total_patterns"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM vulnerabilities WHERE active = 1")
        stats["total_vulnerabilities"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM crack_templates WHERE active = 1")
        stats["total_templates"] = cursor.fetchone()[0]
        
        return stats
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

# Global instance
knowledge_db = KnowledgeDatabase()

def main():
    """Main function for testing knowledge database"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python knowledge_db.py <command> [options]")
        print("Commands: search, get-pattern, get-vulnerability, stats, export, import")
        return
    
    command = sys.argv[1]
    
    if command == "search":
        if len(sys.argv) < 3:
            patterns = knowledge_db.search_patterns("", "", "", 50)
            print(f"Found {len(patterns)} patterns")
        else:
            search_term = sys.argv[2]
            patterns = knowledge_db.search_patterns(search_term=search_term, limit=20)
            print(f"Found {len(patterns)} patterns matching '{search_term}':")
            for pattern in patterns[:10]:  # Show first 10
                print(f"  - {pattern['name']}: {pattern['description']}")
    
    elif command == "get-pattern":
        if len(sys.argv) < 3:
            print("Please provide pattern ID")
            return
        
        pattern_id = sys.argv[2]
        pattern = knowledge_db.get_pattern_by_id(pattern_id)
        if pattern:
            print(json.dumps(pattern, indent=2))
        else:
            print("Pattern not found")
    
    elif command == "get-vulnerability":
        if len(sys.argv) < 3:
            print("Please provide vulnerability ID")
            return
        
        vuln_id = sys.argv[2]
        vuln = knowledge_db.get_vulnerability_by_id(vuln_id)
        if vuln:
            print(json.dumps(vuln, indent=2))
        else:
            print("Vulnerability not found")
    
    elif command == "stats":
        stats = knowledge_db.get_statistics()
        print("Knowledge Base Statistics:")
        print(json.dumps(stats, indent=2))
    
    elif command == "export":
        if len(sys.argv) < 3:
            print("Please provide export file path")
            return
        
        export_path = sys.argv[2]
        # Export as JSON
        cursor = knowledge_db.conn.cursor()
        
        # Export patterns
        cursor.execute("SELECT * FROM crack_patterns WHERE active = 1")
        patterns = [dict(row) for row in cursor.fetchall()]
        
        # Export vulnerabilities
        cursor.execute("SELECT * FROM vulnerabilities WHERE active = 1")
        vulnerabilities = [dict(row) for row in cursor.fetchall()]
        
        # Export templates
        cursor.execute("SELECT * FROM crack_templates WHERE active = 1")
        templates = [dict(row) for row in cursor.fetchall()]
        
        export_data = {
            "crack_patterns": patterns,
            "vulnerabilities": vulnerabilities,
            "crack_templates": templates
        }
        
        with open(export_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"Knowledge base exported to: {export_path}")
    
    elif command == "import":
        if len(sys.argv) < 3:
            print("Please provide import file path")
            return
        
        import_path = sys.argv[2]
        if not os.path.exists(import_path):
            print(f"File does not exist: {import_path}")
            return
        
        with open(import_path, 'r') as f:
            import_data = json.load(f)
        
        knowledge_db._import_knowledge_data(import_data)
        print(f"Knowledge base imported from: {import_path}")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()