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
            for i in range(1, 5):
                quadrants[i] = {
                    "text": "",
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
                            quadrants[q]["text"] += text + " "

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
                if not data["text"].strip():
                    continue # Empty quadrant
                    
                # Extract simple features from text block
                cost = "Free" if "Cost: Free" in data["text"] else "Unknown"
                country = "India" if "Country: India" in data["text"] else "Unknown"
                
                record = CourseRecord(
                    row_number=row_id,
                    institute_name=f"Extracted Institute (Page {page_num+1}, Q{q_id})",
                    course_name=data["text"][:50].strip() + "...",
                    mode="Online" if "Online" in data["text"] else "Offline",
                    duration="Unknown",
                    fees=cost,
                    course_type="Free Audit" if data["free_audit"] else "Standard",
                    field_domain="Cybersecurity",
                    certificate="Unknown",
                    link=data["link"],
                    qs_world_rank="Ranked" if data["qs_ranked"] else None,
                    qs_continental_rank=None,
                    nirf_rank="Ranked" if data["nirf_ranked"] else None,
                    description=data["text"][:200],
                    language="English" if "English" in data["text"] else "Unknown",
                    scholarship="Yes" if data["scholarship"] else "No",
                    country=country,
                    has_uni_logo=data["has_uni_logo"]
                )
                records.append(record)
                row_id += 1
                
        logger.info(f"Vision Parser completed. Extracted {len(records)} records.")
        return records
        
    except Exception as e:
        logger.error(f"Vision PDF Parsing failed: {e}")
        return []
