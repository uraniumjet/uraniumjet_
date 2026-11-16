"""All site copy and contact details live here, so you can edit the site without touching templates.

Items marked CHECK are details taken from your old flyer and website; confirm them before launch.
"""

SITE = {
    "name": "Uranium Jet Digital Solution",
    "short": "Uranium Jet",
    "tagline": "Software and IT, built in Kano.",
    "description": (
        "Uranium Jet Digital Solution builds management software, websites and IT "
        "support for businesses and institutions in Nigeria, and runs a print and "
        "cyber café counter in Kano."
    ),
    "email": "uraniumjetdigitalsolution@gmail.com",
    # CHECK: the old website listed 0814547724 (only 10 digits); the flyer lists 08087314361.
    "phones": [
        {"display": "09034097508", "intl": "+2349034097508"},
        {"display": "08087314361", "intl": "+2348087314361"},
    ],
    # WhatsApp number in international format, digits only (Nigeria = 234, drop the leading 0).
    "whatsapp": "2349034097508",
    "whatsapp_text": "Hello Uranium Jet, I found your website and would like to talk.",
    # CHECK: address is from the flyer.
    "address_lines": [
        "No. 220 Dandago Quarters",
        "Abdullahi Wasai Road",
        "Kano, Kano State, Nigeria",
    ],
    "demo_url": "https://hostel-meals-demo.onrender.com",
    # Optional line shown next to the demo button, for example login details for the demo.
    # Leave empty if the demo needs no login.
    "demo_hint": "",
}

NAV = [
    ("products", "Products"),
    ("services", "Services"),
    ("how_we_work", "How we work"),
    ("team", "Team"),
    ("contact", "Contact"),
]

# Used on the home page and on /services.
SERVICE_GROUPS = [
    {
        "id": "software",
        "title": "Software and web",
        "summary": "Management systems, websites and web apps built around how your organisation actually works.",
        "points": [
            "Custom management systems for hostels, schools, shops and offices",
            "Business websites and web applications",
            "Moving paper records and spreadsheets onto digital systems",
        ],
    },
    {
        "id": "it-support",
        "title": "IT support",
        "summary": "Setup, installation, troubleshooting and advice for offices and institutions.",
        "points": [
            "Computer and software installation",
            "Troubleshooting and repairs guidance",
            "IT consultancy for small organisations",
        ],
    },
    {
        "id": "print-design",
        "title": "Print and design",
        "summary": "Printing, photocopying and finished design work from one counter.",
        "points": [
            "Photocopying, digital printing, scanning and typing",
            "Laminating and binding",
            "Flyers, pamphlets, posters and banners",
            "Logos, business cards and letterheads",
            "Animation design",
        ],
    },
    {
        "id": "cyber-cafe",
        "title": "Cyber café",
        "summary": "Internet access and document help for people who need to get online.",
        "points": [
            "Internet browsing and WiFi",
            "Email and online applications",
            "Digital document services",
        ],
    },
]

PRODUCT_HOSTEL = {
    "name": "Hostel Meals",
    "headline": "Know who ate, who is away, and what to report.",
    "summary": (
        "Hostel Meals records every meal for every resident, tracks exit permits, and gives "
        "the central office the reports it needs. It is built for hostels and mess halls, and "
        "it is not tied to one institution: any organisation that serves meals to residents "
        "can use it."
    ),
    "features": [
        {
            "title": "Meal records for every resident",
            "text": "Each meal is recorded against the student, including when a friend collects it on their behalf.",
        },
        {
            "title": "Exit permits the warden can grant",
            "text": "A student on permit shows as on leave, with the days left before they count as absent. Meals missed inside the permit carry no fine.",
        },
        {
            "title": "Special periods on demand",
            "text": "Ramadan and Navratri are handled by the admin setting the period when it begins, such as the Iftar time, instead of fixed timetables.",
        },
        {
            "title": "Reports, not charges",
            "text": "The system never charges fines itself. It produces the reports the central admin uses to charge students.",
        },
        {
            "title": "Photos at registration",
            "text": "The warden takes each student's photo when they register, so staff can recognise who they are serving.",
        },
        {
            "title": "Reusable by other organisations",
            "text": "Built as a general system, so a new hostel can be set up without rebuilding anything.",
        },
    ],
}

PRODUCTS_PLANNED = [
    {
        "name": "Sales record system",
        "text": "Daily sales, stock and receipts for small shops.",
    },
    {
        "name": "School portal",
        "text": "Student records, results and notices for schools.",
    },
]

# True sequence, so numbering is meaningful.
PROCESS = [
    {
        "title": "Listen",
        "short": "We start with a conversation or a visit to see how you work today.",
        "long": "We ask how the work happens now: who does what, on paper or on screen, and where it goes wrong. We would rather understand your routine than sell you a feature list.",
        "you": "A person who knows the day-to-day work, and a few real examples such as a register or a spreadsheet.",
    },
    {
        "title": "Scope",
        "short": "You get a written plan of what we will build, in plain language.",
        "long": "We write down what the system will and will not do, who uses it, and what you will have after the first release. You agree the plan before any build starts.",
        "you": "A decision-maker who can approve the plan and answer questions quickly.",
    },
    {
        "title": "Build in small releases",
        "short": "You try working versions early, and we adjust as you go.",
        "long": "We build the most important part first and put it in front of you, on a live link where possible. Changes are cheaper to make while the system is small.",
        "you": "A few hours of feedback after each release from the people who will use it.",
    },
    {
        "title": "Hand over and support",
        "short": "We train your staff and stay reachable after launch.",
        "long": "We train the people who will run the system, hand over the admin access, and keep a direct line open on WhatsApp or by phone for questions and fixes.",
        "you": "The staff who will use the system, available for training.",
    },
]

TEAM = [
    {
        "name": "Yusuf Ahmad Shehu",
        "role": "CEO and Managing Director",
        "bio": "Python developer who builds the company's software products. He is also studying for an MSc in AI and cyber security.",
        "photo": "img/yusuf.jpg",
        "alt": "Yusuf Ahmad Shehu",
    },
    {
        "name": "Engr. Ahmad Ahmad Abdullahi",
        "role": "Co-founder, Digital Transformation",
        "bio": "Leads digital transformation work with clients, helping organisations move their operations onto digital systems.",
        "photo": "img/ahmad.jpg",
        "alt": "Engr. Ahmad Ahmad Abdullahi",
    },
]

VALUES = [
    ("Innovation", "We look for practical ways to make work faster and simpler."),
    ("Integrity", "We say plainly what a system can and cannot do."),
    ("Excellence", "We finish work properly, whether it is software or a printed flyer."),
    ("Customer satisfaction", "A job is done when the people using it are happy with it."),
]

CONTACT_TOPICS = [
    ("software", "A software system or website"),
    ("hostel-meals", "The Hostel Meals system"),
    ("it-support", "IT support"),
    ("print-design", "Printing or design"),
    ("other", "Something else"),
]
