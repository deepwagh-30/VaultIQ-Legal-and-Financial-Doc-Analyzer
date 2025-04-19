# analysis/compliance_checker.py

import re
import streamlit as st
from sentence_transformers import SentenceTransformer, util
import torch

# Load sentence transformer model for semantic matching
@st.cache_resource
def load_embedder():
    return SentenceTransformer('all-MiniLM-L6-v2')

# Comprehensive list of compliance requirements by category
COMPLIANCE_REQUIREMENTS = {
    "Financial Reporting": [
        {
            "description": "SOX Section 302 - Disclosure Controls",
            "patterns": [
                "disclosure controls and procedures", 
                "effectiveness of disclosure controls",
                "financial reporting procedures"
            ],
            "recommendation": "Include explicit statements about disclosure controls and procedures evaluation."
        },
        {
            "description": "SOX Section 404 - Internal Controls",
            "patterns": [
                "internal control over financial reporting", 
                "assessment of internal control",
                "financial control framework"
            ],
            "recommendation": "Add language about maintaining effective internal controls over financial reporting."
        },
        {
            "description": "GAAP Compliance Statement",
            "patterns": [
                "generally accepted accounting principles", 
                "GAAP",
                "accounting standards"
            ],
            "recommendation": "Include explicit statement of compliance with GAAP or applicable accounting standards."
        }
    ],
    "Data Privacy": [
        {
            "description": "GDPR Data Processing Provisions",
            "patterns": [
                "data processing agreement", 
                "personal data processing",
                "data controller and processor", 
                "data protection"
            ],
            "recommendation": "Include specific GDPR-compliant data processing terms and roles definition."
        },
        {
            "description": "CCPA Consumer Rights",
            "patterns": [
                "california consumer privacy", 
                "right to delete",
                "right to access", 
                "opt-out of sale"
            ],
            "recommendation": "Add provisions addressing CCPA consumer rights and business obligations."
        },
        {
            "description": "Data Breach Notification",
            "patterns": [
                "data breach notification", 
                "security incident response",
                "breach reporting timeline"
            ],
            "recommendation": "Include clear procedures and timelines for data breach notifications."
        }
    ],
    "Information Security": [
        {
            "description": "Security Safeguards Requirements",
            "patterns": [
                "information security safeguards", 
                "technical security measures",
                "administrative security controls"
            ],
            "recommendation": "Add specific security safeguards requirements and standards compliance."
        },
        {
            "description": "Security Assessment Rights",
            "patterns": [
                "security assessment", 
                "security audit rights",
                "penetration testing", 
                "vulnerability scanning"
            ],
            "recommendation": "Include rights to conduct security assessments or audit security practices."
        },
        {
            "description": "Security Certification Requirements",
            "patterns": [
                "ISO 27001", 
                "SOC 2", 
                "security certification",
                "security standards compliance"
            ],
            "recommendation": "Specify required security certifications or compliance standards."
        }
    ],
    "Employment": [
        {
            "description": "Non-Discrimination Provisions",
            "patterns": [
                "equal opportunity employer", 
                "non-discrimination policy",
                "workplace equality"
            ],
            "recommendation": "Include comprehensive non-discrimination provisions covering protected classes."
        },
        {
            "description": "Workplace Safety Requirements",
            "patterns": [
                "workplace safety", 
                "health and safety policies",
                "safe working environment"
            ],
            "recommendation": "Add specific workplace safety requirements and compliance with regulations."
        },
        {
            "description": "Worker Classification",
            "patterns": [
                "employee classification", 
                "independent contractor",
                "worker status"
            ],
            "recommendation": "Clarify worker classification and ensure compliance with labor laws."
        }
    ],
    "Anti-Corruption": [
        {
            "description": "FCPA/Anti-Bribery Provisions",
            "patterns": [
                "foreign corrupt practices", 
                "anti-bribery",
                "corruption prevention", 
                "government officials"
            ],
            "recommendation": "Include specific anti-corruption and anti-bribery provisions and compliance requirements."
        },
        {
            "description": "Gift Policy",
            "patterns": [
                "gift policy", 
                "business courtesies",
                "gifts and entertainment"
            ],
            "recommendation": "Add clear policies regarding gifts, entertainment, and business courtesies."
        },
        {
            "description": "Third-Party Due Diligence",
            "patterns": [
                "third-party due diligence", 
                "vendor vetting",
                "business partner screening"
            ],
            "recommendation": "Include requirements for conducting due diligence on third parties."
        }
    ]
}

@st.cache_data
def check_compliance(text, confidence_threshold=0.5):
    """
    Check document compliance against standard regulatory requirements
    
    Args:
        text: The extracted text from the document
        confidence_threshold: Minimum confidence level for matching
        
    Returns:
        dict: Compliance analysis results
    """
    embedder = load_embedder()
    
    # Split text into sentences for more accurate matching
    sentences = split_into_sentences(text)
    
    # Generate embeddings for all sentences at once (more efficient)
    if sentences:
        sentence_embeddings = embedder.encode(sentences, convert_to_tensor=True)
    else:
        sentence_embeddings = torch.tensor([])
    
    results = {"checks": {}, "overall_compliant": True}
    
    # Check each compliance category
    for category, requirements in COMPLIANCE_REQUIREMENTS.items():
        category_results = []
        
        for req in requirements:
            requirement_matched = False
            best_match_score = 0
            best_match_text = ""
            
            # Check pattern-based matching first (faster)
            for pattern in req["patterns"]:
                if re.search(pattern, text, re.IGNORECASE):
                    requirement_matched = True
                    break
            
            # If not matched by pattern, use semantic search
            if not requirement_matched and len(sentences) > 0:
                # Encode the requirement patterns
                pattern_embeddings = embedder.encode(req["patterns"], convert_to_tensor=True)
                
                # Find best matches between patterns and sentences
                for pattern_embedding in pattern_embeddings:
                    # Calculate similarity scores
                    similarity_scores = util.pytorch_cos_sim(pattern_embedding, sentence_embeddings)[0]
                    best_idx = similarity_scores.argmax().item()
                    score = similarity_scores[best_idx].item()
                    
                    if score > best_match_score:
                        best_match_score = score
                        if best_idx < len(sentences):
                            best_match_text = sentences[best_idx]
                
                # Consider it matched if similarity exceeds threshold
                if best_match_score >= confidence_threshold:
                    requirement_matched = True
            
            # Record the result
            check_result = {
                "description": req["description"],
                "compliant": requirement_matched,
                "confidence": best_match_score if not requirement_matched else 1.0,
                "recommendation": req["recommendation"] if not requirement_matched else "",
                "best_match": best_match_text if best_match_text else ""
            }
            
            category_results.append(check_result)
            
            # Update overall compliance status
            if not requirement_matched:
                results["overall_compliant"] = False
        
        results["checks"][category] = category_results
    
    return results

def split_into_sentences(text):
    """Split text into sentences for analysis"""
    # Simple sentence splitter (handles common abbreviations)
    text = re.sub(r'([.!?])\s+', r'\1|SPLIT|', text)
    text = re.sub(r'([.!?])"', r'\1"|SPLIT|', text)
    
    # Handle common abbreviations to avoid false splits
    common_abbr = ['Mr.', 'Mrs.', 'Ms.', 'Dr.', 'Inc.', 'Ltd.', 'Co.', 'Corp.',
                  'i.e.', 'e.g.', 'vs.', 'U.S.', 'Fig.']
    
    for abbr in common_abbr:
        text = text.replace(f"{abbr}|SPLIT|", abbr + " ")
    
    # Split the text and filter out empty sentences
    sentences = [s.strip() for s in text.split('|SPLIT|')]
    return [s for s in sentences if s]

def identify_regulatory_references(text):
    """Identify references to specific regulations in text"""
    regulations = {
        "GDPR": r"GDPR|General Data Protection Regulation",
        "CCPA": r"CCPA|California Consumer Privacy Act",
        "HIPAA": r"HIPAA|Health Insurance Portability",
        "SOX": r"SOX|Sarbanes-Oxley|Sarbanes Oxley",
        "PCI DSS": r"PCI DSS|Payment Card Industry",
        "FCPA": r"FCPA|Foreign Corrupt Practices Act"
    }
    
    references = {}
    for reg_name, pattern in regulations.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            references[reg_name] = len(matches)
    
    return references