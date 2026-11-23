"""
Clinical Dietary Whole Foods & Nutrition Monographs
Includes WHO 2023 Guidelines (Fiber >= 25g/day, NSS Sweetener restrictions, NOVA UPF guardrails),
African Heritage Staples, and Clinical Safety Metadata.
"""

from typing import Dict, List, Any, Optional

DIETARY_MONOGRAPHS: Dict[str, Dict[str, Any]] = {
    "brown_cowpeas": {
        "common_name": "Brown Cowpeas / Black-Eyed Beans",
        "botanical_name": "Vigna unguiculata",
        "category": "Legume / Heritage Whole Food",
        "who_guideline_category": "Naturally Occurring Dietary Fiber & Complex Carbohydrates (WHO 2023)",
        "nova_classification": "NOVA 1 (Unprocessed or Minimally Processed Food)",
        "key_nutrients": {
            "dietary_fiber_per_100g": "10.6 g",
            "plant_protein_per_100g": "23.5 g",
            "iron_per_100g": "8.3 mg",
            "potassium_per_100g": "1112 mg",
            "magnesium_per_100g": "184 mg",
            "resistant_starch": "High (Promotes butyrate-producing gut microbiome)"
        },
        "bioactive_compounds": [
            "Polyphenolic Anthocyanins",
            "Flavonoids (Quercetin, Kaempferol)",
            "Phytic Acid (Reduced via traditional overnight soaking)",
            "Bowman-Birk Protease Inhibitors"
        ],
        "therapeutic_indications": [
            "Type 2 Diabetes & Insulin Resistance (Low GI ~38, blunts postprandial glucose surges)",
            "Metabolic Syndrome & Dyslipidemia (Reduces LDL-C via bile acid binding)",
            "Hypertension & Endothelial Health (High potassium/sodium ratio)",
            "Nutritional Anemia (Rich non-heme iron source; optimize with Vitamin C synergy)",
            "Gut Microbiome Dysbiosis (High prebiotic fermentable oligosaccharides)"
        ],
        "culinary_preparation_protocols": [
            "Traditional Overnight Soaking: Soak in fresh water for 8-12 hours and discard soak water to degrade raffinose oligosaccharides and phytates by 45%.",
            "Therapeutic Boiling/Steaming: Boil until soft with fresh ginger, onions, and unrefined red palm oil for beta-carotene synergy (e.g. Traditional Ewa Aganyin / Gbegiri / Waakye).",
            "Piped Steamed Cakes (Moi-Moi): Pureed with sweet red bell peppers and onions, steamed with zero artificial seasoning cubes."
        ],
        "contraindications_and_precautions": [
            "Severe Chronic Kidney Disease (Stage 4-5 / Dialysis): Requires potassium restriction or boil-and-drain leached preparation.",
            "Acute Gout Flare-up: Moderate purine content; consume in calibrated portions during active flares.",
            "Severe Irritable Bowel Syndrome (IBS / FODMAP Sensitivity): May induce flatulence; combine with carminative herbs (Ginger, Fennel, Cumin)."
        ]
    },
    "heritage_sorghum_millet": {
        "common_name": "Heritage Sorghum & Pearl Millet",
        "botanical_name": "Sorghum bicolor / Pennisetum glaucum",
        "category": "Gluten-Free Heritage Ancient Grain",
        "who_guideline_category": "Naturally Occurring Dietary Fiber & Whole Grains (WHO 2023)",
        "nova_classification": "NOVA 1 (Unprocessed or Minimally Processed Whole Grain)",
        "key_nutrients": {
            "dietary_fiber_per_100g": "8.5 g",
            "resistant_starch": "High (Slow-digesting carbohydrate matrix)",
            "iron_per_100g": "4.4 mg",
            "zinc_per_100g": "2.1 mg",
            "gluten_free": "100% Naturally Gluten-Free"
        },
        "bioactive_compounds": [
            "3-Deoxyanthocyanidins (Apigeninidin, Luteolinidin)",
            "Condensed Tannins (Proanthocyanidins)",
            "Phenolic Acids (Ferulic, Caffeic, p-Coumaric acids)",
            "Policosanols (Lipid-lowering plant waxes)"
        ],
        "therapeutic_indications": [
            "Type 2 Diabetes & Glycemic Control (Prolonged gastric transit time and low glycemic index)",
            "Celiac Disease & Non-Celiac Gluten Sensitivity (Safe nutrient-dense gluten replacement)",
            "Cardiovascular Disease (Inhibits HMG-CoA reductase and reduces systemic arterial inflammation)",
            "Colorectal Health & Cancer Prevention (Potent cellular antioxidant and butyrate generation)"
        ],
        "culinary_preparation_protocols": [
            "Traditional Lactic Fermentation (Ogi / Pap / Uji / Koko): Ferment soaked whole grains for 24-48 hours with Lactobacillus cultures to bio-activate free phenols and reduce phytates.",
            "Whole Grain Porridge / Swallow (Tuwo / Ugali): Finely milled whole grain boiled in water into smooth dough swallow; pair with mucilaginous okra or vegetable soup.",
            "Popped or Steamed Grains: Cook whole grains in 1:3 water ratio for 35 minutes as nutritious rice alternative."
        ],
        "contraindications_and_precautions": [
            "Endemic Iodine Deficiency: Extremely high raw pearl millet diets without iodine-rich foods may exert weak goitrogenic effects; ensure iodized salt or sea vegetables in diet."
        ]
    },
    "bitter_leaf_vegetable": {
        "common_name": "Bitter Leaf (Culinary Prepared)",
        "botanical_name": "Vernonia amygdalina",
        "category": "Indigenous Leafy Green Vegetable",
        "who_guideline_category": "Dark Green Leafy Vegetables & Bioactive Phytochemicals (WHO 2023)",
        "nova_classification": "NOVA 1 (Minimally Processed Vegetable)",
        "key_nutrients": {
            "dietary_fiber_per_100g": "6.2 g",
            "vitamin_c_per_100g": "166 mg",
            "beta_carotene_per_100g": "15.8 mg",
            "calcium_per_100g": "145 mg"
        },
        "bioactive_compounds": ["Vernodalin", "Vernomygdin", "Luteolin 7-O-glucoside", "Chlorogenic Acid"],
        "therapeutic_indications": [
            "Hepatic Cleansing & Liver Detoxification",
            "Glycemic Regulation (Enhances peripheral glucose utilization)",
            "Hypertension & Mild Diuresis",
            "Gastrointestinal Antimicrobial & Anthelminthic Support"
        ],
        "culinary_preparation_protocols": [
            "Washed Culinary Soup Preparation: Gently squeeze leaves in clean water to reduce extreme bitterness while preserving 70% of therapeutic polyphenols; simmer into traditional vegetable soup with locust beans (Iru / Dawadawa)."
        ],
        "contraindications_and_precautions": [
            "First Trimester Pregnancy: Avoid large raw concentrated extracts (culinary soup portions are safe)."
        ]
    },
    "moringa_leaves": {
        "common_name": "Moringa Oleifera Leaves",
        "botanical_name": "Moringa oleifera",
        "category": "Superfood Leafy Green / Botanical Micronutrient",
        "who_guideline_category": "Micronutrient-Dense Whole Plant (WHO 2023)",
        "nova_classification": "NOVA 1 (Unprocessed Whole Leaves)",
        "key_nutrients": {
            "dietary_fiber_per_100g": "7.9 g",
            "protein_per_100g": "9.4 g",
            "calcium_per_100g": "440 mg",
            "potassium_per_100g": "337 mg",
            "iron_per_100g": "4.0 mg"
        },
        "bioactive_compounds": ["Moringine (Isothiocyanates)", "Quercetin", "Chlorogenic Acid", "Kaempferol"],
        "therapeutic_indications": [
            "Malnutrition & Micronutrient Deficiencies",
            "Metabolic Syndrome & Lipid Oxidation Prevention",
            "Lactation Support (Natural Galactagogue)",
            "Systemic Anti-Inflammatory"
        ],
        "culinary_preparation_protocols": [
            "Fresh Leaf Infusion / Pottage: Add fresh tender leaves to soups, broths, and stews in the last 3-5 minutes of cooking to preserve heat-sensitive Vitamin C and isothiocyanates."
        ],
        "contraindications_and_precautions": [
            "Hypoglycemic Medication: Synergistic blood sugar lowering; monitor blood glucose."
        ]
    },
    "hibiscus_calyces": {
        "common_name": "Hibiscus / Roselle Calyces",
        "botanical_name": "Hibiscus sabdariffa",
        "category": "Culinary Fruit Calyx / Functional Beverage",
        "who_guideline_category": "Naturally Sugar-Free Functional Botanical Beverage (WHO 2023)",
        "nova_classification": "NOVA 1 (Minimally Processed Botanical Beverage)",
        "key_nutrients": {
            "organic_acids": "Hibiscus Acid, Citric Acid, Malic Acid",
            "vitamin_c": "Potent water-soluble antioxidant"
        },
        "bioactive_compounds": ["Delphinidin-3-sambubioside", "Cyanidin-3-sambubioside", "Protocatechuic Acid"],
        "therapeutic_indications": [
            "Stage 1 Hypertension (Natural ACE inhibition & vascular vasodilation)",
            "Urinary Tract Flushes & Renal Health",
            "Cholesterol & Triglyceride Reduction"
        ],
        "culinary_preparation_protocols": [
            "Therapeutic Zobo Brew: Simmer dried calyces in water with fresh ginger rhizome and pineapple rinds; serve unsweetened or sweetened strictly with whole dates or pure raw honey (ZERO non-sugar sweeteners per WHO 2023)."
        ],
        "contraindications_and_precautions": [
            "Severe Hypotension: Avoid consuming more than 1 liter daily.",
            "Concurrent Acetaminophen (Paracetamol): Space out consumption by 2 hours due to hepatic clearance interactions."
        ]
    },
    "ginger_rhizome": {
        "common_name": "Ginger Rhizome",
        "botanical_name": "Zingiber officinale",
        "category": "Culinary Spice & Therapeutic Prokinetic",
        "who_guideline_category": "Functional Whole Spice & Anti-Inflammatory (WHO 2023)",
        "nova_classification": "NOVA 1 (Unprocessed Fresh Root)",
        "key_nutrients": {
            "bioactive_fraction": "6-Gingerol, 6-Shogaol, Zingiberene"
        },
        "bioactive_compounds": ["6-Gingerol", "8-Gingerol", "10-Gingerol", "6-Shogaol", "Zingerone"],
        "therapeutic_indications": [
            "Gastric Motility & Nausea / Dyspepsia (Prokinetic 5-HT3 antagonism)",
            "Osteoarthritis & Musculoskeletal Pain (Inhibits COX-2 & 5-LOX inflammatory cascades)",
            "Peripheral Circulation & Thermogenesis"
        ],
        "culinary_preparation_protocols": [
            "Fresh Root Grated Infusion: Grate 15-20g fresh ginger root into warm soups, teas, and food marinades."
        ],
        "contraindications_and_precautions": [
            "Active Gallstones / Biliary Obstruction: High doses stimulate gallbladder contraction.",
            "High-Dose Anticoagulants (Warfarin): Exercise moderation with large therapeutic extracts."
        ]
    }
}


WHO_2023_DIETARY_GUIDELINES = {
    "dietary_fiber": {
        "recommendation": ">= 25g of naturally occurring dietary fiber daily from whole plant foods (whole grains, legumes, vegetables, and whole fruits)",
        "clinical_rationale": "Strongest evidence-based protection against all-cause mortality, cardiovascular disease, Type 2 Diabetes, and colorectal neoplasia.",
        "prohibited": "Isolated industrial fiber additives do not confer the full bioactive entourage benefit of whole plant cellular matrices."
    },
    "non_sugar_sweeteners_advisory": {
        "who_guideline_2023": "WHO advises against the use of Non-Sugar Sweeteners (NSS) — including aspartame, saccharin, sucralose, acesulfame K, stevia derivatives, and erythritol — for weight control or reducing the risk of noncommunicable diseases.",
        "clinical_rationale": "Systematic review evidence demonstrates no long-term benefit in reducing body fat in adults or children, and potential undesirable long-term risks including increased risk of Type 2 Diabetes, cardiovascular events, and gut microbiome dysbiosis.",
        "clinical_action": "Recommend naturally sweet whole foods (mashed dates, ripe whole fruits) or minimal raw honey in controlled quantities instead of industrial sweeteners."
    },
    "nova_ultra_processed_foods_guardrails": {
        "guideline": "Strictly eliminate or replace NOVA Category 4 (Ultra-Processed Food and Drink Formulations) with Category 1 (Unprocessed or Minimally Processed Whole Foods).",
        "avoid_list": [
            "Commercial bouillon/seasoning cubes high in monosodium glutamate & industrial trans-fats",
            "Refined white flour bakery products with chemical dough conditioners and preservatives",
            "Carbonated sodas, energy drinks, and packaged synthetic juices",
            "Reconstituted meat products with sodium nitrates and phosphates"
        ],
        "substitute_list": [
            "Traditional fermented locust beans (Iru / Dawadawa / Ogiri) for rich savory umami and prebiotic benefit",
            "Cold-pressed virgin coconut oil, unrefined red palm oil, or extra virgin olive oil",
            "Fresh whole culinary aromatics: Allium sativum (Garlic), Allium cepa (Red Onions), Zingiber (Ginger), and Piper guineense (Uziza)"
        ]
    }
}
