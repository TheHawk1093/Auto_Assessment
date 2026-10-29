"""Fixed wording that code (not the model) puts into feedback, in the languages we support.

When feedback is written in the student's language, every word the student sees should be in it:
the model writes the body, and these strings cover the labels and the feedback that needs no
model (full marks, no answer). A language without an entry falls back to English. The wording
for Tamil and Bengali has not been checked by a native speaker.
"""

from __future__ import annotations

ENGLISH = {
    "did_well": "What you did well",
    "partial": "Partly there",
    "missed": "Missed",
    "incorrect": "Incorrect",
    "full": "Overall, this response earned full marks and needs no changes.",
    "empty": "No answer was given for this question, so no marks could be awarded.",
    "wrote": 'You wrote "{said}", which covers: {idea}.',
    "covered": "Covered: {idea}.",
}

STRINGS: dict[str, dict[str, str]] = {
    "": ENGLISH,
    "Hindi": {
        "did_well": "आपने जो अच्छा किया",
        "partial": "आंशिक रूप से सही",
        "missed": "छूटा हुआ",
        "incorrect": "गलत",
        "full": "कुल मिलाकर, इस उत्तर को पूरे अंक मिले हैं और किसी बदलाव की आवश्यकता नहीं है।",
        "empty": "इस प्रश्न का कोई उत्तर नहीं दिया गया, इसलिए कोई अंक नहीं दिए जा सके।",
        "wrote": 'आपने लिखा "{said}", जो इसे पूरा करता है: {idea}.',
        "covered": "पूरा हुआ: {idea}.",
    },
    "Marathi": {
        "did_well": "तुम्ही चांगले काय केले",
        "partial": "अंशतः बरोबर",
        "missed": "राहिलेले",
        "incorrect": "चुकीचे",
        "full": "एकंदरीत, या उत्तराला पूर्ण गुण मिळाले आहेत आणि कोणत्याही बदलाची गरज नाही.",
        "empty": "या प्रश्नाचे उत्तर दिलेले नाही, त्यामुळे गुण देता आले नाहीत.",
        "wrote": 'तुम्ही लिहिले "{said}", जे याला पूर्ण करते: {idea}.',
        "covered": "पूर्ण: {idea}.",
    },
    "Tamil": {
        "did_well": "நீங்கள் நன்றாகச் செய்தவை",
        "partial": "ஓரளவு சரி",
        "missed": "விடுபட்டது",
        "incorrect": "தவறு",
        "full": "ஒட்டுமொத்தமாக, இந்த விடைக்கு முழு மதிப்பெண்கள் கிடைத்துள்ளன; எந்த மாற்றமும் தேவையில்லை.",
        "empty": "இந்தக் கேள்விக்கு விடை எதுவும் அளிக்கப்படவில்லை, எனவே மதிப்பெண் வழங்க இயலவில்லை.",
        "wrote": 'நீங்கள் "{said}" என்று எழுதியுள்ளீர்கள்; இது பின்வருவதை உள்ளடக்குகிறது: {idea}.',
        "covered": "உள்ளடக்கப்பட்டது: {idea}.",
    },
    "Bengali": {
        "did_well": "আপনি যা ভালো করেছেন",
        "partial": "আংশিক সঠিক",
        "missed": "বাদ পড়েছে",
        "incorrect": "ভুল",
        "full": "সামগ্রিকভাবে, এই উত্তরটি পূর্ণ নম্বর পেয়েছে এবং কোনো পরিবর্তনের প্রয়োজন নেই।",
        "empty": "এই প্রশ্নের কোনো উত্তর দেওয়া হয়নি, তাই কোনো নম্বর দেওয়া যায়নি।",
        "wrote": 'আপনি লিখেছেন "{said}", যা এটি পূর্ণ করে: {idea}.',
        "covered": "পূর্ণ হয়েছে: {idea}.",
    },
}


def words(language: str = "") -> dict[str, str]:
    return STRINGS.get(language.strip().title(), ENGLISH)
