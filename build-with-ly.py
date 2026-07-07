import os
import shutil
import subprocess
import sys
import re

def build_site():
    # 1. WIPE AND RECREATE THE FRESH DOCS FOLDER
    if os.path.exists("docs"):
        print("Cleaning up old build files in docs/...")
        shutil.rmtree("docs")
    
    os.makedirs("docs/assets", exist_ok=True)
    print("Created fresh docs/ directory.")
    
    # 2. READ TEMPLATES
    try:
        with open("templates/layout.html", "r") as f:
            layout = f.read()
        with open("templates/navbar.html", "r") as f:
            navbar = f.read()
    except FileNotFoundError as e:
        print(f"Error loading template assets: {e}")
        sys.exit(1)
        
    # 3. COPY STATIC ASSETS
    if os.path.exists("assets/style.css"):
        shutil.copy("assets/style.css", "docs/assets/style.css")
    if os.path.exists("assets/main.js"):
        shutil.copy("assets/main.js", "docs/assets/main.js")
    if os.path.exists("assets/images"):
        shutil.copytree("assets/images", "docs/assets/images", dirs_exist_ok=True)

    # 4. PARSE PAGES AND COMPILE CORES NATIVELY
    for filename in os.listdir("pages"):
        if filename.endswith(".html"):
            with open(f"pages/{filename}", "r") as f:
                page_content = f.read()
            
            # Stitch the base layout templates together
            final_html = layout.replace("{{ navbar }}", navbar)
            final_html = final_html.replace("{{ content }}", page_content)
            
            # Find all <lilypond file="filename.ly" /> markup formats
            lilypond_tags = re.findall(r'<lilypond\s+file=["\']([^"\']+\.ly)["\']\s*/>', final_html)
            
            for ly_filename in lilypond_tags:
                source_ly_path = os.path.join("assets/lilypond", ly_filename)
                base_name = ly_filename.replace(".ly", "")
                
                if os.path.exists(source_ly_path):
                    print(f"Processing structural vector compilation for: {ly_filename}")
                    
                    # Direct engine command outputting scalable vector files directly to docs/
                    cmd = [
                        "lilypond",
                        "-dbackend=svg",
                        "-dno-point-and-click",
                        f"--output=docs/{base_name}",
                        source_ly_path
                    ]
                    
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    
                    if result.returncode != 0:
                        print(f"❌ Core compilation crash on file: {ly_filename}")
                        print(result.stderr)
                        sys.exit(1)
                    
                    # Clean up random intermediate logs and backend structural artifacts
                    log_file = f"docs/{base_name}.log"
                    if os.path.exists(log_file):
                        os.remove(log_file)
                        
                    # --- DYNAMIC MULTI-PAGE & ONE-PAGE SEARCH ENGINE ---
                    page_images = []
                    
                    # Step A: Look for standard numbered multi-page splits (music-1.svg, music-2.svg...)
                    for item in os.listdir("docs"):
                        if item.startswith(f"{base_name}-") and item.endswith(".svg"):
                            page_images.append(item)
                    
                    # Sort them naturally so page-1 comes before page-2
                    page_images.sort(key=lambda x: [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', x)])
                    
                    # Step B: Edge Case Check - If no numbered files exist, look for a single continuous file (music.svg)
                    if not page_images:
                        single_svg_name = f"{base_name}.svg"
                        if os.path.exists(os.path.join("docs", single_svg_name)):
                            page_images.append(single_svg_name)
                    
                    # Construct image tags stacking every found page cleanly underneath each other
                    img_block_markup = []
                    for svg_page in page_images:
                        tag = f'<img src="{svg_page}" class="lilypond-score" style="display: block; max-width: 100%; margin-bottom: 20px;" alt="Page from score {base_name}">'
                        img_block_markup.append(tag)
                    
                    # Combine all generated image elements into a clean HTML block
                    html_img_replacement = "\n".join(img_block_markup)
                    
                    # Swap your custom tag with the complete sequential page stack
                    final_html = final_html.replace(f'<lilypond file="{ly_filename}" />', html_img_replacement)
                    final_html = final_html.replace(f'<lilypond file=\'{ly_filename}\' />', html_img_replacement)
                else:
                    print(f"⚠️ Warning: Referenced asset path missing from workspace: {source_ly_path}")

            # 5. DEPLOY RAW .LY DOWNLOAD ABILITIES AS BACKUPS
            ly_source_dir = "assets/lilypond"
            if os.path.exists(ly_source_dir):
                for ly_file in os.listdir(ly_source_dir):
                    if ly_file.endswith(".ly"):
                        shutil.copy2(os.path.join(ly_source_dir, ly_file), os.path.join("docs", ly_file))

            # Write the completed output document tree out to disk
            with open(f"docs/{filename}", "w") as f:
                f.write(final_html)
            print(f"Successfully deployed structural layout: docs/{filename}")

    print("Build complete! All vector tracks processed securely.")

if __name__ == "__main__":
    build_site()
    