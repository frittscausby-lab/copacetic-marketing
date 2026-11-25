"""Copacetic Marketing, built on The Pinnacle template (frittscausby-lab/site-template).

python3 build.py          -> dist/     (deploy build, clean addresses, for GitHub Pages)
python3 build.py preview  -> preview/  (links point at index.html so pages open anywhere)
"""
import json, os, re, shutil, sys, html, hashlib
from industries import INDUSTRIES, NEW_POSTS, NEW_IMG

PREVIEW = len(sys.argv) > 1 and sys.argv[1] == "preview"
OUT = "preview" if PREVIEW else "dist"
DOMAIN = "https://copacetic.marketing"
EMAIL = os.environ.get("COPACETIC_EMAIL", "")          # contact address, supplied at build time
CONTACT_URL = "https://www.frittscausby.com/contact"   # used when no address is supplied
FC = "https://www.frittscausby.com"
PIN = "https://thepinnacle.ink/articles"

CSS_V = hashlib.md5(open("assets/style.css", "rb").read()).hexdigest()[:8]
PAGES = {"home": "", "services": "services-1", "press": "press-release-services", "ghost": "ghostwriting",
         "c2c": "conference-to-content", "about": "about", "blog": "blog", "industries": "industries"}
PAGES.update({d["key"]: "industries/" + d["slug"] for d in INDUSTRIES})
IND_MENU = [(d["key"], d["label"]) for d in INDUSTRIES]
# Services menu: items with their own page link to it; the rest are listed without a link for now
MENU = [("press", "Press Releases"), ("ghost", "Ghostwriting"), ("c2c", "Conference to Content"),
        ("ind-realestate", "Real Estate and Listing Writing"), (None, "Sponsored Content"), (None, "Newsletters"),
        (None, "Video Scripts"), (None, "Reputation Management"), (None, "Website Building")]
NAV = [("about", "About"), ("blog", "Blog")]


def depth(p):
    return len([x for x in p.split("/") if x])


def rel(to_path, here):
    up = "../" * depth(here)
    if PREVIEW:
        return f"{up}{to_path + '/' if to_path else ''}index.html"
    if to_path == "":
        return up or "./"
    return f"{up}{to_path}/"


def link(k, here):
    return rel(PAGES[k], here)


IMG = {
    "q10": ("photo-1757356657991-c3fd6e2e812e", "Michael Brown", "vettexan", "Modern luxury home with swimming pools at dusk"),
    "q11": ("photo-1501504905252-473c47e087f8", "Nick Morrison", "nickmorrison", "Laptop and open notebook on a desk"),
    "q12": ("photo-1599008633840-052c7f756385", "Kelly Sikkema", "kellysikkema", "Blank notebook and pen on a wooden bench"),
    "q13": ("photo-1540575467063-178a50c2df87", "Headway", "headwayio", "Audience seated at a conference session"),
    "q14": ("photo-1769092992534-f2d0210162b9", "Ilya Semenov", "si1og", "Library shelves filled with old books"),
    "q15": ("photo-1516280440614-37939bbacd81", "Bogomil Mihaylov", "bogomi", "Microphone on a stand"),
    "qnew": ("photo-1587825140708-dfaf72ae4b04", "Alexandre Pellaes", "apellaes", "Speaker on stage addressing a large audience"),
    "q17": ("photo-1555636222-cae831e670b3", "FilterGrade", "filtergrade", "Residential street lined with houses and palm trees"),
    "q20": ("photo-1524668951403-d44b28200ce0", "Pereanu Sebastian", "sebastian123", "Vintage typewriter"),
    "q21": ("photo-1455390582262-044cdead277a", "Aaron Burden", "aaronburden", "Fountain pen on lined paper"),
    "q22": ("photo-1758599668429-121d54188b9c", "Vitaly Gariev", "silverkblack", "Volunteers caring for a community park"),
    "arch": ("photo-1766603636700-e9d80473f40f", "Alef Morais", "alef_visuals", "Modern house with large windows and a green lawn"),
    "c2c": ("photo-1505373877841-8d25f7d46678", "Teemu Paananen", "xteemu", "Presenter in front of a large screen at a conference"),
    "press": ("photo-1504711434969-e33886168f5c", "AbsolutVision", "codzilla_swiss", "Business pages of a newspaper"),
    "news": ("photo-1773158742082-6f26389f7492", "Viva Reella", "vivareella", "Phone, laptop and coffee on a desk"),
    "web": ("photo-1522542550221-31fd19575a2d", "Hal Gatewood", "halacious", "Sketches of website layouts"),
}
IMG.update(NEW_IMG)
UTM = "utm_source=copacetic_marketing&utm_medium=referral"


def img_url(k, w=1600, h=900):
    return f"https://images.unsplash.com/{IMG[k][0]}?w={w}&h={h}&fit=crop&crop=entropy&auto=format&q=80"


def figure(k, w=1600, h=900, eager=False):
    pid, name, user, alt = IMG[k]
    return (f'<figure><img src="{img_url(k, w, h)}" alt="{alt}" width="{w}" height="{h}" loading="{"eager" if eager else "lazy"}">'
            f'<figcaption>Photo by <a href="https://unsplash.com/@{user}?{UTM}">{name}</a> on '
            f'<a href="https://unsplash.com/?{UTM}">Unsplash</a></figcaption></figure>')


def mail():
    return f"mailto:{EMAIL}" if EMAIL else CONTACT_URL


def contact_inline():
    return f'<a href="{mail()}">{EMAIL}</a>' if EMAIL else f'<a href="{CONTACT_URL}">frittscausby.com/contact</a>'


def cta(title, text, label="Contact"):
    return (f'<div class="cta-band"><div class="cta-band-text"><h4>{title}</h4><p>{text}</p></div>'
            f'<a href="{mail()}" class="btn-primary">{label} &rarr;</a></div>')


def header_block(tag, h1, subtitle):
    sub = f'<p class="subtitle">{subtitle}</p>' if subtitle else ""
    return (f'<div class="article-header"><div class="article-header-inner"><div class="article-tag">{tag}</div>'
            f'<h1>{h1}</h1>{sub}</div></div>')


def menu_items(key, here, items=None):
    return "".join(
        (f'<li><a href="{link(k, here)}"{" aria-current=page" if k == key else ""}>{label}</a></li>' if k
         else f'<li><span>{label}</span></li>') for k, label in (items or MENU))


def sidebar(key, here):
    items = menu_items(key, here)
    return f'''<aside class="sidebar">
    <div class="sidebar-subscribe"><h4>Services</h4>
      <p>Press releases, ghostwriting and marketing content for businesses nationwide.</p>
      <ul class="side-services">{items}</ul>
      <a href="{mail()}" class="btn-primary" style="display:block;text-align:center;">Start a project &rarr;</a></div>
    <div class="side-box"><span class="sidebar-affiliate-label">More from Fritts</span>
      <a class="site" href="{FC}">frittscausby.com</a><p>Freelance writing portfolio and published clips</p>
      <a class="site" href="https://thepinnacle.ink">The Pinnacle</a><p>Luxury real estate, financial markets and the aspirational lifestyle</p></div>
  </aside>'''


def page(key, title, desc, top, main, here=None, og_image=None, schema=None):
    here = PAGES[key] if here is None else here
    up = "../" * depth(here)
    canonical = f"{DOMAIN}/{here + '/' if here else ''}"
    on_svc = key in ("services", "press", "ghost", "c2c")
    nav = (f'<div class="dd"><a href="{link("services", here)}" class="dd-top"{" aria-current=page" if on_svc else ""} aria-haspopup="true">Services <span class="caret" aria-hidden="true">&#9662;</span></a>'
           f'<ul class="dd-menu">{menu_items(key, here)}</ul></div>' +
           f'<div class="dd"><a href="{link("industries", here)}" class="dd-top"{" aria-current=page" if key.startswith("ind") else ""} aria-haspopup="true">Industries <span class="caret" aria-hidden="true">&#9662;</span></a>'
           f'<ul class="dd-menu">{menu_items(key, here, [("industries", "All industries")] + IND_MENU)}</ul></div>' +
           "".join(f'<a href="{link(k, here)}"{" aria-current=page" if k == key else ""}>{lab}</a>' for k, lab in NAV))
    main = main.replace("@CONTACT@", contact_inline()).replace("@MAIL@", mail())
    for k in PAGES:
        main = main.replace(f"@{k}@", link(k, here))
        top = top.replace(f"@{k}@", link(k, here))
    main = re.sub(r"@post:([a-z0-9-]+)@", lambda m: rel("blog/" + m.group(1), here), main)
    og = img_url(og_image or "arch", 1200, 630)
    ld = schema or {"@context": "https://schema.org", "@type": "ProfessionalService", "name": "Copacetic Marketing",
                    "url": DOMAIN + "/", "areaServed": "US",
                    "founder": {"@type": "Person", "name": "Fritts Causby", "url": FC},
                    "description": "Press releases, media outreach, ghostwriting and marketing content."}
    svc_links = f'<a href="{link("services", here)}">All services</a>' + "".join(f'<a href="{link(k, here)}">{lab}</a>' for k, lab in MENU if k)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Copacetic Marketing">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{og}">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="canonical" href="{canonical}">
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Ccircle cx='32' cy='32' r='32' fill='%232E3742'/%3E%3Ctext x='50%25' y='57%25' text-anchor='middle' dominant-baseline='middle' font-family='Georgia' font-size='38' fill='%23F3EEE7'%3EC%3C/text%3E%3C/svg%3E">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{up}assets/style.css?v={CSS_V}">
  <script type="application/ld+json">{json.dumps(ld)}</script>
</head>
<body>
<header>
  <div class="header-inner">
    <a href="{link('home', here)}" class="logo"><span class="logo-mark" aria-hidden="true">C</span><span class="logo-words"><span class="logo-text">Copacetic <span>Marketing</span></span><span class="logo-def"><em>co&middot;pa&middot;cet&middot;ic</em> (adj.): excellent; in fine order</span></span></a>
    <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="site-nav" onclick="var n=document.getElementById('site-nav');var o=n.classList.toggle('open');this.setAttribute('aria-expanded',o)">Menu</button>
    <nav id="site-nav" aria-label="Main">{nav}<a href="{mail()}" class="nav-subscribe">Contact</a></nav>
  </div>
</header>
{top}
<div class="content-with-sidebar">
  <main class="site-main page-body article-body" id="main">
{main}
  </main>
  {sidebar(key, here)}
</div>
<footer>
  <div class="footer-inner">
    <div class="footer-top">
      <div class="footer-brand">
        <span class="logo-text">Copacetic <span>Marketing</span></span>
        <p>Press releases, ghostwriting and marketing content for law firms, real estate professionals and businesses nationwide.</p>
      </div>
      <div class="footer-col">
        <h4>Services</h4>
        {svc_links}
        <a href="{link('industries', here)}">Industries</a>
        <a href="{link('blog', here)}">Blog</a>
        <a href="{link('about', here)}">About</a>
      </div>
      <div class="footer-col">
        <h4>Connect</h4>
        <a href="{mail()}">Contact</a>
        <a href="{FC}">frittscausby.com</a><span class="desc">Freelance writing portfolio and published clips</span>
        <a href="https://thepinnacle.ink">The Pinnacle</a><span class="desc">Luxury real estate, financial markets and the aspirational lifestyle</span>
      </div>
    </div>
    <div class="footer-bottom">
      <span>&copy; 2026 Copacetic Marketing. Fritts Causby, writer.</span>
      <a href="{link('home', here)}">copacetic.marketing</a>
    </div>
  </div>
</footer>
</body>
</html>
"""


HOME_SVC = [
    ("press", "press", "Press releases and media outreach", "An event, a new hire, a service expansion or a fundraiser is an opportunity to seek coverage with a professionally written press release. The service includes a targeted list of local and trade reporters, personal pitch emails and a report on the coverage that follows. The client approves one document and I handle the list, pitches and follow-up."),
    ("ghost", "q20", "Ghostwriting for attorneys", "Blog posts, client alerts and bylined articles with insights and guidance from the perspective of the attorney, written from a short interview and reviewed by the attorney before publishing. Each piece is customized to the voice of the firm and the attorney. The content draws from my experience writing legal content since 2021."),
    ("ghost", "q10", "Ghostwriting for real estate professionals", "Market updates, newsletters, agent bios, LinkedIn posts and area guides built on the insights and knowledge of the agent, leveraging the experience of a writer who has worked in real estate since 2005 in sales, marketing, administration and copywriting. Clients and prospects hear from the agent on a regular schedule, even in the busiest months."),
    ("c2c", "c2c", "Conference to Content", "The effort and planning that go into a conference are significant, so why should the content evaporate when the conference ends? I attend the client event, panel or conference in person, record the sessions for accuracy and write the articles, posts and summary pieces. A single conference can supply months of articles and posts."),
    (None, "arch", "Architectural property narratives and listing descriptions", "Architectural narratives, listing descriptions, property stories and community lifestyle pages for neighborhoods and developments. The story behind a home is often what earns coverage from media outlets, and a written narrative that honors the architecture keeps the agent&rsquo;s name tied to the property long after it sells."),
    (None, "news", "Newsletter distribution and management", "A newsletter is a cost-effective means of connecting with customers. This service covers the writing, formatting, scheduling and distribution of newsletters on a regular cadence, with list management and basic reporting, on the platform the client prefers, including Mailchimp, Constant Contact and Beehiiv."),
    (None, "web", "Website creation and management", "Focused, straightforward websites for small businesses and professionals: a few clearly written pages that load quickly, explain the business and make contact easy. The writing is included, and each site can carry a news section that collects the press releases and articles produced together."),
]


def home_services(here):
    out = []
    for k, img, title, text in HOME_SVC:
        pid, name, user, alt = IMG[img]
        h = f'<a href="{link(k, here)}">{title}</a>' if k else title
        more = f'<p><a class="more" href="{link(k, here)}">Learn more</a></p>' if k else ""
        out.append(f'''<div class="svc-media">
  <figure><img src="{img_url(img, 900, 600)}" alt="{alt}" width="900" height="600" loading="lazy"><figcaption>Photo by <a href="https://unsplash.com/@{user}?{UTM}">{name}</a> on <a href="https://unsplash.com/?{UTM}">Unsplash</a></figcaption></figure>
  <div><h3>{h}</h3><p>{text}</p>{more}</div>
</div>''')
    return '<div class="svc-media-list">' + "".join(out) + "</div>"


def clip(mark, pub, meta, url):
    return (f'<a class="clip" href="{url}"><span class="mark">{mark}</span>'
            f'<span><span class="pub">{pub}</span><br><span class="meta">{meta}</span></span>'
            f'<span class="go">Read the article &rarr;</span></a>')


# ---------------------------------------------------------------- HOME
HOME_TOP = f'''<div class="mini-hero">
  <div class="mini-hero-inner">
    <p>Press releases, sponsored content, newsletters and ghostwritten articles for law firms, real estate professionals and businesses nationwide.</p>
    <a href="@services@" class="mini-hero-link">View services &rarr;</a>
  </div>
</div>'''

HOME = '''
<div class="intro">
  <h1>Content writing and ghostwriting for <em>busy professionals.</em></h1>
  <p class="lede">Marketing is the engine that grows a business and content is the fuel. With content development and distribution services, Copacetic Marketing drives business forward.</p>
  <div class="actions"><a class="btn-primary" href="@MAIL@">Contact &rarr;</a><a class="btn-ghost" href="@services@">View services</a></div>
</div>

<h2>Services</h2>
@HOMESVC@
<p><a class="more" href="@services@">All services</a></p>

<h2>About Copacetic Marketing</h2>
<p>My name is Fritts Causby, and I am the writer behind Copacetic Marketing. Copacetic Marketing is a one-writer firm today, and I bring in designers, writers and editors when it is necessary.</p>
<p>Since 2008, I have written press releases and marketing copy for <a href="https://www.bhhscalifornia.com">Berkshire Hathaway HomeServices California Properties</a>, supporting thousands of agents across Southern and Central California. I have also worked as a ghostwriter for <a href="https://www.wardandsmith.com">Ward and Smith, P.A.</a>, a regional law firm with offices across the Carolinas, since 2021.</p>
<p>My work has appeared in <a href="https://www.inman.com">Inman Real Estate News</a> and <a href="https://www.wrightsvillebeachmagazine.com">Wrightsville Beach Magazine</a>, and my pitches have led to coverage in <a href="https://robbreport.com">Robb Report</a> and <a href="https://www.mansionglobal.com">Mansion Global</a>. Press releases I have created for Berkshire Hathaway HomeServices California Properties have been distributed without my byline to numerous local and regional publications. I also wrote sponsored content for the Wilmington Business Journal for eight years, and I am a freelancer for Wrightsville Beach Magazine.</p>
<p><a class="more" href="@about@">More about Fritts</a> &nbsp;&nbsp; <a class="more" href="''' + FC + '''/testimonials">What clients say</a></p>

<h2>From the blog</h2>
@BLOGCARDS@
<p><a class="more" href="@blog@">All articles</a></p>

<h2>How it works</h2>
<p>Each engagement begins with a brief call or an exchange of emails, whichever suits the client's schedule. A clearly written proposal defines the scope and the price of the project. I prepare a draft for review and revisions, and the finished work is published or distributed. Most projects take 2 to 4 business days, depending on complexity. Rush delivery within 24 to 48 hours is available for an additional fee.</p>

<div class="newsletter-band">
  <h2>Have news worth sharing?</h2>
  <p>To discuss a project, get in touch at @CONTACT@.</p>
  <a href="@MAIL@" class="btn-primary">Contact &rarr;</a>
</div>
'''

# ---------------------------------------------------------------- SERVICES
SERVICES_TOP = header_block("Services", "Services", "The services presented here are not a complete list. There is no such thing as a one-size-fits-all solution, so the process is fluid and the work is adapted to the needs of each client.")
SERVICES = figure("arch", 1600, 700, True) + '''
<div class="svc-list">
  <div class="svc" id="press-releases"><div><h3>Press releases and media outreach</h3></div><div>
    <p>An event, a new hire, a service expansion or a fundraiser is an opportunity to seek coverage with a professionally written press release. The service includes a targeted list of local and trade reporters, personal pitch emails and a report on the coverage that follows. The client approves one document and I handle the list, pitches and follow-up.</p>
    <p><a class="more" href="@press@">Press release services</a></p></div></div>

  <div class="svc" id="attorneys"><div><h3>Ghostwriting for attorneys</h3></div><div>
    <p>Blog posts, client alerts and bylined articles with insights and guidance from the perspective of the attorney, written from a short interview and reviewed by the attorney before publishing. Each piece is customized to the voice of the firm and the attorney. The content draws from my experience writing legal content since 2021. The attorney spends about 30 minutes in conversation and reviews the article before it is published.</p>
    <p><a class="more" href="@ghost@">Ghostwriting services</a> &nbsp;&nbsp; <a class="more" href="@ind-law@">For law firms</a></p></div></div>

  <div class="svc" id="real-estate-ghostwriting"><div><h3>Ghostwriting for real estate professionals</h3></div><div>
    <p>Market updates, newsletters, agent bios, LinkedIn posts and area guides built on the insights and knowledge of the agent, leveraging the experience of a writer who has worked in real estate since 2005 in sales, marketing, administration and copywriting. Clients and prospects hear from the agent on a regular schedule, even in the busiest months.</p>
    <p><a class="more" href="@ghost@">Ghostwriting services</a> &nbsp;&nbsp; <a class="more" href="@ind-realestate@">For real estate</a></p></div></div>

  <div class="svc" id="linkedin"><div><h3>Executive and LinkedIn ghostwriting</h3></div><div>
    <p>Ongoing posts and articles for owners and subject matter experts who want a steady presence but do not have the time to write every post. Nothing is posted without the approval of the client. An optional add-on covers posting and engagement support, with each reply drafted for the approval of the client before posting.</p></div></div>

  <div class="svc" id="newsletters"><div><h3>Newsletter distribution and management</h3></div><div>
    <p>A newsletter is a cost-effective means of connecting with customers. This service covers the writing, formatting, scheduling and distribution of newsletters on a regular cadence, with list management and basic reporting, on the platform the client prefers, including Mailchimp, Constant Contact and Beehiiv. The client approves each issue, and the writing, formatting and sending are handled.</p></div></div>

  <div class="svc" id="conference-to-content"><div><h3>Conference to Content</h3></div><div>
    <p>The effort and planning that go into a conference are significant, so why should the content evaporate when the conference ends? I attend the client event, panel or conference in person, record the sessions for accuracy and write the articles, posts and summary pieces. This is evergreen content that keeps working long after the event is over. A single conference can supply months of articles and posts, and every name, figure and quote is checked against the recording before publication.</p>
    <p><a class="more" href="@c2c@">Conference to Content</a></p></div></div>

  <div class="svc" id="real-estate"><div><h3>Architectural property narratives and listing descriptions</h3></div><div>
    <p>Architectural narratives, listing descriptions, property stories and community lifestyle pages for neighborhoods and developments. Many houses have a resort-like backyard and ocean views. The story behind a home is often what earns coverage from media outlets. A home with a story becomes a resume builder for the agent, and a written narrative that honors the architecture keeps the agent's name tied to the property long after it sells. My article for Inman Real Estate News explains the approach:</p>
    ''' + clip("I", "Inman Real Estate News", "June 5, 2026 &middot; Luxury listing marketing and storytelling &middot; By Fritts Causby", "https://www.inman.com/2026/06/05/luxury-listing-marketing-secrets-storytelling/") + '''
    ''' + clip("P", "The Pinnacle", "Ray Kappe House: An $11.5M Architectural Landmark", PIN + "/landmark-ray-kappe-house-up-for-sale.html") + '''
    ''' + clip("P", "The Pinnacle", "Villa Maggio: Frank Sinatra&rsquo;s Last Intact Estate", PIN + "/villa-maggio-frank-sinatra-last-intact-estate.html") + '''
    ''' + clip("P", "The Pinnacle", "Timeless John Lautner-Designed Home in Long Beach", PIN + "/timeless-john-lautner-designed-home-in-long-beach.html") + '''
  </div></div>

  <div class="svc" id="property-websites"><div><h3>Unique property websites</h3></div><div>
    <p>A dedicated website for each listing can set an agent apart. It shows sellers the effort behind the marketing and can build positive word of mouth. Each site includes the brokerage, license and fair housing information that advertising rules require. Sellers immediately recognize the value, time and effort involved with building a website that is specifically for their home.</p></div></div>

  <div class="svc" id="video-scripts"><div><h3>Video scripts</h3></div><div>
    <p>Scripts for property tours, neighborhood features, brand videos and social clips, tailored to the platform and length the client chooses. A finished script shortens the shoot and keeps the message on point.</p></div></div>

  <div class="svc" id="sponsored-content"><div><h3>Sponsored content</h3></div><div>
    <p>Sponsored articles that describe the value and services of a business and read like journalism, written to the requirements of the publication where the client has purchased space. A business that has paid for the space deserves an article that readers will finish.</p></div></div>

  <div class="svc" id="reputation"><div><h3>Reputation management</h3></div><div>
    <p>Calm, clear messaging when something goes wrong, and ongoing attention to how a business is described online. A prepared statement is ready before the questions arrive.</p></div></div>

  <div class="svc" id="websites"><div><h3>Website creation and management</h3></div><div>
    <p>I design and build focused, straightforward websites for small businesses and professionals: a few clearly written pages that load quickly, explain the business and make contact easy. I also work with WordPress and Wix where a client already uses one of them. Three current examples are <a href="''' + FC + '''">frittscausby.com</a>, <a href="https://thepinnacle.ink">thepinnacle.ink</a> and this site. The writing is included, and each site can carry a news section that collects the press releases and articles produced together.</p></div></div>
</div>
''' + cta("Not sure which service fits?", "Describe the goal, and I will recommend an approach.")

# ---------------------------------------------------------------- PRESS
PRESS_TOP = header_block("Press Releases", "Press Release Services", "A release that is ready to run, and a genuine effort to place it in the right publication.")
PRESS = '''
<p class="lead-in">Many press release services end at the wire. The release is posted to a distribution site, and the process stops there. Reporters are busy, and an announcement from an unfamiliar source rarely gets a second look. My approach is to write a release that an editor or reporter would be proud to copy and paste, then follow up with courtesy and professionalism.</p>

<h2>What is included</h2>
<div class="svc-list">
  <div class="svc"><div><h3>The release</h3></div><p>A clear, accurate release in standard news format and AP style, with a headline, a lead that gets attention, quotes that sound like a person, and credible details that are easy to verify. Research is pulled from online sources, an interview, bullet points in an email&mdash;whatever method is preferred by the client. The client supplies the facts once, in whatever form is easiest, and receives a release that is ready to send.</p></div>
  <div class="svc"><div><h3>A targeted media list</h3></div><p>Local and trade reporters, editors and outlets that cover the relevant subject, hand-selected and personally vetted instead of pulled from a bulk database. The spreadsheet belongs to the client, and the list remains useful for every future announcement.</p></div>
  <div class="svc"><div><h3>Personal pitches</h3></div><p>Short, specific emails to the reporters who cover the industry segment, sent from a real address and followed up on by a real person. The client does not have to chase reporters.</p></div>
  <div class="svc"><div><h3>A coverage report</h3></div><p>A summary of the publications and individuals who received the release, who responded and where it appeared, so the results are clear. The client sees exactly who was contacted and the subsequent results, whether or not the release was published.</p></div>
  <div class="svc"><div><h3>Wire distribution (optional)</h3></div><p>Available as an add-on for announcements that benefit from broad syndication.</p></div>
</div>

<h2>How it works</h2>
<ol class="steps">
  <li>A call of about 15 minutes covers the news, the audience and the intended outcome.</li>
  <li>I write the release and send it for review.</li>
  <li>Once the release is approved, I build the media list and send the pitches.</li>
  <li>I follow up and deliver the report.</li>
</ol>
<p class="note">Turnaround is usually 2 to 4 business days, with up to four edits included.</p>

<h2>Why a press release?</h2>
<p>A law firm announcing a hire, a win or a new practice area may benefit from a press release. Real estate agents and brokerages use press releases to mark a record sale, a milestone or a new listing. Ideas for specific fields are collected on the <a href="@industries@">Industries</a> pages.</p>
<p>Charity fundraisers can be particularly effective, as many editors like to publish feel-good stories. Product launches, new locations, charity sponsorships and client appreciation events are also valid reasons for creating a press release. The service can benefit any organization with news and little time.</p>
<p class="sample">For an example of charity coverage, see the <a href="''' + PIN + '''/love-is-bald-charity-spotlight-supporting-cancer-warriors-in-north-carolina.html">Love is Bald charity spotlight</a> on The Pinnacle and <a href="''' + FC + '''/first-tee-charity-spotlight">First Tee Brings Character to the Fore</a> on frittscausby.com.</p>
<p>Press releases are a valuable form of engagement, and in many cases a published release functions as an advertisement that reaches a more informed audience than a paid ad does. A press release also typically costs less than a single business-card-size print ad in a local or trade publication, where rates often start near $100 per insertion, and the release says far more about the business.</p>

<h2>Pricing</h2>
<div class="price-grid">
  <div class="price-card"><h3>Release only</h3><div class="price">Starting at $300</div><p>A finished release, ready to send.</p></div>
  <div class="price-card"><h3>Release plus outreach</h3><div class="price">Starting at $900</div><p>Release, targeted media list, personal pitches and a coverage report.</p></div>
  <div class="price-card"><h3>Monthly plan</h3><div class="price">Per-release pricing</div><p>For regular announcements, with a discount and a three-month minimum.</p></div>
</div>

<h2>Questions</h2>
<div class="faq">
  <details><summary>Is coverage guaranteed?</summary><p>No. Editors decide what runs, and coverage cannot be promised. What is guaranteed is a professional release, targeted pitching and a report that covers what happened. A well-written release placed in front of the right reporters gives the news a better chance.</p></details>
  <details><summary>Is wire distribution available?</summary><p>Yes, as an add-on.</p></details>
  <details><summary>How soon can work begin?</summary><p>Work usually begins within 2 to 4 business days of an agreed scope. Rush delivery within 24 to 48 hours is available for an additional fee.</p></details>
</div>
''' + cta("To get started", "Share the news, the audience and the timing, and I will reply with a scope and a price.")

# ---------------------------------------------------------------- GHOSTWRITING
GHOST_TOP = header_block("Ghostwriting", "Ghostwriting Services", "Articles, posts and newsletters built from a short conversation. The client supplies the expertise, and I supply the writing.")
GHOST = '''
<p class="lead-in">Professionals know their fields better than anyone writing about them, yet few have the time to turn that knowledge into a steady flow of content. Working with a ghostwriter reduces the time it takes to produce steady, publishable content. A short interview establishes the ideas, I draft from the perspective of the client, and nothing is published under the client's name until it has been reviewed and approved. The information can be shared in the form that is the best fit for the needs of the client, whether it is a transcript from a notes app, a phone call or a link to an existing website. I work around the client's schedule and make the process as easy as possible.</p>

<div class="svc-list">
  <div class="svc" id="attorneys"><div><h3>For attorneys</h3></div><div>
    <p>Blog posts, client alerts, bylined articles and practice area pages from the perspective of the attorney, with answers to the questions clients ask. I have written legal content for Ward and Smith, P.A. since 2021. I also attend firm seminars and conferences in person and turn the sessions into articles. Professional rules vary by state, so the attorney should confirm that the final piece meets the applicable obligations. Anyone can ask a chatbot for complicated legal jargon that will put readers to sleep. I write articles that are accurate, engaging and conversational.</p>
    <p><a class="more" href="@ind-law@">Ghostwriting and press releases for law firms</a></p>
    <p><a class="more" href="@post:does-a-legal-writer-need-a-law-degree@">Related: Does a Legal Writer Need a Law Degree?</a></p></div></div>

  <div class="svc" id="real-estate"><div><h3>For real estate professionals</h3></div><div>
    <p>Market updates, newsletters, listing stories, agent bios and local guides that sound like a person and not a template. Writing listings and PR for agents since 2008 has taught me what buyers respond to and what an effective bio needs to communicate.</p>
    <p>A sample of my real estate writing published in Wrightsville Beach Magazine is available on <a href="''' + FC + '''/coastal-home">frittscausby.com</a>.</p>
    <p><a class="more" href="@ind-realestate@">Writing for real estate agents, teams and brokerages</a></p>
    <p><a class="more" href="@post:why-top-agents-hire-a-real-estate-writer@">Related: Why Top Agents Hire a Real Estate Writer</a></p>
    <p><a class="more" href="''' + PIN + '''/villa-maggio-frank-sinatra-last-intact-estate.html">On The Pinnacle: Villa Maggio, Frank Sinatra&rsquo;s Last Intact Estate</a></p></div></div>

  <div class="svc" id="executives"><div><h3>For executives and business owners</h3></div><div>
    <p>LinkedIn posts, articles and short thought leadership pieces for business owners and subject matter experts with expertise to share and full calendars.</p>
    <p><a class="more" href="@post:the-role-of-a-linkedin-ghostwriter@">Related: The Role of a LinkedIn Ghostwriter</a></p></div></div>
</div>

<h2>How it works</h2>
<ol class="steps">
  <li>I research the client and the business before the call, so the 20 to 30 minute conversation is informed and flows naturally instead of following a list of questions. The call is recorded with permission.</li>
  <li>I research additional sources, create a draft from the perspective of the client and send it for review.</li>
  <li>The client reviews and edits, and the piece is finalized with up to four edits.</li>
  <li>I deliver a version ready to publish, with a headline and, if desired, a search-friendly summary.</li>
</ol>
<p class="note">Turnaround is typically one to two weeks from interview to final.</p>

<h2>Pricing</h2>
<div class="price-grid">
  <div class="price-card"><h3>Single article</h3><div class="price">Starting at $350</div></div>
  <div class="price-card"><h3>Monthly package</h3><div class="price">Starting at $900</div></div>
</div>

<h2>Questions</h2>
<div class="faq">
  <details><summary>Will it sound like me?</summary><p>That is the purpose of the interview. I write from the conversation, using specific words and examples, then refine the phrasing with up to four edits.</p></details>
  <details><summary>Can a ghostwriter be used in a given profession?</summary><p>In most cases, yes, with review and appropriate credit, but the rules vary. This is not legal advice, and professional rules should be checked.</p></details>
</div>
''' + cta("To get started", "Tell me about the expertise you want to share, and I will suggest a schedule and a format.")

# ---------------------------------------------------------------- CONFERENCE TO CONTENT
C2C_TOP = header_block("Conference to Content", "Conference to Content", "Turn the effort behind a conference, panel or client event into content that keeps working for months.")
C2C = figure("c2c", 1600, 700, True) + '''
<p class="lead-in">A conference is expensive to produce and takes months to plan. When the event ends, the insights and conversations that justified the investment usually leave the room with the audience. Conference to Content is a service that captures the substance of an event in real time and converts it into articles, posts and summary pieces the firm can use for the next several months.</p>

<h2>How it works</h2>
<ol class="steps">
  <li>I attend the event in person. Panels, keynotes, breakout sessions and informal remarks are recorded with the permission of each speaker, and I take notes alongside the recording so that names, figures and quotes are captured accurately.</li>
  <li>I draft articles, LinkedIn posts, summary emails and recap pages from the recordings, each piece written in the voice of the attributed presenter and reviewed before publication.</li>
  <li>I deliver the finished content on an agreed schedule, which is usually weekly over the four to eight weeks following the event.</li>
</ol>

<div class="svc-list">
  <div class="svc"><div><h3>What the client receives</h3></div><p>A single two-day conference typically supports a package of four to eight articles, a dozen or more social posts and a summary email for attendees and prospects. Every name, figure and quote is checked against the recording before publication, so an article that pulls a line from a panelist can be trusted to match what the panelist actually said.</p></div>
  <div class="svc"><div><h3>Why it works</h3></div><p>Content produced from a conference carries two advantages that content produced from a brief does not. The ideas are already vetted by people the audience respects, and the writing has the specificity that only comes from the room. A reader who missed the event sees what mattered, and a reader who attended sees the firm doing something useful with the material.</p></div>
  <div class="svc"><div><h3>Who it suits</h3></div><p>Law firms with client-facing seminars, legal CLEs and bar conferences. Real estate brokerages with annual company meetings, agent training weeks and industry events. Business associations and chambers of commerce with speaker series and member conferences. Any organization whose calendar includes events worth attending.</p></div>
  <div class="svc"><div><h3>Experience</h3></div><p>I have attended legal conferences and client seminars for a regional law firm with offices across the Carolinas since 2021, and produced articles, posts and summary pieces from recordings of panels, keynotes and roundtables. Travel is handled at cost and discussed in advance.</p></div>
  <div class="svc"><div><h3>Pricing</h3></div><p>Scope depends on the length of the event, the number of pieces and the publication schedule, so each event is quoted individually.</p></div>
</div>
<p><a class="more" href="@post:how-to-repurpose-content-from-seminars-and-conferences@">Related: How to Repurpose Content from Seminars and Conferences</a></p>
''' + cta("To discuss an upcoming event", "Share the dates, the location and the sessions, and I will put together a quote.")

# ---------------------------------------------------------------- ABOUT
ABOUT_TOP = header_block("About", "About Fritts Causby", "A writer and PR consultant with a background in luxury real estate, legal content and finance.")
ABOUT = '''
<p>I have written for a living since 2008, and real estate has been my focus for most of that time. As a contractor for Berkshire Hathaway HomeServices California Properties, I have been fortunate to support agents nationwide. Most of my work has been remote, and I have worked with clients across the country. The pitches I have created for the company have led to coverage in Robb Report and Mansion Global. That work taught me how to make a property or a person memorable in a few hundred words and how to write for very busy readers.</p>
<p>Learning the nuances of different markets has its challenges. I develop area-specific content through research and the expertise of my clients, and my role has often been to simply refine what they already know.</p>
<p>Over the years, I added services. I developed sponsored content for the Wilmington Business Journal for eight years, and I have produced legal content for Ward and Smith, P.A., a regional law firm with offices across the Carolinas, since 2021. My work has also been published in Inman Real Estate News.</p>
<p>As a writer for Wrightsville Beach Magazine, I have covered a wide array of subject matter, including lifestyle, art, culture, travel and, of course, real estate. A small sample of that work is available at <a href="''' + FC + '''/coastal-home">frittscausby.com</a>.</p>
<p>Personal interest led me to build <a href="https://thepinnacle.ink">The Pinnacle</a>, an online publication covering luxury real estate, financial markets and the aspirational lifestyle.</p>
<p><a href="''' + FC + '''/clients">Other clients</a> have included Coldwell Banker Sea Coast Advantage, Pacific Sotheby&rsquo;s International Realty, Piatt Sotheby&rsquo;s International Realty, Market Consulting Mortgage and hundreds of individual agents nationwide.</p>
<p>I work with each client directly, from the first call to the final draft. Over time, I hope the firm will create opportunities for new writers, graphic designers and young professionals.</p>
<p>I hold a bachelor&rsquo;s degree in English from North Carolina State University and a master&rsquo;s degree in Human Resources and Organization Development from National University. I live on the North Carolina coast, and outside of work I surf, play golf and travel when I can.</p>
<p class="signoff">Thank you for reading, Fritts</p>

<p class="eyebrow" style="margin-top:2.5rem">Published and covered in</p>
<div class="creds">
  <a href="https://www.inman.com/2026/06/05/luxury-listing-marketing-secrets-storytelling/">Inman Real Estate News</a>
  <a href="https://robbreport.com">Robb Report</a>
  <a href="https://www.mansionglobal.com">Mansion Global</a>
  <a href="https://www.wrightsvillebeachmagazine.com">Wrightsville Beach Magazine</a>
  <span>Wilmington Business Journal</span>
</div>

<h2>A note on samples</h2>
<p>Most of the content I have produced was published under the names of my clients. I do not post or share work that I was paid to create as a ghostwriter, out of loyalty to them and to protect their search presence and brand reputation. This has always been important to me from an ethical standpoint, and the same discretion applies to new clients. To get a feel for the writing, see the samples on this site, <a href="''' + FC + '''">frittscausby.com</a> or <a href="https://thepinnacle.ink">thepinnacle.ink</a>.</p>
''' + cta("To discuss a project", "A short call or an email is the easiest way to start.")

SPECS = [
    ("services", "PR, Ghostwriting and Content Services | Copacetic Marketing",
     "Press releases, media outreach, ghostwriting for attorneys and agents, conference recaps, newsletters, websites and more.", SERVICES_TOP, SERVICES, "arch"),
    ("press", "Press Release Writing and Media Outreach | Copacetic Marketing",
     "Press release writing, targeted media outreach and a coverage report for small businesses and professionals nationwide. Clear scopes, clear prices.", PRESS_TOP, PRESS, "q15"),
    ("ghost", "Ghostwriting for Attorneys, Agents and Executives | Copacetic Marketing",
     "Articles, blog posts and LinkedIn content written from the perspective of the client, built from a short interview. Ghostwriting for attorneys, real estate agents and business owners nationwide.", GHOST_TOP, GHOST, "q21"),
    ("about", "About Fritts Causby | Copacetic Marketing",
     "Fritts Causby is a writer and PR consultant with a background in luxury real estate, legal content and finance, working with clients across the country.", ABOUT_TOP, ABOUT, "q20"),
    ("c2c", "Conference to Content: Articles and Posts from Your Events | Copacetic Marketing",
     "Attend, record and transform conferences, panels and client events into articles, posts and summaries that keep working long after the event ends.", C2C_TOP, C2C, "c2c"),
]

# ---------------------------------------------------------------- POSTS + sample links
POSTS = json.load(open("posts.json"))
_LAND = {d["key"]: d for d in INDUSTRIES}
for np_ in NEW_POSTS:
    body = "".join(f"<p>{t}</p>" for t in np_["paras"])
    body += f'<p><a class="more" href="@{np_["land"]}@">{_LAND[np_["land"]]["h1"]}</a></p>'
    if np_.get("extra"):
        body += f'<p><a class="more" href="@{np_["extra"][0]}@">{np_["extra"][1]}</a></p>'
    POSTS.append({"slug": np_["slug"], "title": np_["title"], "key": np_["key"], "html": body, "excerpt": np_["paras"][0]})
POST_TITLES = {p["slug"]: p["title"] for p in POSTS}
SAMPLES = {
    "why-top-agents-hire-a-real-estate-writer": (6, f'For examples of narratives about architecturally significant homes, see the <a href="{PIN}/landmark-ray-kappe-house-up-for-sale.html">Ray Kappe House</a> and <a href="{PIN}/villa-maggio-frank-sinatra-last-intact-estate.html">Villa Maggio, the last intact estate of Frank Sinatra</a> on The Pinnacle, and <a href="{FC}/coastal-home">a coastal home feature</a> on frittscausby.com.'),
    "real-estate-articles-in-marketing": (4, f'For a sample of a home feature written for a local magazine, see <a href="{FC}/coastal-home">Every Detail Tells a Story</a> on frittscausby.com. For an article that compares real estate with other investments, see <a href="{PIN}/stocks-vs-real-estate.html">Stocks vs. Real Estate</a> on The Pinnacle.'),
    "outsourcing-professional-writing": (6, f'For a sample of a business feature written for a general audience, see <a href="{FC}/ncinoheadquartersarticle">Bringing it all Together</a>, an article on the headquarters of nCino published in Wrightsville Beach Magazine.'),
    "copywriter-in-house-writer-or-ai": (3, f'Samples of published work are available at <a href="{FC}">frittscausby.com</a>.'),
    "charitable-initiatives-real-estate-development": (6, f'For examples, see the <a href="{PIN}/love-is-bald-charity-spotlight-supporting-cancer-warriors-in-north-carolina.html">Love is Bald charity spotlight</a> on The Pinnacle and <a href="{FC}/first-tee-charity-spotlight">First Tee Brings Character to the Fore</a> on frittscausby.com.'),
}


def add_sample(p):
    if p["slug"] not in SAMPLES:
        return p["html"]
    after, text = SAMPLES[p["slug"]]
    blocks = re.findall(r"<(?:p|h2|h3|ul|ol)>.*?</(?:p|h2|h3|ul|ol)>", p["html"], flags=re.S)
    target = [b for b in blocks if b.startswith("<p>")][after]
    return p["html"].replace(target, target + f'\n<p class="sample">{text}</p>', 1)


def read_time(h):
    return max(2, round(len(re.sub("<[^>]+>", " ", h).split()) / 230))


def cards(posts, here):
    out = []
    for p in posts:
        ex = p["excerpt"][:165].rsplit(" ", 1)[0].rstrip(".,:;")
        out.append(f'''<a href="{rel('blog/' + p['slug'], here)}" class="article-card">
        <img class="article-card-img" src="{img_url(p['key'], 800, 450)}" alt="{IMG[p['key']][3]}" width="600" height="338" loading="lazy">
        <div class="article-card-tag">Blog &nbsp;&middot;&nbsp; {read_time(p['html'])} min read</div>
        <h3>{p['title']}</h3>
        <p class="article-card-excerpt">{ex}&hellip;</p>
      </a>''')
    return '<div class="article-grid">' + "".join(out) + "</div>"


def related(posts, here):
    return ('<div class="related-section"><h3>Keep Reading</h3><div class="related-grid">' + "".join(
        f'<a href="{rel("blog/" + q["slug"], here)}" class="related-card"><img src="{img_url(q["key"], 600, 400)}" alt="{IMG[q["key"]][3]}" width="400" height="267" loading="lazy"><h4>{q["title"]}</h4></a>'
        for q in posts) + "</div></div>")


# ---------------------------------------------------------------- WRITE
if os.path.exists(OUT):
    shutil.rmtree(OUT)
os.makedirs(f"{OUT}/assets")
shutil.copy("assets/style.css", f"{OUT}/assets/style.css")


def write(path, text):
    d = f"{OUT}/{path}" if path else OUT
    os.makedirs(d, exist_ok=True)
    with open(f"{d}/index.html", "w") as f:
        f.write(text)


write("", page("home", "Content Writing and Ghostwriting | Copacetic Marketing",
               "Press release writing, media outreach, ghostwriting and marketing content for law firms, real estate professionals and businesses nationwide.",
               HOME_TOP, HOME.replace("@BLOGCARDS@", cards(POSTS[:4], "")).replace("@HOMESVC@", home_services("")), og_image="arch"))
for key, title, desc, top, main, og in SPECS:
    write(PAGES[key], page(key, title, desc, top, main, og_image=og))

IND_TOP = header_block("Industries", "Industries", "Every field has its own news, its own audiences and its own rules. These pages cover the events that tend to earn coverage, the services that fit and the rules that apply.")
IND = '<div class="svc-list">' + "".join(
    f'<a class="svc" href="@{d["key"]}@"><div><h3>{d["label"]}</h3></div><p>{d["opening"]}</p></a>' for d in INDUSTRIES) + "</div>" + \
    cta("Not sure where a project fits?", "Describe the news or the goal, and I will recommend an approach.")
write("industries", page("industries", "Industries | Copacetic Marketing",
                         "Press releases, ghostwriting and content for medical practices, builders, nonprofits, financial advisors, associations, resorts, retirement communities, real estate and law firms.",
                         IND_TOP, IND, og_image="press"))


def industry_main(d):
    out = [figure(d["img"], 1600, 700, True), f'<p class="lead-in">{d["opening"]}</p>', "<h2>News-worthy events</h2>"]
    if d["events"]:
        out.append("<ul>" + "".join(f"<li>{e}</li>" for e in d["events"]) + "</ul>")
    out += [f"<p>{p}</p>" for p in d["events_p"]]
    out.append("<h2>What is included</h2>")
    out += [f"<p>{p}</p>" for p in d["included"]]
    out.append(f'<p><a class="more" href="@{d["service"][0]}@">{d["service"][1]}</a></p>')
    out += ["<h2>Rules that apply</h2>", f'<p class="note">{d["rules"]}</p>']
    if d["samples"]:
        out.append("<h2>Samples</h2>")
        out += [f'<p class="sample">{t}</p>' for t in d["samples"]]
    if d["related"]:
        out.append(f'<p><a class="more" href="@post:{d["related"]}@">Related: {POST_TITLES[d["related"]]}</a></p>')
    out.append(cta("To discuss a project", "Share the news, the audience and the timing, and I will reply with a scope and a price."))
    return "\n".join(out)


for d in INDUSTRIES:
    write(PAGES[d["key"]], page(d["key"], d["title"], d["desc"],
                                header_block("Industries", d["h1"], ""), industry_main(d), og_image=d["img"]))

BLOG_TOP = header_block("Blog", "Notes on writing, PR and content", "Practical articles on press releases, ghostwriting, conference content and real estate marketing.")
BLOG = '@CARDS@' + '''
<h2>More reading</h2>
<p>Published clips and samples are collected at <a href="''' + FC + '''">frittscausby.com</a>, a freelance writing portfolio. Luxury real estate, financial markets and the aspirational lifestyle are covered at <a href="https://thepinnacle.ink">The Pinnacle</a>.</p>
'''
write("blog", page("blog", "Blog | Copacetic Marketing",
                   "Articles on press releases, ghostwriting, conference content and real estate marketing from Copacetic Marketing.",
                   BLOG_TOP, BLOG.replace("@CARDS@", cards(POSTS, "blog")), og_image="q13"))

for i, p in enumerate(POSTS):
    path = "blog/" + p["slug"]
    desc = html.escape(p["excerpt"][:155].rsplit(" ", 1)[0], quote=True)
    top = (f'<div class="article-header"><div class="article-header-inner"><div class="article-tag">Blog</div>'
           f'<h1>{p["title"]}</h1><div class="article-byline"><strong>Fritts Causby</strong> &nbsp;&middot;&nbsp; '
           f'Copacetic Marketing &nbsp;&middot;&nbsp; {read_time(p["html"])} min read</div></div></div>')
    rel_posts = [POSTS[(i + k) % len(POSTS)] for k in (1, 2, 3)]
    main = (figure(p["key"], 1600, 900, True) + add_sample(p) +
            cta("Need writing like this?", "Copacetic Marketing provides press releases, ghostwriting and content for law firms, real estate professionals and businesses nationwide.") +
            related(rel_posts, path))
    schema = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": p["title"], "url": f"{DOMAIN}/{path}/",
              "image": img_url(p["key"], 1200, 630), "author": {"@type": "Person", "name": "Fritts Causby", "url": FC},
              "publisher": {"@type": "Organization", "name": "Copacetic Marketing", "url": DOMAIN + "/"}}
    write(path, page("blog", f"{p['title']} | Copacetic Marketing", desc, top, main, here=path, og_image=p["key"], schema=schema))

# 404 page
with open(f"{OUT}/404.html", "w") as f:
    f.write(page("home", "Page not found | Copacetic Marketing", "This page could not be found.",
                 header_block("404", "Page not found", "The page may have moved."),
                 '<p>Try the <a href="/">home page</a>, the <a href="/services-1/">services</a> or the <a href="/blog/">blog</a>.</p>').replace('href="./"', 'href="/"'))

if not PREVIEW:
    with open(f"{OUT}/CNAME", "w") as f:
        f.write("copacetic.marketing\n")
    with open(f"{OUT}/robots.txt", "w") as f:
        bots = ["GPTBot", "ClaudeBot", "anthropic-ai", "CCBot", "Google-Extended", "Applebot-Extended",
                "Meta-ExternalAgent", "DuckAssistBot", "cohere-ai", "Bytespider"]
        f.write("".join(f"User-agent: {b}\nDisallow: /\n\n" for b in bots) +
                f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n")
    allp = list(PAGES.values()) + ["blog/" + p["slug"] for p in POSTS]
    urls = "".join(f"  <url><loc>{DOMAIN}/{p + '/' if p else ''}</loc></url>\n" for p in allp)
    with open(f"{OUT}/sitemap.xml", "w") as f:
        f.write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')
    open(f"{OUT}/.nojekyll", "w").close()
print("built", OUT)
