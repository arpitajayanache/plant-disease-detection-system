/* === LeafAI — React CDN App === */
const { useState, useEffect, useRef, useCallback } = React;

const API_BASE = "http://localhost:5000/api";

const TRANSLATIONS = {
  English: {
    how: "How It Works", scan: "Scanner", summary: "Summary", welcome: "Detect. Diagnose. Heal.",
    tagline: "AI-powered plant disease detection for farmers — fast, accurate, and multilingual.",
    login: "Login", signup: "Sign Up", create: "Create Account", name: "Full Name", email: "Email Address", pass: "Password", confirm: "Confirm Password",
    lang: "Preferred Language", processing: "Processing...", start: "Start Scanning →",
    hero_title: "How LeafAI Works", hero_desc: "Simple steps to protect your crops with the power of AI.",
    step1_title: "Upload or Capture", step1_desc: "Upload a clear photo of the plant leaf from your device or use your camera.",
    step2_title: "AI Analysis", step2_desc: "Our CNN model scans the leaf and detects disease regions in real-time.",
    step3_title: "Get Cure & Guidance", step3_desc: "Receive AI-generated treatment steps with voice assistance support.",
    scan_title: "🔬 Upload Leaf Image", upload_prompt: "Drop your leaf image here or click to upload",
    remove_img: "✕ Remove Image", select_cure_lang: "Select Cure Language", scan_btn: "🔍 Scan Now", upload_first: "Upload an image first",
    results_title: "📊 Detection Results", results_placeholder: "Upload a leaf image and click Scan Now to see results.",
    confidence: "Detection Confidence", detected: "Detected", treatment: "💊 Recommended Treatment", prevention: "🛡️ Preventive Measures",
    pesticides: "🧪 Recommended Pesticides", view_summary: "View Summary →", scan_complete: "Scan Complete! 🌿",
    saved_history: "Your report has been saved to your history.", scan_summary: "🗒️ Scan Summary",
    scan_another: "🔍 Scan Another", dashboard: "🏠 Dashboard", listening: "Listening...", speak_res: "🔊 Read Results",
    voice_assistant: "Voice Assistant", assistant_desc: "I can help you navigate and read results.",
    status_ready: "Ready for commands...", status_listening: "I'm listening...", status_error: "Microphone error.",
    high: "High", medium: "Medium", low: "Low", status: "Status", saved: "Saved ✓", try: "Try:",
    cmd_scan: "Scan now", cmd_home: "Go to Home", cmd_read: "Read results",
    btn_stop_listen: "⏹ Stop Listening", btn_start_listen: "🎤 Start Listening", err_stt: "Speech recognition not supported.",
    err_email: "Enter a valid email.", err_pass: "Password must be 6+ characters.", err_name: "Full name is required.",
    err_confirm: "Passwords do not match.", err_auth: "Authentication failed.", err_server: "Server unreachable. Is the backend running?",
    err_scan: "Failed to analyze image."
  },
  Hindi: {
    how: "यह कैसे काम करता है", scan: "स्कॅन", summary: "सारांश", welcome: "पहचानें। निदान करें। ठीक करें।",
    tagline: "किसानों के लिए एआई-संचालित पौधों के रोग की पहचान - तेज़, सटीक और बहुभाषी।",
    login: "लॉगिन", signup: "साइन अप", create: "खाता बनाएं", name: "पूरा नाम", email: "ईमेल पता", pass: "पासवर्ड", confirm: "पासवर्ड की पुष्टि करें",
    lang: "पसंदीदा भाषा", processing: "प्रसंस्करण...", start: "स्कैनिंग शुरू करें →",
    hero_title: "LeafAI कैसे काम करता है", hero_desc: "एआई की शक्ति से अपनी फसलों की रक्षा करने के लिए सरल कदम।",
    step1_title: "अपलोड या कैप्चर", step1_desc: "अपने डिवाइस से पौधे की पत्ती की स्पष्ट फोटो अपलोड करें या कैमरे का उपयोग करें।",
    step2_title: "एआई विश्लेषण", step2_desc: "हमारा एआई मॉडल पत्ती को स्कैन करता है और वास्तविक समय में बीमारी का पता लगाता है।",
    step3_title: "उपचार और मार्गदर्शन प्राप्त करें", step3_desc: "आवाज सहायता के साथ एआई-जनरेटेड उपचार चरण प्राप्त करें।",
    scan_title: "🔬 पत्ती की छवि अपलोड करें", upload_prompt: "अपनी पत्ती की छवि यहाँ छोड़ें या अपलोड करने के लिए क्लिक करें",
    remove_img: "✕ छवि निकालें", select_cure_lang: "उपचार भाषा चुनें", scan_btn: "🔍 अभी स्कैन करें", upload_first: "पहले एक छवि अपलोड करें",
    results_title: "📊 पहचान के परिणाम", results_placeholder: "पत्ती की छवि अपलोड करें और परिणाम देखने के लिए 'अभी स्कैन करें' पर क्लिक करें।",
    confidence: "पहचान का आत्मविश्वास", detected: "पहचाना गया", treatment: "💊 अनुशंसित उपचार", prevention: "🛡️ निवारक उपाय",
    pesticides: "🧪 अनुशंसित कीटनाशक", view_summary: "सारांश देखें →", scan_complete: "स्कैन पूरा हुआ! 🌿",
    saved_history: "आपकी रिपोर्ट आपके इतिहास में सहेजी गई है।", scan_summary: "🗒️ स्कैन सारांश",
    scan_another: "🔍 एक और स्कैन करें", dashboard: "🏠 डैशबोर्ड", listening: "सुन रहा हूँ...", speak_res: "🔊 परिणाम पढ़ें",
    voice_assistant: "आवाज सहायक", assistant_desc: "मैं आपको नेविगेट करने और परिणाम पढ़ने में मदद कर सकता हूँ।",
    status_ready: "कमांड के लिए तैयार...", status_listening: "मैं सुन रहा हूँ...", status_error: "माइक्रोफ़ोन त्रुटि।",
    high: "उच्च", medium: "मध्यम", low: "कम", status: "स्थिति", saved: "सहेजा गया ✓", try: "कोशिश करें:",
    cmd_scan: "अभी स्कैन करें", cmd_home: "होम पर जाएं", cmd_read: "परिणाम पढ़ें",
    btn_stop_listen: "⏹ सुनना बंद करें", btn_start_listen: "🎤 सुनना शुरू करें", err_stt: "भाषण पहचान समर्थित नहीं है.",
    err_email: "एक मान्य ईमेल दर्ज करें।", err_pass: "पासवर्ड 6+ अक्षरों का होना चाहिए।", err_name: "पूरा नाम आवश्यक है।",
    err_confirm: "पासवर्ड मेल नहीं खाते।", err_auth: "प्रमाणीकरण विफल रहा।", err_server: "सर्वर अनुपलब्ध है। क्या बैकएंड चल रहा है?",
    err_scan: "छवि का विश्लेषण करने में विफल।"
  },
  Marathi: {
    how: "हे कसे कार्य करते", scan: "स्कॅनर", summary: "सारांश", welcome: "ओळखा. निदान करा. बरे करा.",
    tagline: "शेतकऱ्यांसाठी एआय-आधारित वनस्पती रोग शोध - जलद, अचूक आणि बहुभाषिक.",
    login: "लॉगिन", signup: "साइन अप", create: "खाते तयार करा", name: "पूर्ण नाव", email: "ईमेल पत्ता", pass: "पासवर्ड", confirm: "पासवर्डची पुष्टी करा",
    lang: "निवडलेली भाषा", processing: "प्रक्रिया होत आहे...", start: "स्कॅनिंग सुरू करा →",
    hero_title: "LeafAI कसे काम करते", hero_desc: "एआई च्या सामर्थ्याने पिकांचे रक्षण करण्यासाठी सोप्या पायऱ्या.",
    step1_title: "अपलोड किंवा कॅप्चर", step1_desc: "तुमच्या डिव्हाइसवरून झाडाच्या पानाचा स्पष्ट फोटो अपलोड करा किंवा कॅमेरा वापरा.",
    step2_title: "एआय विश्लेषण", step2_desc: "आमचे एआई मॉडेल पानांचे स्कॅनिंग करते आणि रिअल-टाइममध्ये रोग शोधते.",
    step3_title: "उपचार आणि मार्गदर्शन मिळवा", step3_desc: "व्हॉइस असिस्टन्स सपोर्टसह एआय-व्युत्पन्न उपचार पायऱ्या मिळवा.",
    scan_title: "🔬 पानांचे चित्र अपलोड करा", upload_prompt: "तुमच्या पानाचे चित्र येथे टाका किंवा अपलोड करण्यासाठी क्लिक करा",
    remove_img: "✕ चित्र काढा", select_cure_lang: "उपचार भाषा निवडा", scan_btn: "🔍 आता स्कॅन करा", upload_first: "प्रथम चित्र अपलोड करा",
    results_title: "📊 शोध परिणाम", results_placeholder: "पानाचे चित्र अपलोड करा आणि निकाल पाहण्यासाठी 'आता स्कॅन करा' वर क्लिक करा.",
    confidence: "ओळखण्याचा आत्मविश्वास", detected: "आढळले", treatment: "💊 शिफारस केलेले उपचार", prevention: "🛡️ प्रतिबंधात्मक उपाय",
    pesticides: "🧪 शिफारस केलेली कीटकनाशके", view_summary: "सारांश पहा →", scan_complete: "स्कॅन पूर्ण झाले! 🌿",
    saved_history: "तुमचा अहवाल तुमच्या इतिहासामध्ये जतन केला गेला आहे.", scan_summary: "🗒️ स्कॅन सारांश",
    scan_another: "🔍 आणखी एक स्कॅन करा", dashboard: "🏠 डॅशबोर्ड", listening: "ऐकत आहे...", speak_res: "🔊 निकाल वाचा",
    voice_assistant: "व्हॉइस असिस्टंट", assistant_desc: "मी तुम्हाला नेव्हिगेट करण्यात आणि निकाल वाचण्यात मदत करू शकतो.",
    status_ready: "कमांडसाठी तयार...", status_listening: "मी ऐकत आहे...", status_error: "मायक्रोफोन त्रुटी.",
    high: "उच्च", medium: "मध्यम", low: "कमी", status: "स्थिती", saved: "जतन केले ✓", try: "प्रयत्न करा:",
    cmd_scan: "आता स्कॅन करा", cmd_home: "होमवर जा", cmd_read: "निकाल वाचा",
    btn_stop_listen: "⏹ ऐकणे थांबवा", btn_start_listen: "🎤 ऐकणे सुरू करा", err_stt: "स्पीच रिकग्निशन सपोर्टेड नाही.",
    err_email: "वैध ईमेल प्रविष्ट करा.", err_pass: "पासवर्ड 6+ वर्णांचा असावा.", err_name: "पूर्ण नाव आवश्यक आहे.",
    err_confirm: "पासवर्ड जुळत नाहीत.", err_auth: "प्रमाणीकरण अयशस्वी.", err_server: "सर्व्हर उपलब्ध नाही. बॅकएंड चालू आहे का?",
    err_scan: "प्रतिमेचे विश्लेषण करण्यात अयशस्वी."
  },
  Kannada: {
    how: "ಇದು ಹೇಗೆ ಕೆಲಸ ಮಾಡುತ್ತದೆ", scan: "ಸ್ಕ್ಯಾನರ್", summary: "ಸಾರಾಂಶ", welcome: "ಗುರುತಿಸಿ. ರೋಗನಿರ್ಣಯ ಮಾಡಿ. ಗುಣಪಡಿಸಿ.",
    tagline: "ರೈತರಿಗಾಗಿ AI-ಚಾಲಿತ ಸಸ್ಯ ರೋಗ ಪತ್ತೆ - ವೇಗವಾಗಿ, ನಿಖರವಾಗಿ ಮತ್ತು ಬಹುಭಾಷಾ.",
    login: "ಲಾಗಿನ್", signup: "ಸೈನ್ ಅಪ್", create: "ಖಾತೆ ರಚಿಸಿ", name: "ಪೂರ್ಣ ಹೆಸರು", email: "ಇಮೇಲ್ ವಿಳಾಸ", pass: "ಪಾಸ್ವರ್ಡ್", confirm: "ಪಾಸ್ವರ್ಡ್ ದೃಢೀಕರಿಸಿ",
    lang: "ಆದ್ಯತೆಯ ಭಾಷೆ", processing: "ಪ್ರಕ್ರಿಯೆಗೊಳಿಸಲಾಗುತ್ತಿದೆ...", start: "ಸ್ಕ್ಯಾನಿಂಗ್ ಪ್ರಾರಂಭಿಸಿ →",
    hero_title: "LeafAI ಹೇಗೆ ಕೆಲಸ ಮಾಡುತ್ತದೆ", hero_desc: "AI ಶಕ್ತಿಯೊಂದಿಗೆ ನಿಮ್ಮ ಬೆಳೆಗಳನ್ನು ರಕ್ಷಿಸಲು ಸರಳ ಹಂತಗಳು.",
    step1_title: "ಅಪ್‌ಲೋಡ್ ಅಥವಾ ಕ್ಯಾಪ್ಚರ್", step1_desc: "ನಿಮ್ಮ ಸಾಧನದಿಂದ ಸಸ್ಯದ ಎಲೆಯ ಸ್ಪಷ್ಟ ಫೋಟೋವನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ ಅಥವಾ ಕ್ಯಾಮೆರಾ ಬಳಸಿ.",
    step2_title: "AI ವಿಶ್ಲೇಣೆ", step2_desc: "ನಮ್ಮ AI ಮಾದರಿಯು ಎಲೆಯನ್ನು ಸ್ಕ್ಯಾನ್ ಮಾಡುತ್ತದೆ ಮತ್ತು ನೈಜ ಸಮಯದಲ್ಲಿ ರೋಗವನ್ನು ಪತ್ತೆ ಮಾಡುತ್ತದೆ.",
    step3_title: "ಚಿಕಿತ್ಸೆ ಮತ್ತು ಮಾರ್ಗದರ್ಶನ ಪಡೆಯಿರಿ", step3_desc: "ಧ್ವನಿ ಸಹಾಯದ ಬೆಂಬಲದೊಂದಿಗೆ AI-ರಚಿತ ಚಿಕಿತ್ಸಾ ಹಂತಗಳನ್ನು ಸ್ವೀಕರಿಸಿ.",
    scan_title: "🔬 ಎಲೆಯ ಚಿತ್ರವನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ", upload_prompt: "ನಿಮ್ಮ ಎಲೆಯ ಚಿತ್ರವನ್ನು ಇಲ್ಲಿ ಬಿಡಿ ಅಥವಾ ಅಪ್‌ಲೋಡ್ ಮಾಡಲು ಕ್ಲಿಕ್ ಮಾಡಿ",
    remove_img: "✕ ಚಿತ್ರವನ್ನು ತೆಗೆದುಹಾಕಿ", select_cure_lang: "ಚಿಕಿತ್ಸೆ ಭಾಷೆಯನ್ನು ಆರಿಸಿ", scan_btn: "🔍 ಈಗ ಸ್ಕ್ಯಾನ್ ಮಾಡಿ", upload_first: "ಮೊದಲು ಚಿತ್ರವನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ",
    results_title: "📊 ಪತ್ತೆ ಫಲಿತಾಂಶಗಳು", results_placeholder: "ಎಲೆಯ ಚಿತ್ರವನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ ಮತ್ತು ಫಲಿತಾಂಶಗಳನ್ನು ನೋಡಲು 'ಈಗ ಸ್ಕ್ಯಾನ್ ಮಾಡಿ' ಕ್ಲಿಕ್ ಮಾಡಿ.",
    confidence: "ಪತ್ತೆ ವಿಶ್ವಾಸ", detected: "ಪತ್ತೆಯಾಗಿದೆ", treatment: "💊 ಶಿಫಾರಸು ಮಾಡಿದ ಚಿಕಿತ್ಸೆ", prevention: "🛡️ ಮುನ್ನೆಚ್ಚರಿಕೆ ಕ್ರಮಗಳು",
    pesticides: "🧪 ಶಿಫಾರಸು ಮಾಡಿದ ಕೀಟನಾಶಕಗಳು", view_summary: "ಸಾರಾಂಶವನ್ನು ವೀಕ್ಷಿಸಿ →", scan_complete: "ಸ್ಕ್ಯಾನ್ ಪೂರ್ಣಗೊಂಡಿದೆ! 🌿",
    saved_history: "ನಿಮ್ಮ ವರದಿಯನ್ನು ನಿಮ್ಮ ಇತಿಹಾಸಕ್ಕೆ ಉಳಿಸಲಾಗಿದೆ.", scan_summary: "🗒️ ಸ್ಕ್ಯಾನ್ ಸಾರಾಂಶ",
    scan_another: "🔍 ಇನ್ನೊಂದನ್ನು ಸ್ಕ್ಯಾನ್ ಮಾಡಿ", dashboard: "🏠 ಡ್ಯಾಶ್‌ಬೋರ್ಡ್", listening: "ಕೇಳಿಸಿಕೊಳ್ಳುತ್ತಿದೆ...", speak_res: "🔊 ಫಲಿತಾಂಶಗಳನ್ನು ಓದಿ",
    voice_assistant: "ಧ್ವನಿ ಸಹಾಯಕ", assistant_desc: "ನಿಮಗೆ ನ್ಯಾವಿಗೇಟ್ ಮಾಡಲು ಮತ್ತು ಫಲಿತಾಂಶಗಳನ್ನು ಓದಲು ನಾನು ಸಹಾಯ ಮಾಡಬಲ್ಲೆ.",
    status_ready: "ಆಜ್ಞೆಗಳಿಗಾಗಿ ಸಿದ್ಧವಾಗಿದೆ...", status_listening: "ನಾನು ಕೇಳಿಸಿಕೊಳ್ಳುತ್ತಿದ್ದೇನೆ...", status_error: "ಮೈಕ್ರೊಫೋನ್ ದೋಷ.",
    high: "ಹೆಚ್ಚು", medium: "ಮಧ್ಯಮ", low: "ಕಡಿಮೆ", status: "ಸ್ಥಿತಿ", saved: "ಉಳಿಸಲಾಗಿದೆ ✓", try: "ಪ್ರಯತ್ನಿಸಿ:",
    cmd_scan: "ಈಗ ಸ್ಕ್ಯಾನ್ ಮಾಡಿ", cmd_home: "ಮುಖಪುಟಕ್ಕೆ ಹೋಗಿ", cmd_read: "ಫಲಿತಾಂಶಗಳನ್ನು ಓದಿ",
    btn_stop_listen: "⏹ ಕೇಳುವುದನ್ನು ನಿಲ್ಲಿಸಿ", btn_start_listen: "🎤 ಕೇಳಲು ಪ್ರಾರಂಭಿಸಿ", err_stt: "ಧ್ವನಿ ಗುರುತಿಸುವಿಕೆ ಬೆಂಬಲಿತವಾಗಿಲ್ಲ.",
    err_email: "ಮಾನ್ಯವಾದ ಇಮೇಲ್ ನಮೂದಿಸಿ.", err_pass: "ಪಾಸ್ವರ್ಡ್ 6+ ಅಕ್ಷರಗಳಿರಬೇಕು.", err_name: "ಪೂರ್ಣ ಹೆಸರು ಅಗತ್ಯವಿದೆ.",
    err_confirm: "ಪಾಸ್ವರ್ಡ್‌ಗಳು ಹೊಂದಿಕೆಯಾಗುತ್ತಿಲ್ಲ.", err_auth: "ದೃಢೀಕರಣ ವಿಫಲವಾಗಿದೆ.", err_server: "ಸರ್ವರ್ ತಲುಪಲಾಗುತ್ತಿಲ್ಲ. ಬ್ಯಾಕೆಂಡ್ ಚಾಲನೆಯಲ್ಲಿದೆಯೇ?",
    err_scan: "ಚಿತ್ರವನ್ನು ವಿಶ್ಲೇಷಿಸಲು ವಿಫಲವಾಗಿದೆ."
  },
  Telugu: {
    how: "ఇది ఎలా పనిచేస్తుంది", scan: "స్కానర్", summary: "సారాంశం", welcome: "గుర్తించండి. నిర్ధారణ చేయండి. నయం చేయండి.",
    tagline: "రైతుల కోసం AI- ఆధారిత మొక్కల వ్యాధి గుర్తింపు - వేగంగా, ఖచ్చితంగా మరియు బహుభాషా.",
    login: "లాగిన్", signup: "సైన్ అప్", create: "ఖాతాను సృష్టించండి", name: "పూర్తి పేరు", email: "ఈమెయిల్ చిరునామా", pass: "పాస్వర్డ్", confirm: "పాస్వర్డ్ను నిర్ధారించండి",
    lang: "ఇష్టపడే భాష", processing: "ప్రాసెసింగ్...", start: "స్కానింగ్ ప్రారంభించండి →",
    hero_title: "LeafAI ఎలా పనిచేస్తుంది", hero_desc: "AI శక్తితో మీ పంటలను రక్షించడానికి సాధారణ దశలు.",
    step1_title: "అప్‌లోడ్ లేదా క్యాప్చర్", step1_desc: "మీ పరికరం నుండి మొక్క ఆకు యొక్క స్పష్టమైన ఫోటోను అప్‌లోడ్ చేయండి లేదా కెమెరాను ఉపయోగించండి.",
    step2_title: "AI విశ్లేషణ", step2_desc: "మా AI మోడల్ ఆకును స్కాన్ చేస్తుంది మరియు నిజ సమయంలో వ్యాధిని గుర్తిస్తుంది.",
    step3_title: "నివారణ మరియు మార్గదర్శకత్వం పొందండి", step3_desc: "వాయిస్ అసిస్టెన్స్ మద్దతుతో AI-ఉత్పత్తి చేసిన చికిత్స దశలను పొందండి.",
    scan_title: "🔬 ఆకు చిత్రాన్ని అప్‌లోడ్ చేయండి", upload_prompt: "మీ ఆకు చిత్రాన్ని ఇక్కడ వదలండి లేదా అప్‌లోడ్ చేయడానికి క్లిక్ చేయండి",
    remove_img: "✕ చిత్రాన్ని తీసివేయి", select_cure_lang: "నివారణ భాషను ఎంచుకోండి", scan_btn: "🔍 ఇప్పుడే స్కాన్ చేయండి", upload_first: "ముందుగా చిత్రాన్ని అప్‌లోడ్ చేయండి",
    results_title: "📊 గుర్తింపు ఫలితాలు", results_placeholder: "ఆకు చిత్రాన్ని అప్‌లోడ్ చేయండి మరియు ఫలితాలను చూడటానికి 'ఇప్పుడే స్కాన్ చేయండి' క్లిక్ చేయండి.",
    confidence: "గుర్తింపు విశ్వాసం", detected: "గుర్తించబడింది", treatment: "💊 సిఫార్సు చేసిన చికిత్స", prevention: "🛡️ నివారణ చర్యలు",
    pesticides: "🧪 సిఫార్సు చేసిన పురుగుమందులు", view_summary: "సారాంశాన్ని వీక్షించండి →", scan_complete: "స్కాన్ పూర్తయింది! 🌿",
    saved_history: "మీ నివేదిక మీ చరిత్రలో సేవ్ చేయబడింది.", scan_summary: "🗒️ స్కాన్ సారాంశం",
    scan_another: "🔍 మరొకటి స్కాన్ చేయండి", dashboard: "🏠 డాష్‌బోర్డ్", listening: "వినడం జరుగుతోంది...", speak_res: "🔊 ఫలితాలను చదవండి",
    voice_assistant: "వాయిస్ అసిస్టెంట్", assistant_desc: "నేను మీకు నావిగేట్ చేయడానికి మరియు ఫలితాలను చదవడానికి సహాయం చేయగలను.",
    status_ready: "కమాండ్‌ల కోసం సిద్ధంగా ఉంది...", status_listening: "నేను వింటున్నాను...", status_error: "మైక్రోఫోన్ లోపం.",
    high: "అధిక", medium: "మధ్యస్థ", low: "తక్కువ", status: "స్థితి", saved: "సేవ్ చేయబడింది ✓", try: "ప్రయ్నించండి:",
    cmd_scan: "ఇప్పుడే స్కాన్ చేయండి", cmd_home: "హోమ్‌కు వెళ్లండి", cmd_read: "ఫలితాలను చదవండి",
    btn_stop_listen: "⏹ వినడం ఆపండి", btn_start_listen: "🎤 వినడం ప్రారంభించండి", err_stt: "స్పీచ్ రికగ్నిషన్ సపోర్ట్ చేయబడదు.",
    err_email: "చెల్లుబాటు అయ్యే ఇమెయిల్ నమోదు చేయండి.", err_pass: "పాస్‌వర్డ్ 6+ అక్షరాలు ఉండాలి.", err_name: "పూర్తి పేరు అవసరం.",
    err_confirm: "పాస్‌వర్డ్‌లు సరిపోలడం లేదు.", err_auth: "ధృవీకరణ విఫలమైంది.", err_server: "సర్వర్ అందుబాటులో లేదు. బ్యాకెండ్ నడుస్తుందా?",
    err_scan: "చిత్రాన్ని విశ్లేషించడంలో విఫలమైంది."
  },
  Tamil: {
    how: "இது எப்படி வேலை செய்கிறது", scan: "ஸ்கேனர்", summary: "சுருக்கம்", welcome: "கண்டறியவும். கண்டறியவும். குணப்படுத்தவும்.",
    tagline: "விவசாயிகளுக்கான AI-இயங்கும் தாவர நோய் கண்டறிதல் - வேகமான, துல்லியமான மற்றும் பன்மொழி.",
    login: "உள்நுழைக", signup: "பதிவு செய்க", create: "கணக்கை உருவாக்கு", name: "முழு பெயர்", email: "மின்னஞ்சல் முகவரி", pass: "கடவுச்சொல்", confirm: "கடவுச்சொல்லை உறுதிப்படுத்தவும்",
    lang: "விருப்பமான மொழி", processing: "செயலாக்கம்...", start: "ஸ்கேனிங்கைத் தொடங்கு →",
    hero_title: "LeafAI எப்படி வேலை செய்கிறது", hero_desc: "AI இன் சக்தியுடன் உங்கள் பயிர்களைப் பாதுகாக்க எளிய வழிமுறைகள்.",
    step1_title: "பதிவேற்றவும் அல்லது பிடிக்கவும்", step1_desc: "உங்கள் சாதனத்திலிருந்து தாவர இலையின் தெளிவான புகைப்படத்தைப் பதிவேற்றவும் அல்லது கேமராவைப் பயன்படுத்தவும்.",
    step2_title: "AI பகுப்பாய்வு", step2_desc: "எங்கள் AI மாதிரி இலையை ஸ்கேன் செய்து நிகழ்நேரத்தில் நோயைக் கண்டறியும்.",
    step3_title: "நிவாரணம் மற்றும் வழிகாட்டுதலைப் பெறுங்கள்", step3_desc: "குரல் உதவியுடன் AI-உருவாக்கிய சிகிச்சை படிகளைப் பெறுங்கள்.",
    scan_title: "🔬 இலை படத்தைப் பதிவேற்றவும்", upload_prompt: "உங்கள் இலை படத்தை இங்கே விடவும் அல்லது பதிவேற்ற கிளிக் செய்யவும்",
    remove_img: "✕ படத்தை அகற்று", select_cure_lang: "நிவாரண மொழியைத் தேர்ந்தெடுக்கவும்", scan_btn: "🔍 இப்போது ஸ்கேன் செய்", upload_first: "முதலில் ஒரு படத்தைப் பதிவேற்றவும்",
    results_title: "📊 கண்டறிதல் முடிவுகள்", results_placeholder: "இலை படத்தைப் பதிவேற்றி, முடிவுகளைப் பார்க்க 'இப்போது ஸ்கேன் செய்' என்பதைக் கிளிக் செய்யவும்.",
    confidence: "கண்டறிதல் நம்பிக்கை", detected: "கண்டறியப்பட்டது", treatment: "💊 பரிந்துரைக்கப்பட்ட சிகிச்சை", prevention: "🛡️ தடுப்பு நடவடிக்கைகள்",
    pesticides: "🧪 பரிந்துரைக்கப்பட்ட பூச்சிக்கொல்லிகள்", view_summary: "சுருக்கத்தைக் காண்க →", scan_complete: "ஸ்கேன் முடிந்தது! 🌿",
    saved_history: "உங்கள் அறிக்கை உங்கள் வரலாற்றில் சேமிக்கப்பட்டது.", scan_summary: "🗒️ ஸ்கேன் சுருக்கம்",
    scan_another: "🔍 இன்னொன்றை ஸ்கேன் செய்", dashboard: "🏠 டாஷ்போர்டு", listening: "கவனித்துக் கொண்டிருக்கிறேன்...", speak_res: "🔊 முடிவுகளைப் படிக்கவும்",
    voice_assistant: "குரல் உதவியாளர்", assistant_desc: "நான் உங்களுக்கு வழிகாட்டவும் முடிவுகளைப் படிக்கவும் உதவ முடியும்.",
    status_ready: "கட்டளைகளுக்கு தயார்...", status_listening: "நான் கேட்டுக்கொண்டிருக்கிறேன்...", status_error: "மைக்ரோஃபோன் பிழை.",
    high: "அதிகம்", medium: "நடுத்தரம்", low: "குறைவு", status: "நிலை", saved: "சேமிக்கப்பட்டது ✓", try: "முயற்சி செய்க:",
    cmd_scan: "இப்போது ஸ்கேன் செய்", cmd_home: "முகப்புக்குச் செல்", cmd_read: "முடிவுகளைப் படிக்கவும்",
    btn_stop_listen: "⏹ கேட்பதை நிறுத்து", btn_start_listen: "🎤 கேட்கத் தொடங்கு", err_stt: "பேச்சு அங்கீகாரம் ஆதரிக்கப்படவில்லை.",
    err_email: "சரியான மின்னஞ்சலை உள்ளிடவும்.", err_pass: "கடவுச்சொல் 6+ எழுத்துகளாக இருக்க வேண்டும்.", err_name: "முழு பெயர் தேவை.",
    err_confirm: "கடவுச்சொற்கள் பொருந்தவில்லை.", err_auth: "அங்கீகாரம் தோல்வியடைந்தது.", err_server: "சர்வரை அணுக முடியவில்லை. பின்தளம் இயங்குகிறதா?",
    err_scan: "படத்தை பகுப்பாய்வு செய்யத் தவறிவிட்டது."
  }
};

/* ─── Simple Router ─────────────────────────────────────── */
function useRouter() {
  const [path, setPath] = useState(window.location.hash || '#/');
  useEffect(() => {
    const onHash = () => setPath(window.location.hash || '#/');
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  }, []);
  const navigate = useCallback((to) => { window.location.hash = to; }, []);
  return { path, navigate };
}

/* ─── Navbar ─────────────────────────────────────────────── */
function Navbar({ navigate, path, user, uiLang, setUiLang }) {
  return (
    <nav className="navbar">
      <div className="navbar-logo" onClick={() => navigate('#/')} id="nav-logo">
        Leaf<span>AI</span>
      </div>
      <div className="navbar-links">
        <a id="nav-how" onClick={() => navigate('#/how-it-works')} style={{color: path==='#/how-it-works'?'#fefae0':undefined}}>How It Works</a>
        <a id="nav-scan" onClick={() => navigate('#/scanner')} style={{color: path==='#/scanner'?'#fefae0':undefined}}>Scanner</a>
        <a id="nav-ty" onClick={() => navigate('#/thankyou')} style={{color: path==='#/thankyou'?'#fefae0':undefined}}>Summary</a>
        {user && <span className="user-badge" style={{color: 'white', background: 'rgba(255,255,255,0.1)', padding: '0.3rem 0.8rem', borderRadius: '20px', fontSize: '0.85rem'}}>👤 {user.name}</span>}
      </div>
    </nav>
  );
}

/* ─── Fade-In Hook ───────────────────────────────────────── */
function useFadeIn() {
  useEffect(() => {
    const sections = document.querySelectorAll('.fade-in-section');
    const observer = new IntersectionObserver(
      entries => entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); }),
      { threshold: 0.15 }
    );
    sections.forEach(s => observer.observe(s));
    return () => observer.disconnect();
  }, []);
}

/* ════════════════════════════════════════════════════════════
   PAGE 1 — AUTH
   (Modified to call backend /api/auth/...)
   Localized: Yes
════════════════════════════════════════════════════════════ */
function AuthPage({ navigate, setUser, uiLang, setUiLang }) {
  const t = TRANSLATIONS[uiLang];
  const [tab, setTab] = useState('login');
  const [form, setForm] = useState({ name:'', email:'', pass:'', confirm:'', lang: uiLang });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => { setForm(f => ({...f, lang: uiLang})); }, [uiLang]);

  const set = (k, v) => setForm(f => ({...f, [k]: v}));

  const validateLogin = () => {
    const e = {};
    if (!form.email.includes('@')) e.email = t.err_email;
    if (form.pass.length < 6) e.pass = t.err_pass;
    return e;
  };
  const validateSignup = () => {
    const e = validateLogin();
    if (!form.name.trim()) e.name = t.err_name;
    if (form.pass !== form.confirm) e.confirm = t.err_confirm;
    return e;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const errs = tab === 'login' ? validateLogin() : validateSignup();
    if (Object.keys(errs).length) { setErrors(errs); return; }
    
    setLoading(true);
    try {
      const endpoint = tab === 'login' ? '/auth/login' : '/auth/signup';
      const body = tab === 'login' 
        ? { email: form.email, password: form.pass }
        : { name: form.name, email: form.email, password: form.pass, language: form.lang };

      const res = await fetch(API_BASE + endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      const data = await res.json();

      if (res.ok) {
        localStorage.setItem('leafai_user', JSON.stringify(data.user));
        setUser(data.user);
        if (data.user.language) setUiLang(data.user.language);
        navigate('#/how-it-works');
      } else {
        setErrors({ server: data.error || t.err_auth });
      }
    } catch (err) {
      setErrors({ server: t.err_server });
    } finally {
      setLoading(false);
    }
  };

  const Field = ({ id, label, type='text', k, placeholder='' }) => (
    <div className="form-group">
      <label htmlFor={id}>{label}</label>
      <input id={id} type={type} placeholder={placeholder}
        value={form[k]} onChange={ev => { set(k, ev.target.value); setErrors(er => ({...er, [k]: undefined})); }}
        className={errors[k] ? 'error' : ''} />
      {errors[k] && <div className="error-msg">{errors[k]}</div>}
    </div>
  );

  return (
    <div className="auth-layout page-enter">
      <div className="auth-left">
        <div className="float-leaf" /><div className="float-leaf" /><div className="float-leaf" /><div className="float-leaf" />
        <div className="auth-left-content">
          <div className="auth-brand">Leaf<span>AI</span></div>
          <div className="auth-tagline">{t.welcome}</div>
          <div className="auth-plant-art">
            <div className="leaf-art">
              <div className="leaf leaf-1" />
              <div className="leaf leaf-2" />
              <div className="leaf leaf-3" />
              <div className="leaf leaf-4" />
              <div className="stem" />
            </div>
          </div>
          <p style={{color:'rgba(149,213,178,0.7)',fontSize:'0.9rem',lineHeight:1.6,maxWidth:280}}>
            {t.tagline}
          </p>
        </div>
      </div>

      <div className="auth-right">
        <div className="auth-card">
          <div className="auth-tabs">
            <button id="tab-login" className={`auth-tab ${tab==='login'?'active':''}`} onClick={() => { setTab('login'); setErrors({}); }}>{t.login}</button>
            <button id="tab-signup" className={`auth-tab ${tab==='signup'?'active':''}`} onClick={() => { setTab('signup'); setErrors({}); }}>{t.signup}</button>
          </div>

          <form onSubmit={handleSubmit} noValidate>
            {errors.server && <div className="error-msg" style={{marginBottom:'1rem',textAlign:'center'}}>{errors.server}</div>}
            {tab === 'signup' && <Field id="f-name" label={t.name} k="name" placeholder={uiLang === 'Hindi' ? "प्रिया पाटिल" : "Priya Patil"} />}
            <Field id="f-email" label={t.email} type="email" k="email" placeholder="you@example.com" />
            <Field id="f-pass" label={t.pass} type="password" k="pass" placeholder="••••••••" />
            {tab === 'signup' && <>
              <Field id="f-confirm" label={t.confirm} type="password" k="confirm" placeholder="••••••••" />
              <div className="form-group">
                <label htmlFor="f-lang">{t.lang}</label>
                <select id="f-lang" value={form.lang} onChange={e => { set('lang', e.target.value); setUiLang(e.target.value); }}>
                  {Object.keys(TRANSLATIONS).map(l => <option key={l}>{l}</option>)}
                </select>
              </div>
            </>}
            <button id="btn-submit-auth" type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? t.processing : (tab === 'login' ? `🌿 ${t.login}` : `🌱 ${t.create}`)}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

/* ════════════════════════════════════════════════════════════
   PAGE 2 — HOW IT WORKS
════════════════════════════════════════════════════════════ */
function HowItWorksPage({ navigate, path, user, uiLang, setUiLang }) {
  const t = TRANSLATIONS[uiLang];
  useFadeIn();

  const steps = [
    { icon:'📷', title: t.step1_title, desc: t.step1_desc },
    { icon:'🧠', title: t.step2_title, desc: t.step2_desc },
    { icon:'🌿', title: t.step3_title, desc: t.step3_desc },
  ];

  return (
    <div className="page-enter">
      <Navbar navigate={navigate} path={path} user={user} uiLang={uiLang} setUiLang={setUiLang} />

      <section className="how-hero">
        <h1>{t.hero_title}</h1>
        <p>{t.hero_desc}</p>
      </section>

      <section className="steps-section">
        <div className="steps-container fade-in-section">
          {steps.map((s, i) => (
            <React.Fragment key={i}>
              <div className="step-card">
                <div className="step-num">{i+1}</div>
                <div className="step-icon">{s.icon}</div>
                <h3>{s.title}</h3>
                <p>{s.desc}</p>
              </div>
              {i < steps.length-1 && <div className="steps-connector">→</div>}
            </React.Fragment>
          ))}
        </div>
      </section>

      <div className="how-cta fade-in-section">
        <button id="btn-start-scanning" className="btn btn-earth" onClick={() => navigate('#/scanner')}>
          {t.start}
        </button>
      </div>
    </div>
  );
}

/* ════════════════════════════════════════════════════════════
   PAGE 3 — SCANNER
   Localized: Yes
════════════════════════════════════════════════════════════ */
function ScannerPage({ navigate, path, user, setLastScan, uiLang, setUiLang }) {
  const t = TRANSLATIONS[uiLang];
  const [image, setImage] = useState(null);
  const [imageFile, setImageFile] = useState(null);
  const [scanning, setScanning] = useState(false);
  const [results, setResults] = useState(null);
  const [lang, setLang] = useState(uiLang);
  const [barWidth, setBarWidth] = useState(0);
  const [error, setError] = useState(null);
  const fileRef = useRef();

  useEffect(() => { setLang(uiLang); }, [uiLang]);

  const handleFile = (file) => {
    if (!file || !file.type.startsWith('image/')) return;
    setImageFile(file);
    const reader = new FileReader();
    reader.onload = e => setImage(e.target.result);
    reader.readAsDataURL(file);
    setResults(null); setBarWidth(0); setError(null);
  };

  const handleDrop = (e) => { e.preventDefault(); handleFile(e.dataTransfer.files[0]); };

  const handleScan = async () => {
    if (!imageFile) return;
    setScanning(true); setResults(null); setBarWidth(0); setError(null);

    const formData = new FormData();
    formData.append('image', imageFile);
    formData.append('language', lang);
    if (user?._id) formData.append('user_id', user._id);

    try {
      const res = await fetch(API_BASE + '/predict', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();

      if (res.ok) {
        setResults(data);
        setLastScan(data);
        setTimeout(() => setBarWidth(data.confidence * 100), 100);
      } else {
        setError(data.error || t.err_scan);
      }
    } catch (err) {
      setError(t.err_server);
    } finally {
      setScanning(false);
    }
  };

  const confLevel = barWidth >= 75 ? 'high' : barWidth >= 50 ? 'medium' : 'low';
  const fillClass = confLevel === 'high' ? '' : confLevel === 'medium' ? 'medium' : 'low';

  return (
    <div className="scanner-page page-enter">
      <Navbar navigate={navigate} path={path} user={user} uiLang={uiLang} setUiLang={setUiLang} />

      <div className="scanner-container">
        <div className="scanner-panel">
          <h2>{t.scan_title}</h2>

          <div
            id="upload-zone"
            className={`upload-zone ${scanning ? 'scan-anim-wrapper' : ''}`}
            onClick={() => !image && fileRef.current.click()}
            onDrop={handleDrop}
            onDragOver={e => e.preventDefault()}
          >
            {scanning && <div className="scan-line" />}
            {image ? (
              <img src={image} alt="Uploaded leaf" onClick={() => fileRef.current.click()} />
            ) : (
              <>
                <div className="upload-icon">🍃</div>
                <p>{t.upload_prompt}</p>
              </>
            )}
            <input ref={fileRef} type="file" accept="image/*"
              onChange={e => handleFile(e.target.files[0])} />
          </div>

          {image && !scanning && (
            <button style={{marginTop:'0.5rem',fontSize:'0.8rem',background:'none',border:'none',color:'#e63946',cursor:'pointer'}}
              onClick={() => { setImage(null); setImageFile(null); setResults(null); setBarWidth(0); }}>
              {t.remove_img}
            </button>
          )}

          <div className="lang-selector">
            <label htmlFor="cure-lang">{t.select_cure_lang}</label>
            <select id="cure-lang" value={lang} onChange={e => setLang(e.target.value)}>
              {Object.keys(TRANSLATIONS).map(l => <option key={l} value={l}>{l}</option>)}
            </select>
          </div>

          {scanning && (
            <div className="spinner-wrap">
              <div className="spinner" />
              <p style={{marginTop:'1rem',color:'var(--green-mid)',fontWeight:600}}>{t.processing}</p>
            </div>
          )}

          {error && <div className="error-msg" style={{marginTop:'1rem'}}>{error}</div>}

          {!scanning && (
            <button id="btn-scan-now" className="btn btn-primary" style={{marginTop:'1.5rem',width:'100%',justifyContent:'center'}}
              onClick={handleScan} disabled={!image}>
              {image ? t.scan_btn : t.upload_first}
            </button>
          )}
        </div>

        {results && (
          <div className="scanner-panel">
            <h2>{t.results_title}</h2>
            <div className="confidence-bar-wrap">
              <label>{t.confidence}</label>
              <div className="confidence-track">
                <div className={`confidence-fill ${fillClass}`} style={{width: barWidth+'%'}} />
              </div>
              <div style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}>
                <span className="confidence-pct" style={{color: confLevel==='high'?'var(--green-mid)':confLevel==='medium'?'var(--earth)':'#e63946'}}>
                  {Math.round(barWidth)}% — {confLevel === 'high' ? `✅ ${t.high}` : confLevel === 'medium' ? `⚠️ ${t.medium}` : `❌ ${t.low}`}
                </span>
              </div>
              <div className="disease-name">{t.detected}: {results.disease}</div>
            </div>

            <div className="treatment-card" id="treatment-report">
              <h3>{t.treatment}</h3>
              <p style={{fontSize:'0.9rem',marginBottom:'1rem',fontStyle:'italic'}}>{results.cure.description}</p>
              <ol>
                {results.cure.treatment_steps.map((s, i) => (
                  <li key={i}><strong>{s.title}</strong>: {s.detail}</li>
                ))}
              </ol>
              <div className="preventive-section">
                <h4>{t.prevention}</h4>
                <ul>
                  {results.cure.prevention.map((p, i) => <li key={i}>{p}</li>)}
                </ul>
              </div>
            </div>

            <div style={{marginTop:'1.5rem',textAlign:'center'}}>
              <button id="btn-go-summary" className="btn btn-earth" onClick={() => navigate('#/thankyou')}>
                {t.view_summary}
              </button>
            </div>
          </div>
        )}

        {!results && !scanning && (
          <div className="scanner-panel" style={{textAlign:'center',padding:'3rem',color:'var(--text-light)'}}>
            <div style={{fontSize:'3rem'}}>🌱</div>
            <p style={{marginTop:'1rem'}}>{t.results_placeholder}</p>
          </div>
        )}
      </div>
      <VoiceAssistant uiLang={uiLang} results={results} handleScan={handleScan} navigate={navigate} />
    </div>
  );
}

/* ════════════════════════════════════════════════════════════
   PAGE 4 — THANK YOU
   Localized: Yes
════════════════════════════════════════════════════════════ */
const CONFETTI = ['🍃','🌿','🍀','🌱','🪴'];

function ThankYouPage({ navigate, path, user, lastScan, uiLang, setUiLang }) {
  const t = TRANSLATIONS[uiLang];
  const leaves = Array.from({length: 15}, (_, i) => ({
    id: i, emoji: CONFETTI[i % CONFETTI.length], left: Math.random() * 100,
    delay: Math.random() * 5, dur: 4 + Math.random() * 4, size: 0.8 + Math.random() * 0.8,
  }));

  return (
    <div className="page-enter" style={{position:'relative',overflow:'hidden'}}>
      <Navbar navigate={navigate} path={path} user={user} uiLang={uiLang} setUiLang={setUiLang} />
      {leaves.map(l => (
        <div key={l.id} className="confetti-leaf" style={{
          left: l.left+'%', fontSize: l.size+'rem', animationDuration: l.dur+'s', animationDelay: l.delay+'s',
        }}>{l.emoji}</div>
      ))}

      <div className="ty-page">
        <svg className="checkmark-svg" viewBox="0 0 100 100">
          <circle className="checkmark-circle" cx="50" cy="50" r="45" />
          <polyline className="checkmark-check" points="28,52 44,68 72,36" />
        </svg>

        <h1>{t.scan_complete}</h1>
        <p className="subtitle">{t.saved_history}</p>

        {lastScan ? (
          <div className="summary-card">
            <h3>{t.scan_summary}</h3>
            {[
              [t.detected, lastScan.disease],
              [t.confidence, (lastScan.confidence * 100).toFixed(1) + '%'],
              [t.lang, lastScan.cure?._meta?.source_language || uiLang],
              [t.status, t.saved],
            ].map(([l, v]) => (
              <div className="summary-row" key={l}>
                <span className="summary-label">{l}</span>
                <span className="summary-value">{v}</span>
              </div>
            ))}
          </div>
        ) : (
          <div className="summary-card">{t.results_placeholder}</div>
        )}

        <div className="ty-buttons">
          <button className="btn btn-primary" onClick={() => navigate('#/scanner')}>{t.scan_another}</button>
          <button className="btn btn-outline" onClick={() => navigate('#/how-it-works')}>{t.dashboard}</button>
        </div>
      </div>
    </div>
  );
}

/* ════════════════════════════════════════════════════════════
   VOICE ASSISTANT COMPONENT
   Localized: Yes
════════════════════════════════════════════════════════════ */
function VoiceAssistant({ uiLang, results, handleScan, navigate }) {
  const t = TRANSLATIONS[uiLang];
  const [isOpen, setIsOpen] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [status, setStatus] = useState(t.status_ready);
  const recognitionRef = useRef(null);

  useEffect(() => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      setStatus(t.err_stt);
      return;
    }
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognitionRef.current = new SpeechRecognition();
    recognitionRef.current.continuous = false;
    recognitionRef.current.interimResults = false;
    
    const langMap = { 'Hindi': 'hi-IN', 'Kannada': 'kn-IN', 'Marathi': 'mr-IN', 'English': 'en-US', 'Tamil': 'ta-IN', 'Telugu': 'te-IN' };
    recognitionRef.current.lang = langMap[uiLang] || 'en-US';

    recognitionRef.current.onstart = () => { setIsListening(true); setStatus(t.status_listening); };
    recognitionRef.current.onend = () => { setIsListening(false); setStatus(t.status_ready); };
    recognitionRef.current.onerror = () => { setIsListening(false); setStatus(t.status_error); };
    
    recognitionRef.current.onresult = (event) => {
      const command = event.results[0][0].transcript.toLowerCase();
      processCommand(command);
    };
  }, [uiLang, t]);

  const processCommand = (cmd) => {
    console.log("Voice Command:", cmd);
    // Multilingual command matching
    const isScan = cmd.includes('scan') || cmd.includes('स्कॅन') || cmd.includes('स्कैन') || cmd.includes('ಸ್ಕ್ಯಾನ್') || cmd.includes('స్కాన్') || cmd.includes('ஸ்கேன்');
    const isHome = cmd.includes('home') || cmd.includes('dashboard') || cmd.includes('मुख्य') || cmd.includes('ಮುಖಪುಟ') || cmd.includes('హోమ్') || cmd.includes('முகப்பு');
    const isRead = cmd.includes('read') || cmd.includes('वाच') || cmd.includes('पढ़ो') || cmd.includes('ಓದಿ') || cmd.includes('చదవండి') || cmd.includes('படிக்க');
    const isStop = cmd.includes('stop') || cmd.includes('थांब') || cmd.includes('रुको') || cmd.includes('ನಿಲ್ಲಿಸು') || cmd.includes('ఆపు') || cmd.includes('நிறுத்து');

    if (isScan) {
      if (window.location.hash === '#/scanner') handleScan();
      else navigate('#/scanner');
    } else if (isHome) {
      navigate('#/how-it-works');
    } else if (isRead) {
      speakResults();
    } else if (isStop) {
      window.speechSynthesis.cancel();
    }
  };

  const speakResults = () => {
    if (!results || !('speechSynthesis' in window)) return;
    const reportText = `${results.disease}. ${results.cure.description}. ${results.cure.treatment_steps.map(s => s.title + ': ' + s.detail).join('. ')}`;
    const utterance = new SpeechSynthesisUtterance(reportText);
    const langMap = { 'Hindi': 'hi-IN', 'Kannada': 'kn-IN', 'Marathi': 'mr-IN', 'English': 'en-US', 'Tamil': 'ta-IN', 'Telugu': 'te-IN' };
    utterance.lang = langMap[uiLang] || 'en-US';
    window.speechSynthesis.speak(utterance);
  };

  const toggleListen = () => {
    if (isListening) recognitionRef.current.stop();
    else recognitionRef.current.start();
  };

  return (
    <>
      <div className="mic-label">{t.voice_assistant}</div>
      <button className={`mic-fab ${isListening ? 'pulsing' : ''}`} onClick={() => setIsOpen(!isOpen)}>
        🎙️
      </button>

      {isOpen && (
        <div className="voice-popup">
          <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:'1rem'}}>
            <h4 style={{margin:0}}>🎙️ {t.voice_assistant}</h4>
            <button onClick={() => setIsOpen(false)} style={{background:'none',border:'none',cursor:'pointer'}}>✕</button>
          </div>
          <p style={{fontSize:'0.8rem',color:'#666',marginBottom:'1rem'}}>{t.assistant_desc}</p>
          
          <div className="voice-status-card">
            <div className={`status-dot ${isListening ? 'active' : ''}`} />
            <span>{status}</span>
          </div>

          <div style={{display:'flex',gap:'0.5rem',marginTop:'1rem'}}>
            <button className={`btn ${isListening ? 'btn-earth' : 'btn-primary'}`} style={{flex:1,fontSize:'0.85rem',padding:'0.5rem'}} onClick={toggleListen}>
              {isListening ? t.btn_stop_listen : t.btn_start_listen}
            </button>
            {results && (
              <button className="btn btn-outline" style={{flex:1,fontSize:'0.85rem',padding:'0.5rem'}} onClick={speakResults}>
                {t.speak_res}
              </button>
            )}
          </div>
          
          <div className="voice-commands-hint">
            <strong>{t.try}</strong> "{t.cmd_scan}", "{t.cmd_home}", "{t.cmd_read}"
          </div>
        </div>
      )}
    </>
  );
}

/* ════════════════════════════════════════════════════════════
   ROOT APP
════════════════════════════════════════════════════════════ */
function App() {
  const { path, navigate } = useRouter();
  const [user, setUser] = useState(null);
  const [lastScan, setLastScan] = useState(null);
  const [uiLang, setUiLang] = useState('English');

  useEffect(() => {
    const saved = localStorage.getItem('leafai_user');
    if (saved) {
      const u = JSON.parse(saved);
      setUser(u);
      if (u.language) setUiLang(u.language);
    }
  }, []);

  const commonProps = { navigate, path, user, uiLang, setUiLang };

  const pages = {
    '#/'           : <AuthPage {...commonProps} setUser={setUser} />,
    '#/how-it-works': <HowItWorksPage {...commonProps} />,
    '#/scanner'    : <ScannerPage {...commonProps} setLastScan={setLastScan} />,
    '#/thankyou'   : <ThankYouPage {...commonProps} lastScan={lastScan} />,
  };

  return pages[path] || pages['#/'];
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
