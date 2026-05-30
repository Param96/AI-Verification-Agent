import fitz  # PyMuPDF
import re
import csv
from pathlib import Path
from typing import List, Dict, Any, Optional
from utils.logger import logger
from utils.schema import CourseRecord

def decode_cipher(text: str) -> str:
    """
    Decodes the custom ASCII offset cipher found in the scrambled PDF.
    Handles both standard offsets and specific marker patterns.
    """
    if '\x03' in text or 'FRXUVH' in text or '%' in text:
        decoded = ""
        for char in text:
            val = ord(char) + 29
            if 32 <= val <= 126:
                decoded += chr(val)
            else:
                decoded += char
        return decoded.strip()
    return text.strip()

def extract_details_from_text(detail_text: str) -> Dict[str, str]:
    """
    Extract structured details (Cost, Mode, Country, Duration, Language, Skills) from text.
    Uses regex patterns to parse the detail fields.
    """
    detail_text = re.sub(r'\s+', ' ', detail_text)
    # Fix common OCR glitches
    detail_text = detail_text.replace("Ofi-,ine", "Offline").replace("Ofline", "Offline")
    
    details = {
        "cost": "",
        "mode": "",
        "country": "",
        "duration": "",
        "language": "",
        "skills": ""
    }
    
    # Extract each field using regex patterns
    cost_match = re.search(r'Cost:\s*(.*?)(?=Mode:|Country:|Duration:|Language:|Skills:|$)', detail_text, re.IGNORECASE)
    mode_match = re.search(r'Mode:\s*(.*?)(?=Country:|Duration:|Language:|Skills:|$)', detail_text, re.IGNORECASE)
    country_match = re.search(r'Country:\s*(.*?)(?=Duration:|Language:|Skills:|$)', detail_text, re.IGNORECASE)
    duration_match = re.search(r'Duration:\s*(.*?)(?=Language:|Skills:|$)', detail_text, re.IGNORECASE)
    lang_match = re.search(r'Language:\s*(.*?)(?=Skills:|$)', detail_text, re.IGNORECASE)
    skills_match = re.search(r'Skills:\s*(.*?)(?=$)', detail_text, re.IGNORECASE)
    
    details["cost"] = cost_match.group(1).strip() if cost_match else ""
    details["mode"] = mode_match.group(1).strip() if mode_match else ""
    details["country"] = country_match.group(1).strip() if country_match else ""
    details["duration"] = duration_match.group(1).strip() if duration_match else ""
    details["language"] = lang_match.group(1).strip() if lang_match else ""
    details["skills"] = skills_match.group(1).strip() if skills_match else ""
    
    return details

def parse_pdf_vision(file_path: Path) -> List[CourseRecord]:
    """
    Advanced Computer Vision & Spatial PDF Parser with two-column card extraction.
    Handles scrambled text, multi-column layouts, and structured course card parsing.
    """
    logger.info(f"Vision Parsing PDF: {file_path}")
    records = []
    
    try:
        doc = fitz.open(file_path)
        row_id = 1
        
        for page_num, page in enumerate(doc):
            logger.debug(f"Processing page {page_num + 1}")
            raw_links = page.get_links()
            
            # Split page in half to process left and right columns separately
            w = page.rect.width
            h = page.rect.height
            left_rect = fitz.Rect(0, 0, w / 2, h)
            right_rect = fitz.Rect(w / 2, 0, w, h)
            
            for side, rect in [("Left", left_rect), ("Right", right_rect)]:
                
                # Extract links for this side
                side_links = []
                for link in raw_links:
                    if 'uri' in link:
                        center_x = (link['from'].x0 + link['from'].x1) / 2
                        if (side == "Left" and center_x < w / 2) or (side == "Right" and center_x >= w / 2):
                            side_links.append({'url': link['uri'], 'y0': link['from'].y0})
                side_links.sort(key=lambda x: x['y0'])
                
                # Get text blocks (paragraphs) instead of raw lines
                blocks = page.get_text("blocks", clip=rect)
                blocks = [b for b in blocks if b[6] == 0]  # Text only, no images
                blocks.sort(key=lambda b: b[1])  # Sort vertically
                
                current_card_blocks = []
                url_index = 0
                
                for block in blocks:
                    raw_text = block[4]
                    text = decode_cipher(raw_text).strip()
                    
                    text_clean = re.sub(r'\s+', '', text.lower())
                    
                    # Trigger: We reached the end of a card (detected by "link to course" markers)
                    if "linktocourse" in text_clean or "frxuvh" in text_clean or text_clean.startswith("http"):
                        
                        if not current_card_blocks:
                            continue
                        
                        header_blocks = []
                        detail_text = ""
                        cost_found = False
                        
                        # Sort gathered blocks into Headers (Names) and Details (Data)
                        for cb in current_card_blocks:
                            cb_clean = re.sub(r'\s+', ' ', cb).strip()
                            
                            # Filter out PDF header noise
                            noise_keywords = ["nirf", "qs world", "free to audit", "scholarship", 
                                            "bachelors degree", "masters degree", "certificate", 
                                            "free course", "post graduate"]
                            if any(n in cb_clean.lower() for n in noise_keywords):
                                continue
                                
                            if "Cost:" in cb_clean or "Mode:" in cb_clean:
                                cost_found = True
                                
                            if not cost_found:
                                header_blocks.append(cb_clean)
                            else:
                                detail_text += " " + cb_clean
                                
                        # Parse course and institute names (handles wrapped lines)
                        if len(header_blocks) >= 2:
                            institute = header_blocks[-1]
                            course_name = " ".join(header_blocks[:-1])
                        elif len(header_blocks) == 1:
                            course_name = header_blocks[0]
                            institute = "Unknown Institute"
                        else:
                            course_name = "Unknown Course"
                            institute = "Unknown Institute"
                            
                        # Clean non-ASCII characters
                        course_name = re.sub(r'[^\x00-\x7F]+', '', course_name).strip()
                        institute = re.sub(r'[^\x00-\x7F]+', '', institute).strip()
                        
                        # Extract structured details
                        details = extract_details_from_text(detail_text)
                        
                        # Get URL for this course
                        target_url = side_links[url_index]['url'] if url_index < len(side_links) else None
                        
                        # Create CourseRecord
                        record = CourseRecord(
                            row_number=row_id,
                            institute_name=institute,
                            course_name=course_name,
                            mode=details["mode"] if details["mode"] else None,
                            duration=details["duration"] if details["duration"] else None,
                            fees=details["cost"] if details["cost"] else None,
                            country=details["country"] if details["country"] else None,
                            language=details["language"] if details["language"] else None,
                            link=target_url,
                            description=details["skills"] if details["skills"] else None
                        )
                        
                        records.append(record)
                        logger.debug(f"✅ Row {row_id}: {course_name} from {institute}")
                        
                        row_id += 1
                        url_index += 1
                        current_card_blocks = []  # Reset for next card
                        
                    else:
                        current_card_blocks.append(text)
        
        logger.info(f"Vision Parser completed. Extracted {len(records)} records from {len(doc)} pages.")
        doc.close()
        return records
        
    except Exception as e:
        logger.error(f"Vision PDF Parsing failed: {e}")
        return []
