export type Language = "en" | "hi" | "bn";

export const LANGUAGE_LABELS: Record<Language, string> = {
  en: "English",
  hi: "हिन्दी",
  bn: "বাংলা",
};

const translations = {
  en: {
    skipToContent: "Skip to main content", prototype: "Scholarship Verification Prototype",
    title: "TRISETU", subtitle: "AI-enabled scholarship & fellowship management system for Scheduled Tribes",
    ministry: "Ministry of Tribal Affairs • Workflow Prototype", studentPortal: "Student Portal",
    adminPortal: "Administration", applications: "Applications", home: "Home", language: "Language",
    prototypeNotice: "Prototype • Not an official Government of India portal",
    uploadDocuments: "Upload documents", demoMode: "Demo Mode", createApplication: "Create application",
    applicationCreated: "Application created successfully.", selectScheme: "1. Select scheme",
    uploadStep: "2. Upload documents", uploadAvailable: "Upload available documents",
    uploadHelp: "Upload the documents you have. Verification will check whether all required documents are present.",
    noFile: "No file selected", chooseFile: "Choose file", changeFile: "Change file",
    documentsSelected: "Documents selected", missingDocuments: "Missing required documents will be identified during verification.",
    uploadVerify: "Upload documents & verify", uploading: "Uploading...", processing: "Processing",
    startingVerification: "Starting OCR and verification...", verificationProcessing: "Verification is still processing",
    verificationCompleted: "Verification completed", applicationId: "Application ID", studentId: "Student ID",
    scheme: "Scheme", status: "Status", riskScore: "Risk score", notEvaluated: "Not evaluated",
    requiredDocuments: "Required Documents", category: "Category", income: "Income", academic: "Academic",
    passed: "Passed", notPassed: "Not passed", severity: "Severity", result: "Result",
    extractedValue: "Extracted value", expectedCondition: "Expected condition", reasoning: "Reasoning",
    noValidation: "No validation results available.", studentInformation: "Student Information",
    uploadedDocuments: "Uploaded Documents", noDocuments: "No documents uploaded.", ocrStatus: "OCR status",
    validationScorecard: "Validation Scorecard", humanReview: "Human Review",
    flaggedReview: "This application was flagged for administrative review. A mismatch is a review signal, not an automatic fraud decision.",
    reviewReason: "Administrative review reason", approve: "Approve", requestResubmission: "Request resubmission",
    reject: "Reject", applicationDashboard: "Application dashboard",
    dashboardDescription: "Monitor applications, verification and review queues.",
    totalApplications: "Total applications", flaggedForReview: "Flagged for review",
    applicationReview: "Application review", reviewDescription: "Review applications and inspect document-level validation.",
    viewApplications: "View applications", applicationQueue: "Application Queue", review: "Review",
    loadingApplications: "Loading applications…", noApplications: "No applications found.", retry: "Retry",
    reviewApplicationsDescription: "Review scholarship applications and verification status.",
    loadingApplication: "Loading application review…", footerText: "TRISETU • Scholarship verification workflow prototype",
    govInspired: "Designed with citizen-first accessibility and multilingual principles inspired by Indian government web standards.",
    incomeCertificate: "Income Certificate", casteCertificate: "Caste Certificate", academicRecord: "Academic Record",
    identityDocument: "Identity Document", preMatric: "Pre-Matric Scholarship", postMatric: "Post-Matric Scholarship",
    topClass: "National Scholarship Scheme - Top Class", nationalFellowship: "National Fellowship Scheme",
    nationalOverseas: "National Overseas Scholarship", submitted: "Submitted", approved: "Approved",
    deficient: "Deficient", resubmitted: "Resubmitted", flagged: "Flagged for Review",
    adminReviewStatus: "Admin Review", rejected: "Rejected", ocrProcessing: "Processing",
    readable: "Readable", unreadable: "Unreadable", partiallyReadable: "Partially Readable",
    noReasoning: "No reasoning available.", notAvailable: "Not available",
    errorCreate: "Application creation failed.", errorUpload: "Document verification failed.",
    errorApplications: "Could not load applications.", errorApplication: "Could not load this application.",
    errorReview: "Administrative review failed.", demoIdMissing: "Demo Mode is not configured. NEXT_PUBLIC_DEMO_STUDENT_ID is missing.",
    createBeforeUpload: "Create the application before uploading documents.",
    selectDocument: "Please select at least one document before verification.",
    invalidFile: "is invalid. Use a non-empty PDF, JPG, JPEG or PNG file up to 10 MB.",
    none: "None", low: "Low", medium: "Medium", high: "High",
    reviewReasonDefault: "Reviewed by administrator based on the submitted evidence.",
  },
  hi: {
    skipToContent: "मुख्य सामग्री पर जाएँ", prototype: "छात्रवृत्ति सत्यापन प्रोटोटाइप",
    title: "TRISETU", subtitle: "अनुसूचित जनजातियों के लिए AI-सक्षम छात्रवृत्ति एवं फेलोशिप प्रबंधन प्रणाली",
    ministry: "जनजातीय कार्य मंत्रालय • वर्कफ़्लो प्रोटोटाइप", studentPortal: "छात्र पोर्टल",
    adminPortal: "प्रशासन", applications: "आवेदन", home: "होम", language: "भाषा",
    prototypeNotice: "प्रोटोटाइप • भारत सरकार का आधिकारिक पोर्टल नहीं",
    uploadDocuments: "दस्तावेज़ अपलोड करें", demoMode: "डेमो मोड", createApplication: "आवेदन बनाएँ",
    applicationCreated: "आवेदन सफलतापूर्वक बनाया गया।", selectScheme: "1. योजना चुनें",
    uploadStep: "2. दस्तावेज़ अपलोड करें", uploadAvailable: "उपलब्ध दस्तावेज़ अपलोड करें",
    uploadHelp: "अपने उपलब्ध दस्तावेज़ अपलोड करें। सत्यापन में आवश्यक दस्तावेज़ों की जाँच होगी।",
    noFile: "कोई फ़ाइल चयनित नहीं", chooseFile: "फ़ाइल चुनें", changeFile: "फ़ाइल बदलें",
    documentsSelected: "चयनित दस्तावेज़", missingDocuments: "सत्यापन के दौरान आवश्यक दस्तावेज़ों की कमी बताई जाएगी।",
    uploadVerify: "दस्तावेज़ अपलोड एवं सत्यापित करें", uploading: "अपलोड हो रहा है...", processing: "प्रक्रिया जारी है",
    startingVerification: "OCR और सत्यापन शुरू हो रहा है...", verificationProcessing: "सत्यापन अभी प्रक्रिया में है",
    verificationCompleted: "सत्यापन पूरा हुआ", applicationId: "आवेदन आईडी", studentId: "छात्र आईडी",
    scheme: "योजना", status: "स्थिति", riskScore: "जोखिम स्कोर", notEvaluated: "मूल्यांकन नहीं हुआ",
    requiredDocuments: "आवश्यक दस्तावेज़", category: "श्रेणी", income: "आय", academic: "शैक्षणिक",
    passed: "उत्तीर्ण", notPassed: "उत्तीर्ण नहीं", severity: "गंभीरता", result: "परिणाम",
    extractedValue: "निकाला गया मान", expectedCondition: "अपेक्षित शर्त", reasoning: "कारण",
    noValidation: "कोई सत्यापन परिणाम उपलब्ध नहीं है।", studentInformation: "छात्र जानकारी",
    uploadedDocuments: "अपलोड किए गए दस्तावेज़", noDocuments: "कोई दस्तावेज़ अपलोड नहीं किया गया।", ocrStatus: "OCR स्थिति",
    validationScorecard: "सत्यापन स्कोरकार्ड", humanReview: "मानवीय समीक्षा",
    flaggedReview: "इस आवेदन को प्रशासनिक समीक्षा के लिए चिन्हित किया गया है। असंगति समीक्षा का संकेत है, स्वतः धोखाधड़ी का निर्णय नहीं।",
    reviewReason: "प्रशासनिक समीक्षा का कारण", approve: "स्वीकृत करें", requestResubmission: "पुनः जमा करने का अनुरोध",
    reject: "अस्वीकार करें", applicationDashboard: "आवेदन डैशबोर्ड",
    dashboardDescription: "आवेदन, सत्यापन और समीक्षा कतारों की निगरानी करें।",
    totalApplications: "कुल आवेदन", flaggedForReview: "समीक्षा के लिए चिन्हित",
    applicationReview: "आवेदन समीक्षा", reviewDescription: "छात्रवृत्ति आवेदनों और दस्तावेज़ सत्यापन की समीक्षा करें।",
    viewApplications: "आवेदन देखें", applicationQueue: "आवेदन कतार", review: "समीक्षा",
    loadingApplications: "आवेदन लोड हो रहे हैं…", noApplications: "कोई आवेदन नहीं मिला।", retry: "पुनः प्रयास",
    reviewApplicationsDescription: "छात्रवृत्ति आवेदनों और सत्यापन स्थिति की समीक्षा करें.",
    loadingApplication: "आवेदन समीक्षा लोड हो रही है…", footerText: "TRISETU • छात्रवृत्ति सत्यापन वर्कफ़्लो प्रोटोटाइप",
    govInspired: "भारतीय सरकारी वेब मानकों से प्रेरित नागरिक-केंद्रित, सुलभ और बहुभाषी सिद्धांतों के साथ डिज़ाइन किया गया।",
    incomeCertificate: "आय प्रमाण पत्र", casteCertificate: "जाति प्रमाण पत्र", academicRecord: "शैक्षणिक रिकॉर्ड",
    identityDocument: "पहचान दस्तावेज़", preMatric: "प्री-मैट्रिक छात्रवृत्ति", postMatric: "पोस्ट-मैट्रिक छात्रवृत्ति",
    topClass: "राष्ट्रीय छात्रवृत्ति योजना - टॉप क्लास", nationalFellowship: "राष्ट्रीय फेलोशिप योजना",
    nationalOverseas: "राष्ट्रीय ओवरसीज़ छात्रवृत्ति", submitted: "जमा किया गया", approved: "स्वीकृत",
    deficient: "अपूर्ण", resubmitted: "पुनः जमा", flagged: "समीक्षा के लिए चिन्हित",
    adminReviewStatus: "प्रशासनिक समीक्षा", rejected: "अस्वीकृत", ocrProcessing: "प्रक्रिया जारी",
    readable: "पठनीय", unreadable: "अपठनीय", partiallyReadable: "आंशिक रूप से पठनीय",
    noReasoning: "कोई कारण उपलब्ध नहीं है।", notAvailable: "उपलब्ध नहीं",
    errorCreate: "आवेदन बनाना विफल हुआ।", errorUpload: "दस्तावेज़ सत्यापन विफल हुआ.",
    errorApplications: "आवेदन लोड नहीं हो सके।", errorApplication: "यह आवेदन लोड नहीं हो सका।",
    errorReview: "प्रशासनिक समीक्षा विफल हुई।", demoIdMissing: "डेमो मोड कॉन्फ़िगर नहीं है। NEXT_PUBLIC_DEMO_STUDENT_ID उपलब्ध नहीं है।",
    createBeforeUpload: "दस्तावेज़ अपलोड करने से पहले आवेदन बनाएँ।",
    selectDocument: "सत्यापन से पहले कम से कम एक दस्तावेज़ चुनें।",
    invalidFile: "अमान्य है। 10 MB तक की गैर-रिक्त PDF, JPG, JPEG या PNG फ़ाइल का उपयोग करें।",
    none: "कोई नहीं", low: "कम", medium: "मध्यम", high: "उच्च",
    reviewReasonDefault: "प्रस्तुत साक्ष्य के आधार पर प्रशासक द्वारा समीक्षा की गई।",
  },
  bn: {
    skipToContent: "মূল বিষয়বস্তুতে যান", prototype: "বৃত্তি যাচাইকরণ প্রোটোটাইপ",
    title: "TRISETU", subtitle: "তফসিলি উপজাতিদের জন্য AI-সক্ষম বৃত্তি ও ফেলোশিপ ব্যবস্থাপনা ব্যবস্থা",
    ministry: "জনজাতীয় বিষয়ক মন্ত্রক • ওয়ার্কফ্লো প্রোটোটাইপ", studentPortal: "শিক্ষার্থী পোর্টাল",
    adminPortal: "প্রশাসন", applications: "আবেদন", home: "হোম", language: "ভাষা",
    prototypeNotice: "প্রোটোটাইপ • ভারত সরকারের সরকারি পোর্টাল নয়",
    uploadDocuments: "নথি আপলোড করুন", demoMode: "ডেমো মোড", createApplication: "আবেদন তৈরি করুন",
    applicationCreated: "আবেদন সফলভাবে তৈরি হয়েছে।", selectScheme: "১. প্রকল্প নির্বাচন করুন",
    uploadStep: "২. নথি আপলোড করুন", uploadAvailable: "উপলব্ধ নথি আপলোড করুন",
    uploadHelp: "আপনার কাছে থাকা নথিগুলি আপলোড করুন। যাচাইকরণে প্রয়োজনীয় নথি পরীক্ষা করা হবে।",
    noFile: "কোনও ফাইল নির্বাচিত নয়", chooseFile: "ফাইল নির্বাচন করুন", changeFile: "ফাইল পরিবর্তন করুন",
    documentsSelected: "নির্বাচিত নথি", missingDocuments: "যাচাইকরণের সময় প্রয়োজনীয় নথির ঘাটতি চিহ্নিত করা হবে।",
    uploadVerify: "নথি আপলোড ও যাচাই করুন", uploading: "আপলোড হচ্ছে...", processing: "প্রক্রিয়া চলছে",
    startingVerification: "OCR ও যাচাইকরণ শুরু হচ্ছে...", verificationProcessing: "যাচাইকরণ এখনও চলছে",
    verificationCompleted: "যাচাইকরণ সম্পন্ন", applicationId: "আবেদন আইডি", studentId: "শিক্ষার্থী আইডি",
    scheme: "প্রকল্প", status: "স্থিতি", riskScore: "ঝুঁকি স্কোর", notEvaluated: "মূল্যায়ন হয়নি",
    requiredDocuments: "প্রয়োজনীয় নথি", category: "শ্রেণি", income: "আয়", academic: "শিক্ষাগত",
    passed: "পাস", notPassed: "পাস নয়", severity: "গুরুত্ব", result: "ফলাফল",
    extractedValue: "উদ্ধার করা মান", expectedCondition: "প্রত্যাশিত শর্ত", reasoning: "কারণ",
    noValidation: "কোনও যাচাইকরণ ফলাফল পাওয়া যায়নি।", studentInformation: "শিক্ষার্থীর তথ্য",
    uploadedDocuments: "আপলোড করা নথি", noDocuments: "কোনও নথি আপলোড করা হয়নি।", ocrStatus: "OCR অবস্থা",
    validationScorecard: "যাচাইকরণ স্কোরকার্ড", humanReview: "মানবিক পর্যালোচনা",
    flaggedReview: "এই আবেদনটি প্রশাসনিক পর্যালোচনার জন্য চিহ্নিত হয়েছে। অসঙ্গতি পর্যালোচনার সংকেত, স্বয়ংক্রিয় জালিয়াতির সিদ্ধান্ত নয়।",
    reviewReason: "প্রশাসনিক পর্যালোচনার কারণ", approve: "অনুমোদন করুন", requestResubmission: "পুনরায় জমা দেওয়ার অনুরোধ",
    reject: "প্রত্যাখ্যান করুন", applicationDashboard: "আবেদন ড্যাশবোর্ড",
    dashboardDescription: "আবেদন, যাচাইকরণ এবং পর্যালোচনা সারি পর্যবেক্ষণ করুন।",
    totalApplications: "মোট আবেদন", flaggedForReview: "পর্যালোচনার জন্য চিহ্নিত",
    applicationReview: "আবেদন পর্যালোচনা", reviewDescription: "বৃত্তি আবেদন ও নথি যাচাইকরণ পর্যালোচনা করুন।",
    viewApplications: "আবেদন দেখুন", applicationQueue: "আবেদন সারি", review: "পর্যালোচনা",
    loadingApplications: "আবেদন লোড হচ্ছে…", noApplications: "কোনও আবেদন পাওয়া যায়নি।", retry: "আবার চেষ্টা করুন",
    reviewApplicationsDescription: "বৃত্তি আবেদন ও যাচাইকরণের অবস্থা পর্যালোচনা করুন।",
    loadingApplication: "আবেদন পর্যালোচনা লোড হচ্ছে…", footerText: "TRISETU • বৃত্তি যাচাইকরণ ওয়ার্কফ্লো প্রোটোটাইপ",
    govInspired: "ভারতীয় সরকারি ওয়েব মানদণ্ড থেকে অনুপ্রাণিত নাগরিক-কেন্দ্রিক, অ্যাক্সেসযোগ্য ও বহুভাষিক নীতিতে ডিজাইন করা।",
    incomeCertificate: "আয় শংসাপত্র", casteCertificate: "জাতি শংসাপত্র", academicRecord: "শিক্ষাগত রেকর্ড",
    identityDocument: "পরিচয় নথি", preMatric: "প্রি-ম্যাট্রিক বৃত্তি", postMatric: "পোস্ট-ম্যাট্রিক বৃত্তি",
    topClass: "জাতীয় বৃত্তি প্রকল্প - টপ ক্লাস", nationalFellowship: "জাতীয় ফেলোশিপ প্রকল্প",
    nationalOverseas: "জাতীয় ওভারসিজ বৃত্তি", submitted: "জমা হয়েছে", approved: "অনুমোদিত",
    deficient: "অসম্পূর্ণ", resubmitted: "পুনরায় জমা", flagged: "পর্যালোচনার জন্য চিহ্নিত",
    adminReviewStatus: "প্রশাসনিক পর্যালোচনা", rejected: "প্রত্যাখ্যাত", ocrProcessing: "প্রক্রিয়াধীন",
    readable: "পাঠযোগ্য", unreadable: "অপাঠযোগ্য", partiallyReadable: "আংশিকভাবে পাঠযোগ্য",
    noReasoning: "কোনও কারণ পাওয়া যায়নি।", notAvailable: "উপলব্ধ নয়",
    errorCreate: "আবেদন তৈরি করা যায়নি।", errorUpload: "নথি যাচাইকরণ ব্যর্থ হয়েছে।",
    errorApplications: "আবেদন লোড করা যায়নি।", errorApplication: "এই আবেদনটি লোড করা যায়নি।",
    errorReview: "প্রশাসনিক পর্যালোচনা ব্যর্থ হয়েছে।", demoIdMissing: "ডেমো মোড কনফিগার করা নেই। NEXT_PUBLIC_DEMO_STUDENT_ID নেই।",
    createBeforeUpload: "নথি আপলোডের আগে আবেদন তৈরি করুন।",
    selectDocument: "যাচাইকরণের আগে অন্তত একটি নথি নির্বাচন করুন।",
    invalidFile: "অবৈধ। ১০ MB পর্যন্ত খালি নয় এমন PDF, JPG, JPEG বা PNG ফাইল ব্যবহার করুন।",
    none: "কোনও নয়", low: "কম", medium: "মাঝারি", high: "উচ্চ",
    reviewReasonDefault: "জমা দেওয়া প্রমাণের ভিত্তিতে প্রশাসক পর্যালোচনা করেছেন।",
  },
} as const;

export type TranslationKey = keyof typeof translations.en;

export function translate(language: Language, key: TranslationKey): string {
  return translations[language][key] ?? translations.en[key];
}

export function schemeLabel(language: Language, schemeId: string): string {
  const keys: Record<string, TranslationKey> = {
    PRE_MATRIC: "preMatric", POST_MATRIC: "postMatric", TOP_CLASS: "topClass",
    NATIONAL_FELLOWSHIP: "nationalFellowship", NATIONAL_OVERSEAS: "nationalOverseas",
  };
  return keys[schemeId] ? translate(language, keys[schemeId]) : schemeId;
}

export function statusLabel(language: Language, status: string): string {
  const keys: Record<string, TranslationKey> = {
    SUBMITTED: "submitted", PROCESSING: "processing", APPROVED: "approved",
    DEFICIENT: "deficient", RESUBMITTED: "resubmitted", FLAGGED_FOR_REVIEW: "flagged",
    ADMIN_REVIEW: "adminReviewStatus", REJECTED: "rejected",
  };
  return keys[status] ? translate(language, keys[status]) : status;
}

export function documentTypeLabel(language: Language, type: string): string {
  const keys: Record<string, TranslationKey> = {
    INCOME_CERTIFICATE: "incomeCertificate", CASTE_CERTIFICATE: "casteCertificate",
    ACADEMIC_RECORD: "academicRecord", IDENTITY_DOCUMENT: "identityDocument",
  };
  return keys[type] ? translate(language, keys[type]) : type;
}

export function ocrStatusLabel(language: Language, status: string): string {
  const keys: Record<string, TranslationKey> = {
    PROCESSING: "ocrProcessing", READABLE: "readable", UNREADABLE: "unreadable",
    PARTIALLY_READABLE: "partiallyReadable",
  };
  return keys[status] ? translate(language, keys[status]) : status;
}
