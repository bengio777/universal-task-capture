"""Category definitions for task classification.

Ported from the Claude Skill (SKILL.md). Single source of truth for
category names, descriptions, examples, and classification rules.
"""

CONFIDENCE_THRESHOLD = 0.8

CATEGORIES = {
    "Shopping / Errands": {
        "description": "Physical tasks, purchases, pickups, drop-offs",
        "examples": [
            "Pick up dry cleaning",
            "Buy birthday gift for Mom",
            "Return Amazon package",
            "Get groceries",
        ],
    },
    "Technical / Dev": {
        "description": "Coding, debugging, infrastructure, tooling, dev environment, CI/CD",
        "examples": [
            "Fix the auth bug in login flow",
            "Set up CI pipeline",
            "Refactor the API layer",
            "Update Node version",
        ],
    },
    "Class / Study": {
        "description": "Coursework, certification prep, learning tasks, study sessions, exam prep",
        "examples": [
            "Review Chapter 7 on access controls",
            "Practice CompTIA labs",
            "Read the PKI section",
            "Study for quiz",
        ],
    },
    "Content / Writing": {
        "description": "Blog posts, articles, social media, creative writing, media production, newsletters",
        "examples": [
            "Draft the Substack post on AI workflows",
            "Write LinkedIn post about MEDDPICC",
            "Outline podcast episode",
        ],
    },
    "Business / Sales": {
        "description": "Revenue, pipeline, CRM, discovery calls, proposals, customer-facing, operational",
        "examples": [
            "Follow up with Acme Corp on the proposal",
            "Update CRM with call notes",
            "Prep for Thursday's discovery call",
        ],
    },
    "Personal": {
        "description": "Health, finance, home, life admin, relationships, non-work tasks",
        "examples": [
            "Schedule dentist appointment",
            "Call Dad this weekend",
            "Renew passport",
            "Pay electric bill",
        ],
    },
    "Workflow / Process": {
        "description": "Building, documenting, improving workflows, systems, skills, automations",
        "examples": [
            "Write SOP for onboarding workflow",
            "Add a new category to capture skill",
            "Review classification accuracy",
        ],
    },
    "Social / Community": {
        "description": "Events, meetups, community engagement, networking, social commitments",
        "examples": [
            "RSVP to the AI meetup",
            "Follow up with Maria from the conference",
            "Plan game night",
            "Join the Discord event",
        ],
    },
}

CLASSIFICATION_RULES = """
1. Choose the single best category. Never multi-classify.
2. If the task clearly fits one category, assign it immediately.
3. If the task is ambiguous between exactly two categories, state both and ask the user which one.
4. If the task doesn't fit any category, classify as "Needs Sorting".
5. Use any additional context from the conversation to inform classification.
"""
