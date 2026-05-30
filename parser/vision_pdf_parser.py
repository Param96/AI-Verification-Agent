import fitz  # PyMuPDF
import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Any
from utils.logger import logger
from utils.schema import CourseRecord

def unscramble_text(text: str) -> str:
    """
    Decodes the custom ASCII offset (-29) found in the scrambled PDF.
    """
    decoded = ""
    for char in text:
        # Only shift typical printable scrambled characters
        if 32 <= ord(char) <= 126:
            new_char = chr(ord(char) + 29)
            # Ensure it stays in printable range for our specific cipher
            if ord(new_char) <= 126:
                decoded += new_char
            else:
                decoded += char
        else:
            decoded += char
    return decoded.strip()

def get_quadrant(x: float, y: float, width: float, height: float) -> int:
    """
    Returns 1 (Top-Left), 2 (Top-Right), 3 (Bottom-Left), 4 (Bottom-Right).
    """
    mid_x = width / 2
    mid_y = height / 2
    if x < mid_x and y < mid_y: return 1
    if x >= mid_x and y < mid_y: return 2
    if x < mid_x and y >= mid_y: return 3
    if x >= mid_x and y >= mid_y: return 4

def parse_pdf_vision(file_path: Path) -> List[CourseRecord]:
    """Custom Computer Vision & Spatial PDF Parser."""
    logger.info(f"Vision Parsing PDF: {file_path}")
    records = []
    
    try:
        doc = fitz.open(file_path)
        row_id = 1
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            width = page.rect.width
            height = page.rect.height
            
            # Quadrant data buckets
            quadrants = {1: {}, 2: {}, 3: {}, 4: {}}
            page_domain = "Unknown"
            
            for i in range(1, 5):
                quadrants[i] = {
                    "text": "",
                    "spans": [],
                    "link": None,
                    "qs_ranked": False,
                    "nirf_ranked": False,
                    "scholarship": False,
                    "free_audit": False,
                    "has_uni_logo": False
                }

            # 1. Extract Links
            for link in page.get_links():
                if link['kind'] == fitz.LINK_URI:
                    rect = link['from']
                    q = get_quadrant(rect.x0, rect.y0, width, height)
                    quadrants[q]["link"] = link['uri']

            # 2. Extract Text & Unscramble
            blocks = page.get_text("dict")["blocks"]
            for b in blocks:
                if "lines" in b:
                    for line in b["lines"]:
                        for span in line["spans"]:
                            q = get_quadrant(span["bbox"][0], span["bbox"][1], width, height)
                            # Unscramble if it looks like the garbled text
                            text = span["text"]
                            if "%" in text or "\\" in text or "]" in text: 
                                text = unscramble_text(text)
                            
                            y, x = span["bbox"][1], span["bbox"][0]
                            if y < 40:
                                if "FREE" not in text.upper() and len(text.strip()) > 3:
                                    page_domain = text.strip()
                                elif "FREE COURSE" in text.upper():
                                    page_domain = "Free Courses"
                                continue # Skip adding header text to the course block
                                    
                            quadrants[q]["spans"].append({
                                "text": text,
                                "y": y,
                                "x": x
                            })

            # 3. Detect Logos (Vision/Image Bounding Boxes)
            # In a full production CV pipeline, we would render the page to an image
            # and use cv2.matchTemplate() to find the QS/NIRF logos.
            # For now, we detect ANY embedded image in the bottom-right of the quadrant 
            # and set boolean flags.
            for img in page.get_images(full=True):
                xref = img[0]
                rects = page.get_image_rects(xref)
                for rect in rects:
                    q = get_quadrant(rect.x0, rect.y0, width, height)
                    
                    # Calculate local coordinates within the quadrant to classify the logo
                    local_x = rect.x0 if (q == 1 or q == 3) else rect.x0 - (width / 2)
                    local_y = rect.y0 if (q == 1 or q == 2) else rect.y0 - (height / 2)
                    
                    quad_width = width / 2
                    quad_height = height / 2
                    
                    if local_y < (quad_height / 3) and local_x > (quad_width / 2):
                        # Top-Right area of the quadrant -> University Logo
                        quadrants[q]["has_uni_logo"] = True
                    else:
                        # Bottom area -> QS / NIRF / Scholarship logos
                        quadrants[q]["qs_ranked"] = True
                        quadrants[q]["scholarship"] = True

            # 4. Compile Records
            for q_id, data in quadrants.items():
                if not data["spans"]:
                    continue # Empty quadrant
                    
                # 5. Regex Feature Extraction
                # Sort spans visually: top-to-bottom, left-to-right
                data["spans"].sort(key=lambda s: (round(s["y"] / 8), s["x"]))
                full_text = " ".join([s["text"].strip() for s in data["spans"] if s["text"].strip()])
                
                import re
                
                cost_match = re.search(r'Cost:\s*(\S+)', full_text, re.IGNORECASE)
                mode_match = re.search(r'Mode:\s*(\S+)', full_text, re.IGNORECASE)
                country_match = re.search(r'Country:\s*(\S+)', full_text, re.IGNORECASE)
                duration_match = re.search(r'Duration:\s*(\S+)', full_text, re.IGNORECASE)
                language_match = re.search(r'Language:\s*(\S+)', full_text, re.IGNORECASE)
                skills_match = re.search(r'Skills:\s*(.*?)(?:Link to course|$)', full_text, re.IGNORECASE)
                domain_match = re.search(r'Domain:\s*(.*?)(?:Cost:|Mode:|Country:|Duration:|Language:|Skills:|$)', full_text, re.IGNORECASE)
                header_text = full_text.split("Cost:")[0].strip() if "Cost:" in full_text else full_text[:100]
                
                # Smart split of header text into Course Name and Institute Name
                header_spans = []
                for s in data["spans"]:
                    if "Cost:" in s["text"]:
                        break
                    if s["text"].strip():
                        header_spans.append(s["text"].strip())
                        
                institute_name = header_spans[0] if header_spans else header_text
                course_name = " ".join(header_spans[1:]) if len(header_spans) > 1 else institute_name
                
                extracted_domain = page_domain
                if domain_match:
                    extracted_domain = domain_match.group(1).strip()
                elif "FREE COURSE" in full_text.upper() or extracted_domain == "Unknown":
                    extracted_domain = page_domain if page_domain != "Unknown" else "General"
                
                # Filter out legend/footer boxes that are not actual courses
                if "NIRF Ranked Institute" in header_text or "Free To Audit Course" in header_text:
                    continue
                if not (cost_match or mode_match or duration_match or country_match) and not data["link"]:
                    continue
                
                record = CourseRecord(
                    row_number=row_id,
                    institute_name=institute_name,
                    course_name=course_name,
                    mode=mode_match.group(1) if mode_match else "Online",
                    duration=duration_match.group(1) if duration_match else "Unknown",
                    fees=cost_match.group(1) if cost_match else "Unknown",
                    course_type="Free Audit" if data["free_audit"] else "Standard",
                    field_domain=extracted_domain,
                    certificate="Unknown",
                    link=data["link"],
                    qs_world_rank="Ranked" if data["qs_ranked"] else None,
                    qs_continental_rank=None,
                    nirf_rank="Ranked" if data["nirf_ranked"] else None,
                    description=skills_match.group(1).strip() if skills_match else full_text[:200],
                    language=language_match.group(1) if language_match else "English",
                    scholarship="Yes" if data["scholarship"] else "No",
                    country=country_match.group(1) if country_match else "Unknown",
                    has_uni_logo=data["has_uni_logo"]
                )
                records.append(record)
                row_id += 1
                
        logger.info(f"Vision Parser completed. Extracted {len(records)} records.")
        return records
        
    except Exception as e:
        logger.error(f"Vision PDF Parsing failed: {e}")
        return []
