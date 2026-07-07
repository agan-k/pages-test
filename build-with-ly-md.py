import os
import shutil
import subprocess
import sys
import re
import markdown
import frontmatter

def compile_lilypond_snippet(ly_code_or_path, base_name, is_file_path=False, path_prefix=""):
    """Compiles a LilyPond file or raw string block into SVG assets in docs/"""
    target_source_path = os.path.join("docs", f"{base_name}.ly")
    
    if is_file_path:
        if os.path.exists(ly_code_or_path):
            shutil.copy2(ly_code_or_path, target_source_path)
        else:
            print(f"⚠️ Warning: Reference path missing: {ly_code_or_path}")
            return ""
    else:
        with open(target_source_path, "w") as f:
            f.write(ly_code_or_path)

    cmd = [
        "lilypond",
        "-dbackend=svg",
        "-dno-point-and-click",
        f"--output=docs/{base_name}",
        target_source_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Core compilation crash on code block: {base_name}")
        print(result.stderr)
        sys.exit(1)
        
    log_file = f"docs/{base_name}.log"
    if os.path.exists(log_file):
        os.remove(log_file)

    page_images = []
    for item in os.listdir("docs"):
        if item.startswith(f"{base_name}-") and item.endswith(".svg"):
            page_images.append(item)
            
    page_images.sort(key=lambda x: [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', x)])
    
    if not page_images:
        single_svg_name = f"{base_name}.svg"
        if os.path.exists(os.path.join("docs", single_svg_name)):
            page_images.append(single_svg_name)
            
    img_block_markup = []
    for svg_page in page_images:
        # Uses the dynamic path_prefix to resolve paths cleanly across folder levels
        tag = f'<img src="{path_prefix}{svg_page}" class="lilypond-score" style="display: block; max-width: 100%; margin-bottom: 20px;" alt="Page from score {base_name}">'
        img_block_markup.append(tag)
        
    return "\n".join(img_block_markup)


def process_lilypond_tags(html_content, unique_page_id, path_prefix=""):
    """Finds both <lilypond file="..." /> and <lilypond>...</lilypond> tags and converts them to SVG images"""
    snippet_counter = 1
    
    file_tags = re.findall(r'<lilypond\s+file=["\']([^"\']+\.ly)["\']\s*/>', html_content)
    for ly_filename in file_tags:
        source_ly_path = os.path.join("content", "lilypond", ly_filename)
        base_name = ly_filename.replace(".ly", "")
        
        img_markup = compile_lilypond_snippet(source_ly_path, base_name, is_file_path=True, path_prefix=path_prefix)
        
        html_content = html_content.replace(f'<lilypond file="{ly_filename}" />', img_markup)
        html_content = html_content.replace(f'<lilypond file=\'{ly_filename}\' />', img_markup)

    block_tags = re.findall(r'<lilypond>(.*?)</lilypond>', html_content, re.DOTALL)
    for raw_code in block_tags:
        clean_code = raw_code.strip()
        base_name = f"snippet-{unique_page_id}-{snippet_counter}"
        
        img_markup = compile_lilypond_snippet(clean_code, base_name, is_file_path=False, path_prefix=path_prefix)
        
        html_content = html_content.replace(f'<lilypond>{raw_code}</lilypond>', img_markup)
        snippet_counter += 1
        
    return html_content


def build_site():
    # 1. WIPE AND RECREATE THE FRESH DOCS FOLDER
    if os.path.exists("docs"):
        print("Cleaning up old build files in docs/...")
        shutil.rmtree("docs")
    
    os.makedirs("docs/articles", exist_ok=True)
    os.makedirs("docs/assets", exist_ok=True)
    print("Created fresh docs/ directory architecture.")
    
    # 2. READ TEMPLATES
    try:
        with open("templates/layout.html", "r") as f: layout = f.read()
        with open("templates/article-layout.html", "r") as f: article_layout = f.read()
        with open("templates/navbar.html", "r") as f: navbar = f.read()
    except FileNotFoundError as e:
        print(f"Error loading assets or layout files: {e}")
        sys.exit(1)
        
    # 3. COPY STATIC ASSETS
    if os.path.exists("assets/style.css"): shutil.copy("assets/style.css", "docs/assets/style.css")
    if os.path.exists("assets/main.js"): shutil.copy("assets/main.js", "docs/assets/main.js")
    if os.path.exists("assets/images"): shutil.copytree("assets/images", "docs/assets/images", dirs_exist_ok=True)

    # 4. PROCESS STANDARD HTML PAGES
    if os.path.exists("pages"):
        for filename in os.listdir("pages"):
            if filename.endswith(".html"):
                with open(f"pages/{filename}", "r") as f:
                    page_content = f.read()
                
                final_html = layout.replace("{{ navbar }}", navbar).replace("{{ content }}", page_content)
                page_id = filename.replace(".html", "")
                
                # Standard pages live in the root, so they don't need a path prefix to find root SVGs
                final_html = process_lilypond_tags(final_html, page_id, path_prefix="")
                
                with open(f"docs/{filename}", "w") as f:
                    f.write(final_html)
                print(f"Compiled page: docs/{filename}")

    # 5. PROCESS MARKDOWN ARTICLES (Looking at content/articles/)
    articles_metadata = []
    source_articles_dir = os.path.join("content", "articles")
    
    if os.path.exists(source_articles_dir):
        for filename in os.listdir(source_articles_dir):
            if filename.endswith(".md"):
                post_path = os.path.join(source_articles_dir, filename)
                
                post = frontmatter.load(post_path)
                post_html_content = markdown.markdown(post.content)
                
                built_article = article_layout
                built_article = built_article.replace("{{ title }}", str(post.get("title", "Untitled")))
                built_article = built_article.replace("{{ date }}", str(post.get("date", "Unknown Date")))
                built_article = built_article.replace("{{ author }}", str(post.get("author", "Anonymous")))
                
                summary_text = post.get("summary", "")
                if summary_text:
                    built_article = built_article.replace("{{ summary }}", str(summary_text))
                    built_article = built_article.replace("{% if summary %}", "").replace("{% endif %}", "")
                else:
                    built_article = re.sub(r'{% if summary %}.*?{% endif %}', '', built_article, flags=re.DOTALL)

                built_article = built_article.replace("{{ content }}", post_html_content)
                final_post_html = layout.replace("{{ navbar }}", navbar).replace("{{ content }}", built_article)
                
                article_id = filename.replace(".md", "")
                
                # Articles live in a subfolder, so they require '../' to reach the root SVGs correctly
                final_post_html = process_lilypond_tags(final_post_html, article_id, path_prefix="../")
                
                output_name = f"articles/{article_id}.html"
                with open(os.path.join("docs", output_name), "w") as f:
                    f.write(final_post_html)
                
                articles_metadata.append({
                    "title": str(post.get("title", "Untitled")),
                    "date": str(post.get("date", "0000-00-00")),
                    "summary": str(summary_text),
                    "url": output_name
                })
                print(f"Compiled blog post article: docs/{output_name}")

    # 6. GENERATE ARTICLES FEED LANDING PAGE (articles.html)
    articles_metadata.sort(key=lambda x: x["date"], reverse=True)
    
    feed_html_list = ["<h1>Latest Articles</h1>", '<ul class="article-feed-list" style="list-style:none; padding:0;">']
    for meta in articles_metadata:
        item = f'''
        <li style="margin-bottom: 25px;">
            <h2><a href="/{meta['url']}">{meta['title']}</a></h2>
            <small style="color:#666;">Published: {meta['date']}</small>
            <p>{meta['summary']}</p>
        </li>
        '''
        feed_html_list.append(item)
    feed_html_list.append("</ul>")
    
    feed_content = "\n".join(feed_html_list)
    final_feed_html = layout.replace("{{ navbar }}", navbar).replace("{{ content }}", feed_content)
    
    with open("docs/articles.html", "w") as f:
        f.write(final_feed_html)
    print("Compiled feed center page directory: docs/articles.html")

    # 7. CLEAN UP EXTRA LEFTOVER TRACKING COPIES IN ROOT
    for file in os.listdir("docs"):
        if file.endswith(".ly"):
            os.remove(os.path.join("docs", file))
            
    print("Build complete! All files generated in docs/.")

if __name__ == "__main__":
    build_site()
