import os
import shutil

def build_site():
    # 1. COMPLETELY WIPE THE OLD docs FOLDER
    # This prevents ghost files, old versions, or deleted pages from staying in docs/
    if os.path.exists("docs"):
        print("Cleaning up old build files...")
        shutil.rmtree("docs")
    
    # 2. Recreate the fresh, empty directory structure
    os.makedirs("docs/assets", exist_ok=True)
    print("Created fresh docs/ directory.")
    
    # 3. Read the layout and navbar templates into memory
    with open("templates/layout.html", "r") as f:
        layout = f.read()
        
    with open("templates/navbar.html", "r") as f:
        navbar = f.read()
        
    # 4. Copy current CSS and JS files to the fresh production folder
    if os.path.exists("assets/style.css"):
        shutil.copy("assets/style.css", "docs/assets/style.css")
    if os.path.exists("assets/main.js"):
        shutil.copy("assets/main.js", "docs/assets/main.js")

    # 5. Compile the pages fresh
    for filename in os.listdir("pages"):
        if filename.endswith(".html"):
            with open(f"pages/{filename}", "r") as f:
                page_content = f.read()
            
            # Stitch the navbar and page content into the layout template
            final_html = layout.replace("{{ navbar }}", navbar)
            final_html = final_html.replace("{{ content }}", page_content)
            
            with open(f"docs/{filename}", "w") as f:
                f.write(final_html)
                
            print(f"Compiled: docs/{filename}")
            
    print("Build complete! Ready for deployment.")

if __name__ == "__main__":
    build_site()
