import urllib.request
from html.parser import HTMLParser

# Database ccSLD Populer Dunia untuk Filter Tambahan
POPULAR_CCSLDS = [
    # Indonesia (.id)
    ".co.id", ".web.id", ".my.id", ".biz.id", ".org.id", ".net.id", ".ac.id", ".sch.id", ".go.id",
    # United Kingdom (.uk)
    ".co.uk", ".org.uk", ".me.uk", ".net.uk", ".ltd.uk",
    # Australia (.au)
    ".com.au", ".net.au", ".org.au", ".id.au",
    # Japan (.jp)
    ".co.jp", ".ne.jp", ".or.jp",
    # Singapore (.sg)
    ".com.sg", ".net.sg", ".org.sg",
    # India (.in)
    ".co.in", ".net.in", ".org.in", ".ind.in",
    # Brazil (.br)
    ".com.br", ".net.br", ".org.br",
    # New Zealand (.nz)
    ".co.nz", ".net.nz", ".org.nz",
    # Mexico (.mx)
    ".com.mx", ".net.mx", ".org.mx",
    # South Africa (.za)
    ".co.za", ".org.za", ".web.za",
    # USA / US (.us)
    ".is.us", ".isa.us",
    # Spain (.es)
    ".com.es", ".org.es", ".nom.es"
]


class RootTableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_tr = False
        self.in_td = False
        self.current_row = []
        self.rows = []

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.in_tr = True
            self.current_row = []
        elif tag == "td" and self.in_tr:
            self.in_td = True

    def handle_endtag(self, tag):
        if tag == "tr" and self.in_tr:
            self.in_tr = False
            if len(self.current_row) >= 2:
                self.rows.append(self.current_row)
        elif tag == "td" and self.in_td:
            self.in_td = False

    def handle_data(self, data):
        if self.in_td:
            text = data.strip()
            if text:
                if len(self.current_row) < 3:
                    self.current_row.append(text)
                else:
                    self.current_row[-1] += " " + text


def map_type_label(raw_type: str) -> str:
    mapping = {
        "generic": "gTLD",
        "country-code": "ccTLD",
        "sponsored": "sTLD",
        "generic-restricted": "grTLD",
        "infrastructure": "iTLD",
        "test": "tTLD",
    }
    return mapping.get(raw_type.lower(), raw_type)


def fetch_tlds_with_types(suffix="e"):
    url = "https://www.iana.org/domains/root/db"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    results = []
    clean_suffix = suffix.lower().strip().lstrip(".")

    try:
        with urllib.request.urlopen(req) as response:
            html_content = response.read().decode("utf-8")

        parser = RootTableParser()
        parser.feed(html_content)

        for row in parser.rows:
            if len(row) >= 2:
                raw_domain = row[0].strip()
                raw_type = row[1].strip()

                domain = (
                    raw_domain.lower()
                    if raw_domain.startswith(".")
                    else f".{raw_domain.lower()}"
                )
                clean_name = domain.lstrip(".")

                if clean_name.endswith(clean_suffix) and not clean_name.startswith("xn--"):
                    results.append({
                        "domain": domain,
                        "type": map_type_label(raw_type),
                        "type_raw": raw_type,
                    })

    except Exception as e:
        print(f"Error fetching root data: {e}")

    for ccsld in POPULAR_CCSLDS:
        clean_ccsld = ccsld.lower().strip().lstrip(".")
        if clean_ccsld.endswith(clean_suffix):
            if not any(item["domain"] == ccsld for item in results):
                results.append({
                    "domain": ccsld,
                    "type": "ccSLD",
                    "type_raw": "country-code second level",
                })

    return results


def export_to_html(data, target_char="e", filename=None):
    # Nama file fisik di disk tetap .html agar bisa dibaca server
    file_disk_name = f"{target_char}.html" if not filename else filename

    ccslds = [item for item in data if item["type"] == "ccSLD"]
    cctlds = [item for item in data if item["type"] == "ccTLD"]
    gtlds = [item for item in data if item["type"] not in ["ccTLD", "ccSLD"]]

    cards_html = ""

    for item in ccslds:
        cards_html += f'                        <div class="tld-card ccsld"><span class="domain-text">{item["domain"]}</span><span class="type-label">ccSLD</span></div>\n'

    for item in cctlds:
        cards_html += f'                        <div class="tld-card cctld"><span class="domain-text">{item["domain"]}</span><span class="type-label">cc</span></div>\n'

    for item in gtlds:
        cards_html += f'                        <div class="tld-card"><span class="domain-text">{item["domain"]}</span><span class="type-label">{item["type"]}</span></div>\n'

    page_title = f"TLDs Ending with '{target_char}' — Korvali TLD"
    page_desc = f"Browse all {len(data)} top-level domains (TLDs) and ccSLDs ending with letter '{target_char}'. Powered by Korvali Infrastructure."
    
    # 🌟 CLEAN URL SEO: Tanpa ekstensi .html di atribut meta!
    page_url = f"https://tld.korvali.net/{target_char}"

    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=yes" />
    <title>{page_title}</title>
    
    <!-- Primary Meta Tags -->
    <meta name="title" content="{page_title}" />
    <meta name="description" content="{page_desc}" />
    <meta name="keywords" content="TLD ending with {target_char}, domain hacks, Korvali tld list, ccSLD, Korvali TLD, domain extension {target_char}" />
    <meta name="robots" content="index, follow" />

    <!-- Clean Canonical URL -->
    <link rel="canonical" href="{page_url}" />

    <!-- Open Graph / Link Preview (Clean URL) -->
    <meta property="og:type" content="website" />
    <meta property="og:url" content="{page_url}" />
    <meta property="og:title" content="{page_title}" />
    <meta property="og:description" content="{page_desc}" />
    <meta property="og:image" content="https://korvali.net/img/korvali.jpg" />
    <meta property="og:site_name" content="Korvali TLD" />

    <!-- Twitter Card (Clean URL) -->
    <meta property="twitter:card" content="summary_large_image" />
    <meta property="twitter:url" content="{page_url}" />
    <meta property="twitter:title" content="{page_title}" />
    <meta property="twitter:description" content="{page_desc}" />
    <meta property="twitter:image" content="https://korvali.net/img/korvali.jpg" />

    <!-- Favicon & App Icons -->
    <link rel="icon" type="image/png" sizes="128x128" href="/favicon.png" />
    <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
    <meta name="application-name" content="Korvali TLD" />
    <meta name="apple-mobile-web-app-title" content="Korvali TLD" />

    <!-- Structured Data (Clean URL) -->
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "WebPage",
      "name": "{page_title}",
      "description": "{page_desc}",
      "url": "{page_url}",
      "publisher": {{
        "@type": "Organization",
        "name": "Korvali Infrastructure",
        "url": "https://korvali.net"
      }}
    }}
    </script>

    <link rel="stylesheet" href="https://korvali.net/playground.css" />

    <style>
        html, body {{
            height: auto !important;
            min-height: 100vh !important;
            overflow-x: hidden !important;
            overflow-y: auto !important;
        }}

        body {{
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: flex-start !important;
            padding: 16px 8px 40px 8px !important;
        }}

        .tld-page-wrapper {{
            width: 100%;
            max-width: 820px;
            margin: 0 auto;
        }}

        .tld-flex-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px 6px;
            margin-top: 14px;
            align-items: center;
        }}

        .tld-card {{
            background: rgba(2, 4, 10, 0.6);
            border: 1px solid rgba(34, 211, 238, 0.15);
            padding: 6px 10px;
            border-radius: 8px;
            font-size: 12.5px;
            color: #a5f3fc;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            white-space: nowrap;
            flex-grow: 1;
            transition: border-color 0.2s, transform 0.15s;
        }}

        .tld-card:hover {{
            border-color: rgba(34, 211, 238, 0.4);
            transform: translateY(-2px);
        }}

        .tld-card .domain-text {{
            font-weight: 700;
        }}

        .tld-card.cctld {{
            border-color: rgba(251, 191, 36, 0.25);
            color: #fbbf24;
            background: rgba(251, 191, 36, 0.05);
        }}

        .tld-card.ccsld {{
            border-color: rgba(74, 222, 128, 0.3);
            color: #4ade80;
            background: rgba(74, 222, 128, 0.06);
        }}

        .tld-card .type-label {{
            font-size: 8.5px;
            opacity: 0.5;
            font-weight: 600;
            text-transform: uppercase;
            margin-left: auto;
        }}

        @media (max-width: 400px) {{
            .tld-card {{
                padding: 5px 8px;
                font-size: 11.5px;
            }}
        }}
    </style>
</head>
<body>

    <div class="tld-page-wrapper">
        <div class="terminal-wrapper" style="max-height: none; margin-bottom: 0;">

            <div class="terminal-header">
                <div class="header-dots">
                    <span class="dot-red"></span>
                    <span class="dot-yellow"></span>
                    <span class="dot-green"></span>
                </div>
                <div class="header-title">
                    <strong>Korvali TLD</strong> &#x00B7; Filter: '{target_char}'
                </div>
                <span class="header-version">Korvali Database</span>
            </div>

            <div class="info-modal-body" style="background: rgba(2, 4, 10, 0.3);">
                <div class="modal-section">
                    <h1 class="page-title">
                        TLDs Ending with <span class="highlight">'{target_char}'</span>
                    </h1>
                    <div class="page-subtitle">
                        Total Found: <strong class="cyan">{len(data)} Domains</strong> (Excluding Punycode)
                    </div>

                    <p class="body-text" style="font-size: 11.5px; opacity: 0.75;">
                        <span style="color: #4ade80;">■ ccSLD</span> = Country-Code Second-Level &#x00B7; 
                        <span style="color: #fbbf24;">■ ccTLD</span> = Country-Code Top-Level &#x00B7; 
                        <span style="color: #22d3ee;">■ gTLD</span> = Generic Domain
                    </p>

                    <hr class="divider" />

                    <div class="tld-flex-container">
{cards_html}                    </div>

                    <hr class="divider" style="margin-top: 24px;" />

                    <div class="donation-container" style="margin-top: 10px;">
                        <div class="donation-card">
                            <div class="donation-info">
                                <span class="donation-icon">&#9889;</span>
                                <div>
                                    <p class="donation-title">Power Korvali Infrastructure</p>
                                    <p class="donation-sub">Support edge servers, domain renewals, and keep tools free forever.</p>
                                </div>
                            </div>
                            <div class="donation-buttons">
                                <a href="https://sociabuzz.com/korvali/support" target="_blank" rel="noopener" class="donate-btn donate-idr">
                                    &#127470;&#127465; IDR 
                                </a>
                                <a href="https://ko-fi.com/korvali" target="_blank" rel="noopener" class="donate-btn donate-kofi">
                                    &#9749; USD 
                                </a>
                                <a href="https://nowpayments.io/donation/korvali" target="_blank" rel="noopener" class="donate-btn donate-crypto">
                                    &#8383; Crypto
                                </a>
                            </div>
                        </div>
                    </div>

                    <hr class="divider" style="margin-top: 20px;" />

                    <div style="text-align: center;">
                        <a href="https://korvali.net" class="line text-cyan url-highlight" style="font-size: 13px;">&#x2190; Powered by Korvali Infrastructure</a>
                    </div>

                </div>
            </div>
        </div>
    </div>

</body>
</html>
"""

    with open(file_disk_name, "w", encoding="utf-8") as f:
        f.write(html_template)

    print(f"\n🚀 Success! Created '{file_disk_name}' with 100% Korvali Branding.")


if __name__ == "__main__":
    user_input = input("Enter TLD/SLD suffix (e.g., e, io, ai, id): ").strip()
    
    if not user_input:
        user_input = "e"

    clean_suffix = user_input.lstrip(".")

    print(f"\n[+] Processing TLD/ccSLD data ending with '{clean_suffix}'...")
    tld_data = fetch_tlds_with_types(suffix=clean_suffix)

    if tld_data:
        export_to_html(tld_data, target_char=clean_suffix)
    else:
        print(f"❌ No TLD/SLD found ending with '{clean_suffix}'.")
