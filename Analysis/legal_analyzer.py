# analysis/legal_analyzer.py

import spacy
import re
import streamlit as st
from collections import defaultdict

# Load spaCy model
@st.cache_resource
def load_nlp_model():
    return spacy.load("en_core_web_sm")

# Extended dictionary of legal clauses with risk patterns and levels
LEGAL_CLAUSES = {
    "Indemnification": {
        "patterns": [
            r"(indemnify|indemnification|hold harmless|defend against)",
            r"(shall compensate|reimburse .* for any losses)",
            r"(indemnifying party|indemnified party)"
        ],
        "risk_levels": {
            "unlimited": "High",
            "cap": "Medium",
            "mutual": "Low"
        }
    },
    "Limitation of Liability": {
        "patterns": [
            r"(limit(ation)? of liability|liability .* limited|shall not exceed)",
            r"(cap on damages|maximum liability|not be liable for more than)",
            r"(no event shall .* be liable)"
        ],
        "risk_levels": {
            "not_present": "High",
            "low_cap": "High",
            "reasonable_cap": "Low",
            "waived_consequential": "Medium"
        }
    },
    "Termination": {
        "patterns": [
            r"(terminat(e|ion) .* convenience|right to terminate)",
            r"(early terminat(e|ion)|cancel .* agreement|prematurely)",
            r"(terminat(e|ion) notice period|notice of terminat(e|ion))"
        ],
        "risk_levels": {
            "at_will": "High",
            "with_cause": "Medium",
            "mutual": "Low"
        }
    },
    "Intellectual Property": {
        "patterns": [
            r"(intellectual property|IP rights|patent|copyright|trademark)",
            r"(ownership of .* (IP|property|work product|deliverables))",
            r"(transfer of .* ownership|assign .* rights)"
        ],
        "risk_levels": {
            "full_transfer": "High",
            "license": "Medium",
            "limited_license": "Low"
        }
    },
    "Confidentiality": {
        "patterns": [
            r"(confidentiality|confidential information|trade secrets)",
            r"(non-disclosure|not disclose|maintain .* secrecy)",
            r"(protect .* information|confidential treatment)"
        ],
        "risk_levels": {
            "weak": "High",
            "standard": "Medium",
            "strong": "Low"
        }
    },
    "Governing Law": {
        "patterns": [
            r"(govern(ed)? by the laws|jurisdiction|venue)",
            r"(applicable law|disputes .* settled|legal proceedings)",
            r"(forum selection|choice of law|subject to .* laws)"
        ],
        "risk_levels": {
            "unfavorable": "High",
            "neutral": "Medium",
            "favorable": "Low"
        }
    },
    "Force Majeure": {
        "patterns": [
            r"(force majeure|act of god|beyond .* control)",
            r"(unforeseen circumstance|unavoidable .* delay)",
            r"(prevent performance|excuse .* performance)"
        ],
        "risk_levels": {
            "not_present": "High",
            "limited": "Medium",
            "comprehensive": "Low"
        }
    },
    "Payment Terms": {
        "patterns": [
            r"(payment terms|payment .* due|invoice .* payable)",
            r"(net \d+|payment schedule|payment obligation)",
            r"(late payment|interest .* unpaid|fee for .* delay)"
        ],
        "risk_levels": {
            "short_timeline": "High",
            "standard": "Medium",
            "extended": "Low"
        }
    }
}

@st.cache_data
def analyze_legal_document(text, confidence_threshold=0.5):
    """
    Comprehensive legal analysis of document text
    
    Args:
        text: The extracted text from the document
        confidence_threshold: Minimum confidence level for detection
        
    Returns:
        dict: Legal analysis results
    """
    nlp = load_nlp_model()
    
    # Extract contract information
    contract_info = extract_contract_info(text, nlp)
    
    # Identify risk clauses
    risk_clauses = identify_risk_clauses(text, confidence_threshold)
    
    # Extract contract value if present
    contract_value = extract_contract_value(text)
    
    # Extract parties' obligations
    obligations = extract_obligations(text, nlp)
    
    # Extract contract duration
    duration = extract_contract_duration(text)
    
    # Return comprehensive results
    return {
        "contract_info": contract_info,
        "risk_clauses": risk_clauses,
        "contract_value": contract_value,
        "obligations": obligations,
        "duration": duration
    }

def extract_contract_info(text, nlp):
    """Extract basic contract information using NER and pattern matching"""
    doc = nlp(text)
    
    # Extract parties using Named Entity Recognition
    parties = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
    
    # Filter out duplicate parties and common false positives
    filtered_parties = []
    common_false_positives = ['Inc', 'LLC', 'Ltd', 'Corporation', 'Company', 'Corp']
    
    for party in parties:
        # Skip if it's a common false positive
        if party in common_false_positives:
            continue
        
        # Skip if it's already in the filtered list
        if party in filtered_parties:
            continue
        
        # Skip if it's too short (likely an abbreviation or error)
        if len(party) < 3:
            continue
        
        filtered_parties.append(party)
    
    # Extract dates using NER
    dates = [ent.text for ent in doc.ents if ent.label_ == "DATE"]
    
    # Extract governing law clause using pattern matching
    law_pattern = r"governed by the laws of ([^,.;]*)"
    law_match = re.search(law_pattern, text, re.IGNORECASE)
    governing_law = law_match.group(1).strip() if law_match else None
    
    # Extract contract type using pattern matching
    contract_types = [
        "service agreement", "lease agreement", "employment contract",
        "non-disclosure agreement", "purchase agreement", "license agreement",
        "consulting agreement", "master service agreement"
    ]
    
    contract_type = None
    for ct in contract_types:
        if re.search(ct, text, re.IGNORECASE):
            contract_type = ct.title()
            break
    
    return {
        "parties": filtered_parties[:10],  # Limit to top 10 parties
        "dates": dates[:5],  # Limit to top 5 dates
        "governing_law": governing_law,
        "contract_type": contract_type
    }

def identify_risk_clauses(text, confidence_threshold=0.5):
    """Identify risk clauses and evaluate their risk level"""
    results = {}
    
    # Check each legal clause category
    for category, clause_info in LEGAL_CLAUSES.items():
        found_patterns = []
        clause_text = []
        
        # Check each pattern in this category
        for pattern in clause_info["patterns"]:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Extract the matching text and surrounding context
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 100)
                context = text[start:end]
                
                found_patterns.append(pattern)
                clause_text.append(context)
        
        # If patterns were found, evaluate risk level
        if found_patterns:
            risk_level = evaluate_risk_level(category, clause_text, clause_info["risk_levels"])
            
            # Generate description and recommendation
            description = f"Found {len(found_patterns)} instances of {category} language."
            recommendation = generate_recommendation(category, risk_level)
            
            results[category] = {
                "found": True,
                "patterns_matched": found_patterns,
                "risk_level": risk_level,
                "description": description,
                "recommendation": recommendation
            }
        else:
            # If no patterns found, check if this is itself a risk
            if "not_present" in clause_info["risk_levels"]:
                risk_level = clause_info["risk_levels"]["not_present"]
                
                results[category] = {
                    "found": False,
                    "patterns_matched": [],
                    "risk_level": risk_level,
                    "description": f"No {category} clause detected, which may present a risk.",
                    "recommendation": f"Consider adding a {category} clause to mitigate risk."
                }
            else:
                results[category] = {
                    "found": False,
                    "patterns_matched": [],
                    "risk_level": "N/A"
                }
    
    return results

def evaluate_risk_level(category, clause_texts, risk_levels):
    """Evaluate the risk level of a clause based on its content"""
    # Default to medium risk if found but can't determine specifics
    default_risk = "Medium"
    
    # Special handling for different clause types
    if category == "Indemnification":
        # Check if indemnification is unlimited
        if any("unlimited" in text.lower() or "all" in text.lower() for text in clause_texts):
            return risk_levels.get("unlimited", default_risk)
        # Check if indemnification has a cap
        elif any("cap" in text.lower() or "limit" in text.lower() for text in clause_texts):
            return risk_levels.get("cap", default_risk)
        # Check if indemnification is mutual
        elif any("mutual" in text.lower() or "both parties" in text.lower() for text in clause_texts):
            return risk_levels.get("mutual", default_risk)
    
    elif category == "Limitation of Liability":
        # Check if liability is capped low
        if any(re.search(r"limited to .* (less than|equal to) \$?\d{1,6}", text) for text in clause_texts):
            return risk_levels.get("low_cap", default_risk)
        # Check if liability cap is reasonable
        elif any("cap" in text.lower() or "limit" in text.lower() for text in clause_texts):
            return risk_levels.get("reasonable_cap", default_risk)
        # Check if consequential damages are waived
        elif any("consequential" in text.lower() and "waive" in text.lower() for text in clause_texts):
            return risk_levels.get("waived_consequential", default_risk)
    
    elif category == "Termination":
        # Check if termination is at will
        if any("at will" in text.lower() or "any reason" in text.lower() for text in clause_texts):
            return risk_levels.get("at_will", default_risk)
        # Check if termination requires cause
        elif any("with cause" in text.lower() or "for cause" in text.lower() for text in clause_texts):
            return risk_levels.get("with_cause", default_risk)
        # Check if termination rights are mutual
        elif any("mutual" in text.lower() or "both parties" in text.lower() for text in clause_texts):
            return risk_levels.get("mutual", default_risk)
    
    # Return default risk level if specific conditions aren't matched
    return default_risk

def generate_recommendation(category, risk_level):
    """Generate a recommendation based on clause category and risk level"""
    recommendations = {
        "Indemnification": {
            "High": "Consider negotiating for a cap on indemnification obligations or excluding certain types of damages.",
            "Medium": "Review the indemnification provisions for fair allocation of risk between parties.",
            "Low": "Mutual indemnification provides balanced protection. No immediate action needed."
        },
        "Limitation of Liability": {
            "High": "Negotiate for a reasonable liability cap that's proportional to the contract value.",
            "Medium": "Consider clarifying which types of damages are excluded and ensure adequate protection.",
            "Low": "Current limitation of liability appears reasonable. Regular review recommended."
        },
        "Termination": {
            "High": "Negotiate for more balanced termination rights or longer notice periods.",
            "Medium": "Ensure termination for cause definitions are clear and reasonable.",
            "Low": "Termination provisions appear balanced. No immediate action needed."
        },
        "Intellectual Property": {
            "High": "Consider negotiating for a license rather than full transfer of IP rights.",
            "Medium": "Clarify the scope of IP rights being transferred or licensed.",
            "Low": "IP provisions appear to provide adequate protection. Regular review recommended."
        },
        "Confidentiality": {
            "High": "Strengthen confidentiality provisions with clearer definitions and longer terms.",
            "Medium": "Review confidentiality terms to ensure adequate protection of sensitive information.",
            "Low": "Confidentiality provisions appear comprehensive. No immediate action needed."
        },
        "Governing Law": {
            "High": "Consider negotiating for a more favorable or neutral jurisdiction.",
            "Medium": "Evaluate the implications of the current governing law on potential disputes.",
            "Low": "Current jurisdiction appears favorable. No immediate action needed."
        },
        "Force Majeure": {
            "High": "Add a comprehensive force majeure clause to mitigate risks from unforeseeable events.",
            "Medium": "Expand the force majeure clause to cover additional scenarios relevant to your business.",
            "Low": "Force majeure provisions appear comprehensive. No immediate action needed."
        },
        "Payment Terms": {
            "High": "Negotiate for more favorable payment terms or longer payment periods.",
            "Medium": "Review payment terms to ensure they align with cash flow requirements.",
            "Low": "Payment terms appear favorable. No immediate action needed."
        }
    }
    
    # Return recommendation if available, otherwise a generic one
    return recommendations.get(category, {}).get(risk_level, 
        f"Review the {category} clause and consider consulting with legal counsel regarding the {risk_level.lower()} risk level.")

def extract_contract_value(text):
    """Extract contract value information"""
    # Patterns for different ways contract values might be expressed
    value_patterns = [
        r"contract value of \$?([0-9,\.]+)",
        r"total value of \$?([0-9,\.]+)",
        r"agreement .* worth \$?([0-9,\.]+)",
        r"consideration of \$?([0-9,\.]+)",
        r"fee of \$?([0-9,\.]+)",
        r"amount of \$?([0-9,\.]+)"
    ]
    
    for pattern in value_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = match.group(1).replace(',', '')
            try:
                return f"${float(value):,.2f}"
            except ValueError:
                return None
    
    return None

def extract_obligations(text, nlp):
    """Extract key obligations for each party"""
    obligations = defaultdict(list)
    
    # Process text with spaCy
    doc = nlp(text)
    
    # Extract parties if possible
    parties = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
    
    # If parties were found, look for their obligations
    if parties:
        for party in parties:
            # Look for sentences containing the party and obligation indicators
            for sent in doc.sents:
                sent_text = sent.text.lower()
                if party.lower() in sent_text and any(term in sent_text for term in 
                                                    ["shall", "must", "required to", "agrees to", "will"]):
                    obligations[party].append(sent.text)
    
    # If no specific party obligations found, extract general obligations
    if not any(obligations.values()):
        obligation_sentences = []
        for sent in doc.sents:
            sent_text = sent.text.lower()
            if any(term in sent_text for term in ["shall", "must", "required to", "agrees to", "will"]):
                obligation_sentences.append(sent.text)
        
        if obligation_sentences:
            obligations["General Obligations"] = obligation_sentences[:5]  # Limit to top 5
    
    return dict(obligations)

def extract_contract_duration(text):
    """Extract information about contract duration"""
    # Patterns for contract duration
    duration_patterns = [
        r"term of (?:this|the) agreement (?:is|shall be) ([^.;]*)",
        r"agreement (?:shall|will) (?:remain|be) in (?:effect|force) for ([^.;]*)",
        r"duration of (?:this|the) agreement (?:is|shall be) ([^.;]*)",
        r"(?:this|the) agreement (?:shall|will) continue for ([^.;]*)",
        r"(?:this|the) agreement (?:shall|will) expire on ([^.;]*)"
    ]
    
    for pattern in duration_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return None