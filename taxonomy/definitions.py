CYBERSECURITY_TAXONOMY = {
    "Foundational Domains": [
        "Information Security",
        "Computer Security",
        "Cyberspace Security",
        "Introductory Cybersecurity",
        "Cybersecurity",
        "Cyber Security",
    ],
    "Network & Infrastructure Security": [
        "Network Security",
        "Web Security",
        "Cloud Security",
        "IoT Security",
        "Defensive Security",
        "Network Defense and Protection",
        "Cloud Infrastructure Defense",
    ],
    "System & Endpoint Security": [
        "System Security",
        "Operating Systems Security",
        "Endpoint Security",
        "Mobile Security",
        "Biometric Security",
        "Endpoint Protection",
    ],
    "Application & Data Security": [
        "Application Security",
        "Web Application Security",
        "Mobile Application Security",
        "Software Security",
        "Data Security",
        "Database Security",
    ],
    "Cyber Forensics & Investigation": [
        "Cyber Forensics",
        "Digital Forensics",
        "Mobile Forensics",
        "Computer Forensics",
        "Data Forensics",
        "Network Forensics",
    ],
    "Legal, Ethical & Strategic Security": [
        "Cyber Law",
        "Ethical Hacking",
        "Offensive Security",
        "Penetration Testing",
        "Penetration Testing and Red Teaming",
        "Red Teaming",
        "Exploit Development",
    ],
}


def get_all_subdomains():
    """Flattens the taxonomy into a single list of all subdomains."""
    subdomains = []
    for domain, subs in CYBERSECURITY_TAXONOMY.items():
        subdomains.extend(subs)
    return subdomains
