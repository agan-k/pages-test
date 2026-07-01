import os
import shutil

def build_site():
    # 1. Clear out the old build and create fresh directories
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    os.makedirs("dist/assets", exist_ok=True)
    
    # 2. Read the layout into memory
    with open("templates/layout.html", "r") as f:
        layout = f.read()
        
    # 3. Copy the CSS and JS files directly to the production folder
    if os.path.exists("assets/style.css"):
        shutil.copy("assets/style.css", "dist/assets/style.css")
    if os.path.exists("assets/main.js"):
        shutil.copy("assets/main.js", "dist/assets/main.js")

    # 4. Compile the pages
    for filename in os.listdir("pages"):
        if filename.endswith(".html"):
            with open(f"pages/{filename}", "r") as f:
                page_content = f.read()
            
            # Stitch the page content into the layout template
            final_html = layout.replace("{{ content }}", page_content)
            
            with open(f"dist/{filename}", "w") as f:
                f.write(final_html)
                
            print(f"Compiled: dist/{filename}")

if __name__ == "__main__":
    build_site()
