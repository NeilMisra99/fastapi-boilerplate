from typing import Union

from fastapi import FastAPI, HTTPException, Request
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import re
from fastapi.responses import Response
import logging
import os
from pathlib import Path

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.post("/download-ai-slides-pdf")
async def download_ai_slides_pdf(request: Request):
    try:
        data = await request.json()
        html_slides = data.get("slides", [])
        
        if not html_slides:
            raise HTTPException(status_code=400, detail="No slides provided")

        def process_list_items(html_content: str) -> str:
            # Pattern to match li elements containing p and span tags
            # Handles both single and double quotes in style attributes
            pattern = r'<li>\s*<p>\s*<span style=[\'"]([^\'"]+)[\'"]>(.*?)</span>\s*</p>\s*</li>'
            
            # Replace with simplified structure, moving style to li
            replacement = r'<li style="\1">\2</li>'
            
            return re.sub(pattern, replacement, html_content)

        # Process each slide's HTML
        processed_slides = [process_list_items(slide) for slide in html_slides]
        
        # Continue with the rest of your existing HTML template and processing
        full_html = """
        <html>
          <head>
            <meta charset="utf-8">
            <style>
              @font-face {
                font-family: 'Inter';
                font-style: normal;
                font-weight: 100 900;
                src: url('fonts/Inter-VariableFont_opsz,wght.ttf') format('truetype-variations');
              }
              
              @font-face {
                font-family: 'Inter';
                font-style: italic;
                font-weight: 100 900;
                src: url('fonts/Inter-Italic-VariableFont_opsz,wght.ttf') format('truetype-variations');
              }
              
              @page {
                size: landscape;
                margin: 0;
              }
              body { 
                margin: 0; 
                padding: 0;
                font-family: 'Inter', Arial, 'Helvetica Neue', Helvetica, sans-serif;
              }
              .slide {
                font-family: 'Inter', Arial, 'Helvetica Neue', Helvetica, sans-serif;
                position: relative;
                background-color: #ffffff;
                width: 1080px;
                height: 810px;
                margin: 0;
                page-break-after: always;
                overflow: hidden;
              }

              .slide div {
                font-family: 'Inter', Arial, 'Helvetica Neue', Helvetica, sans-serif;
                min-width: 0;
                position: absolute;
                box-sizing: border-box;
                padding: 0;
              }

              .slide img {
                width: 100%;
                height: auto;
                -webkit-user-drag: none;
                user-drag: none;
              }

              .slide h1,
              .slide h2,
              .slide h3,
              .slide h4,
              .slide h5,
              .slide h6,
              .slide p,
              .slide span,
              .slide li,
              .slide div {
                font-family: 'Liberation Sans', Arial, 'Helvetica Neue', Helvetica, sans-serif;
              }
              .slide li::marker {
                color: #0095ff;
              }
              .slide p:last-child {
                margin-bottom: 0 !important;
              }
              .slide p:first-child {
                margin-top: 0 !important;
              }
              .slide ol {
                padding-left: 1.5555556em;
                list-style-type: decimal;
              }
              .slide ul {
                padding-left: 1.5555556em;
                list-style-type: disc;
              }
              .slide ul ul {
                margin-left: 10px;
                list-style-type: circle;
              }
              .slide ul ul ul {
                margin-left: 10px;
                list-style-type: square;
              }
              
              .slide ul li:last-child,
              .slide ol li:last-child {
                margin-bottom: 0.6666667em !important;
              }
              .slide hr {
                border-top: 2px solid rgba(13, 13, 13, 0.1);
                margin: 1rem 0;
              }
              .slide br {
                margin: 0;
              }
              .slide a[href] {
                color: #0095ff;
                text-decoration: underline #0095ff;
              }
              div[data-type="title"] {
                line-height: 1.2;
              }
              div[data-type="title"] strong {
                display: block;  /* Ensure proper spacing */
              }
              div[data-type="paragraph"] {
                overflow: visible;
                word-wrap: break-word;
                line-height: 1.6;
                padding: 0;
              }
              div[data-type="paragraph"] > span {
                display: block;
                width: 100%;
                height: 100%;
                box-sizing: border-box;
              }
              div[data-type="paragraph"] p {
                margin: 0 0 1em 0;
              }
              div[data-type="paragraph"] ul {
                margin: 0.5em 0;
                padding-left: 1.5em;
              }
              div[data-type="paragraph"] li {
                margin-bottom: 0.5em;
                line-height: 1.6;
              }
              [style*="width"],
              [style*="height"] {
                box-sizing: border-box !important;
              }
              [style*="font-size: 20px"] {
                line-height: 1.6;
                letter-spacing: 0.01em;
              }
              div[data-type="image"] {
                display: block;
                page-break-inside: avoid;
              }
              div[data-type="image"] img {
                max-width: 100%;
                height: auto;
                display: block;
              }
              /* Two-column layout support */
              .two-column > * {
                width: 100%;
                overflow-wrap: break-word;
                column-count: 2;
              }
               .two-column-content > div > * {
                width: 100%;
                overflow-wrap: break-word;
                column-count: 2;
              }
              /* Text wrapper functionality */
              text-wrapper-left::after {
                content: "";
                display: table;
                clear: both;
                position: relative;
              }
              
              text-wrapper-right::after {
                content: "";
                display: table;
                clear: both;
                position: relative;
              }
              /* Image alignment rules */
              div:has(div > img):has(+ text-wrapper-left),
              img:has(+ text-wrapper-left) {
                float: left;
                margin-top: 0 !important;
                margin-right: 1rem;
                margin-bottom: 1rem;
              }
              div:has(div > img):has(+ text-wrapper-right),
              img:has(+ text-wrapper-right) {
                float: right;
                margin-top: 0 !important;
                margin-left: 1rem;
                margin-bottom: 1rem;
              }
              /* Updated image styles */
              .slide img {
                width: 100% !important;
                height: 100% !important;
                -webkit-user-drag: none;
                user-drag: none;
                object-fit: contain;
              }
              /* Link hover states */
              .slide a:hover {
                color: #1c89d6;
              }
              /* Adjusted list styles */
              .slide ol,
              .slide ul {
                padding-left: 1.5555556em;
                margin: 0.5em 0;
              }
              .slide ol {
                list-style-type: decimal;
              }
              .slide ul {
                list-style-type: disc;
              }
              .slide ul ul {
                margin-left: 10px;
                list-style-type: circle;
              }
              .slide ul ul ul {
                margin-left: 10px;
                list-style-type: square;
              }
              /* Ensure consistent list styling within the slide */
              .slide ol, .slide ul {
                margin: 0;
                padding-left: 1.5em;
                list-style-position: outside;
              }
              /* If additional tweaking is needed for paragraphs */
              div[data-type="paragraph"] ul {
                margin: 0;
                padding-left: 1.5em;
                list-style-position: outside;
              }
            </style>
          </head>
          <body>
        """

        for slide in processed_slides:
            full_html += f'<div class="slide">{slide}</div>'
        
        full_html += "</body></html>"

        test_html = """
            <div data-type='title' id='e-92f1d83a-f11a-48c5-94ac-af06f282b0d5' style='position: absolute; width: 952px; height: auto; left: 64px; top: 64px;'>
                <p><strong><span style='font-size: 48px; color: #0095FF;'>Agenda today</span></strong></p>
            </div>
            <div data-type='paragraph' id='e-3d432bcd-7e8b-40ab-b119-727c3d4c9561' style='position: absolute; width: 952px; height: 588px; left: 64px; top: 144px;'>
                <ol>
                    <li><p><span style='font-size: 28px;'>The Roots of European Expansion:  Motivation and Early Stages</span></p></li>
                    <li><p><span style='font-size: 28px;'>The Scramble for Africa and Asia: Competition and Colonial Strategies</span></p></li>
                    <li><p><span style='font-size: 28px;'>Comparative Colonial Experiences: Americas, South Asia, and Africa</span></p></li>
                    <li><p><span style='font-size: 28px;'>The Legacy of Colonialism: Social, Economic, and Political Impacts</span></p></li>
                    <li><p><span style='font-size: 28px;'>Decolonization and its Aftermath: Nationalism, Development, and the Cold War</span></p></li>
                </ol>
            </div>
        """

        try:
            # Get the absolute path to the fonts directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            fonts_dir = os.path.join(current_dir, "fonts")
            
            # Make sure the font paths are absolute
            normal_font_path = os.path.join(fonts_dir, "Inter-VariableFont_opsz,wght.ttf")
            italic_font_path = os.path.join(fonts_dir, "Inter-Italic-VariableFont_opsz,wght.ttf")
            
            # Verify font files exist
            if not os.path.exists(normal_font_path) or not os.path.exists(italic_font_path):
                logging.error(f"Font files not found: {normal_font_path}, {italic_font_path}")
                raise HTTPException(status_code=500, detail="Font files not found")
            
            # Create PDF using WeasyPrint with absolute paths to font files
            font_config = FontConfiguration()
            html = HTML(string=full_html)
            css = CSS(string=f'''
                @font-face {{
                    font-family: 'Inter';
                    font-style: normal;
                    font-weight: 100 900;
                    src: url('file://{normal_font_path}') format('truetype-variations');
                }}
                @font-face {{
                    font-family: 'Inter';
                    font-style: italic;
                    font-weight: 100 900;
                    src: url('file://{italic_font_path}') format('truetype-variations');
                }}
                @page {{
                    size: 1080px 810px landscape;
                    margin: 0;
                }}
                body, * {{
                    font-family: 'Inter', sans-serif !important;
                }}
                /* Reset line-height to browser defaults */
                p, div, span, li {{
                    line-height: 1.4 !important;
                }}
            ''', font_config=font_config)
            
            # Generate PDF
            pdf = html.write_pdf(
                stylesheets=[css],
                font_config=font_config,
                presentational_hints=True
            )
            
            return Response(
                content=pdf,
                media_type="application/pdf",
                headers={"Content-Disposition": "attachment; filename=ai_slides.pdf"}
            )
            
        except Exception as e:
            logging.error(f"Error generating PDF: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")
    
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")