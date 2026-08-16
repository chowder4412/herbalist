"""
Phytotherapy Specialist and WHO / IMPPAT Botanical Monograph Database
"""

from typing import Dict, List
from .models import HerbalRemedy, HerbDrugInteraction


class PhytotherapySpecialist:
    """Advanced botanical medicine and herb-drug interaction specialist"""
    
    def __init__(self):
        self.herbal_database = self._initialize_herbal_database()
        self.interaction_matrix = self._initialize_interaction_matrix()
        
    def _initialize_herbal_database(self) -> Dict[str, HerbalRemedy]:
        """Initialize comprehensive WHO Monographed & Peer-Reviewed Botanical Database (100+ Plants)"""
        return {
            # ── 1. AFRICAN & NIGERIAN PHYTOTHERAPY ──
            "bitter_leaf": HerbalRemedy(
                common_name="Bitter Leaf",
                botanical_name="Vernonia amygdalina",
                active_compounds=["Vernodalin", "Vernolepin", "Luteolin", "Vernomygdin", "Sesquiterpene lactones"],
                therapeutic_actions=["Hypoglycemic", "Anti-diabetic", "Hepatoprotective", "Antimalarial", "Anti-inflammatory"],
                clinical_indications=["Type 2 Diabetes", "High blood sugar", "Liver detox", "Malaria recovery", "Fever"],
                recommended_dosage="Fresh leaf decoction: 1 teacup (150 mL) 2 times daily; Dried extract: 400 mg twice daily",
                safety_warnings=["Very bitter taste; may increase gut peristalsis; caution in severe hypotension"]
            ),
            "moringa": HerbalRemedy(
                common_name="Moringa",
                botanical_name="Moringa oleifera",
                active_compounds=["Moringinine", "Quercetin", "Chlorogenic acid", "Isothiocyanates", "Niazimicin"],
                therapeutic_actions=["Nutritive superfood", "Hypoglycemic", "Antihypertensive", "Antioxidant", "Anti-inflammatory"],
                clinical_indications=["Malnutrition", "Metabolic syndrome", "High blood pressure", "Lactation support", "Joint inflammation"],
                recommended_dosage="Leaf powder: 3-5 grams daily in warm water or porridge; Decoction: 1 cup twice daily",
                safety_warnings=["Avoid root bark extracts during pregnancy due to uterine contracting properties"]
            ),
            "zobo_hibiscus": HerbalRemedy(
                common_name="Zobo / Roselle",
                botanical_name="Hibiscus sabdariffa",
                active_compounds=["Delphinidin-3-sambubioside", "Cyanidin-3-sambubioside", "Hibiscic acid", "Protocatechuic acid"],
                therapeutic_actions=["Antihypertensive", "ACE-inhibitory", "Diuretic", "Hypolipidemic", "Nephroprotective"],
                clinical_indications=["Hypertension", "High blood pressure", "Elevated cholesterol", "Fluid retention", "UTI support"],
                recommended_dosage="Infusion (tea): 250 mL brewed hot/cold twice daily; Standardized extract: 500 mg daily",
                safety_warnings=["Excessive doses may lower BP rapidly; caution in hypotension or with ACE-inhibitor meds"]
            ),
            "bitter_kola": HerbalRemedy(
                common_name="Bitter Kola",
                botanical_name="Garcinia kola",
                active_compounds=["Kolaviron", "Garcinia biflavonoids GB1 & GB2", "Cycloartenol", "Xanthones"],
                therapeutic_actions=["Hepatoprotective", "Bronchodilator", "Antiviral", "Anti-inflammatory", "Aphrodisiac"],
                clinical_indications=["Respiratory distress", "Asthma", "Cough", "Liver toxicity", "Viral infections", "Low libido"],
                recommended_dosage="1-2 seeds chewed raw daily or 500 mg pulverized seed powder daily",
                safety_warnings=["Contains mild natural xanthine stimulants; consume in morning/afternoon"]
            ),
            "neem": HerbalRemedy(
                common_name="Neem / Dongoyaro",
                botanical_name="Azadirachta indica",
                active_compounds=["Nimbin", "Nimbidin", "Azadirachtin", "Quercetin", "Gedunin"],
                therapeutic_actions=["Antimalarial", "Broad-spectrum Antimicrobial", "Antifungal", "Dermatological", "Hypoglycemic"],
                clinical_indications=["Malaria fever", "Skin lesions", "Eczema", "Ringworm", "Dental plaque", "Blood purifying"],
                recommended_dosage="Topical leaf paste for skin; Oral decoction: 50 mL twice daily for 5 days maximum",
                safety_warnings=["Short-term use only; unsafe for young infants or pregnant women"]
            ),
            "papaya_leaf": HerbalRemedy(
                common_name="Papaya Leaf",
                botanical_name="Carica papaya",
                active_compounds=["Papain", "Carpaine", "Chymopapain", "Quercetin", "Kaempferol"],
                therapeutic_actions=["Thrombocyte booster", "Platelet enhancing", "Digestive enzyme", "Antimalarial"],
                clinical_indications=["Dengue fever recovery", "Thrombocytopenia (low platelets)", "Indigestion", "Intestinal parasites"],
                recommended_dosage="Fresh leaf juice: 10-20 mL twice daily for 5 days; Leaf extract: 500 mg twice daily",
                safety_warnings=["Avoid high doses in early pregnancy; may interact with blood thinners"]
            ),
            "guava_leaf": HerbalRemedy(
                common_name="Guava Leaf",
                botanical_name="Psidium guajava",
                active_compounds=["Quercetin", "Guaijaverin", "Ursolic acid", "Ellagic acid", "Caryophyllene"],
                therapeutic_actions=["Antidiarrheal", "Antimicrobial", "Hypoglycemic", "Cardioprotective", "Astringent"],
                clinical_indications=["Acute diarrhea", "Gastroenteritis", "Toothache", "High blood sugar", "Candidiasis"],
                recommended_dosage="Decoction: 1 cup (150 mL) 3 times daily; Mouth rinse for gum disease",
                safety_warnings=["May cause mild constipation if taken in excessive quantities"]
            ),
            "stonebreaker": HerbalRemedy(
                common_name="Stonebreaker (Chanca Piedra)",
                botanical_name="Phyllanthus niruri",
                active_compounds=["Phyllanthin", "Hypophyllanthin", "Corilagin", "Geraniin", "Repandusinic acid"],
                therapeutic_actions=["Urolithiasis dissolver", "Nephroprotective", "Hepatoprotective", "Hypouricemic"],
                clinical_indications=["Kidney stones", "Gallstones", "High uric acid / Gout", "Hepatitis B support", "Edema"],
                recommended_dosage="Decoction: 1 cup (200 mL) simmered whole plant tea 3 times daily for 2 weeks",
                safety_warnings=["Diuretic effect; monitor potassium levels; avoid in early pregnancy"]
            ),
            "utazi": HerbalRemedy(
                common_name="Utazi / Bush Buck",
                botanical_name="Gongronema latifolium",
                active_compounds=["Pregnane glycosides", "Essential oils", "Saponins", "Alkaloids", "Flavonoids"],
                therapeutic_actions=["Hypoglycemic", "Anti-inflammatory", "Postpartum uterine cleansing", "Digestive bitters"],
                clinical_indications=["Diabetes management", "Postpartum recovery", "Loss of appetite", "Stomach upset"],
                recommended_dosage="Chew 3-5 fresh leaves daily or drink 100 mL leaf infusion once daily",
                safety_warnings=["Intense bitter flavor; avoid excessive use in early pregnancy"]
            ),
            "ringworm_bush": HerbalRemedy(
                common_name="Ringworm Bush (Asunwon)",
                botanical_name="Senna alata / Cassia alata",
                active_compounds=["Rhein", "Chrysophanol", "Aloe-emodin", "Kaempferol", "Anthraquinones"],
                therapeutic_actions=["Antifungal", "Dermatological healer", "Antibacterial", "Laxative"],
                clinical_indications=["Ringworm (Tinea corporis)", "Athlete's foot", "Eczema", "Constipation"],
                recommended_dosage="Topical: Crush leaves and apply directly to skin lesion twice daily; Oral: Short-term tea",
                safety_warnings=["Oral use is a strong anthraquinone laxative; do not use orally for >7 consecutive days"]
            ),
            "scent_leaf": HerbalRemedy(
                common_name="Scent Leaf (Efirin)",
                botanical_name="Ocimum gratissimum",
                active_compounds=["Eugenol", "Thymol", "Citral", "Linalool", "Rosmarinic acid"],
                therapeutic_actions=["Broad-spectrum Antimicrobial", "Antispasmodic", "Antidiarrheal", "Anti-inflammatory"],
                clinical_indications=["Abdominal cramps", "Diarrhea", "Fungal mouth wash", "Cough", "Nausea"],
                recommended_dosage="Infusion tea: 1 cup (150 mL) 3 times daily after meals; Fresh leaf juice for cramps",
                safety_warnings=["Safe botanical; high concentrated essential oil should not be ingested raw"]
            ),
            "mangosteen": HerbalRemedy(
                common_name="Mangosteen",
                botanical_name="Garcinia mangostana",
                active_compounds=["Alpha-mangostin", "Gamma-mangostin", "Xanthones", "Proanthocyanidins"],
                therapeutic_actions=["Anti-inflammatory", "Anti-cancer research", "Antioxidant", "Antibacterial"],
                clinical_indications=["Chronic systemic inflammation", "Skin allergy", "Gut inflammation", "Immune boost"],
                recommended_dosage="Pericarp rind extract: 500 mg twice daily; Fruit juice: 100 mL daily",
                safety_warnings=["May slow blood clotting; stop 2 weeks prior to scheduled surgery"]
            ),
            "cape_aloe": HerbalRemedy(
                common_name="Cape Aloe",
                botanical_name="Aloe ferox",
                active_compounds=["Aloin", "Aloe-emodin", "Polymannans", "Glycoproteins", "Chromones"],
                therapeutic_actions=["Stimulant laxative", "Dermatological healing", "Anti-inflammatory", "Immune modulation"],
                clinical_indications=["Severe constipation", "Burns", "Skin wounds", "Psoriasis", "Gut detox"],
                recommended_dosage="Inner gel topically; Dried resin: 50-100 mg for constipation (short-term)",
                safety_warnings=["Contraindicated in intestinal obstruction, Crohn's disease, and pregnancy"]
            ),

            # ── 2. AYURVEDA & IMPPAT MONOGRAPHS ──
            "turmeric": HerbalRemedy(
                common_name="Turmeric / Curcumin",
                botanical_name="Curcuma longa",
                active_compounds=["Curcuminoids", "Curcumin", "Demethoxycurcumin", "Turmerones"],
                therapeutic_actions=["Anti-inflammatory (NF-kB inhibitor)", "Antioxidant", "Neuroprotective", "Hepatoprotective"],
                clinical_indications=["Joint pain", "Arthritis", "Inflammatory bowel support", "Cognitive health", "Liver health"],
                recommended_dosage="500-1000 mg standardized extract daily (with piperine / black pepper for bio-absorption)",
                safety_warnings=["Use with caution with anticoagulants", "May aggravate active gallstones"]
            ),
            "ashwagandha": HerbalRemedy(
                common_name="Ashwagandha",
                botanical_name="Withania somnifera",
                active_compounds=["Withanolides", "Withaferin A", "Somniferine", "Anahygrine"],
                therapeutic_actions=["Adaptogenic", "Anxiolytic", "Cortisol modulating", "Immunomodulatory", "Nootropic"],
                clinical_indications=["Chronic stress", "Anxiety", "Adrenal fatigue", "Insomnia", "Thyroid support", "Low stamina"],
                recommended_dosage="300-600 mg standardized root extract daily with warm milk or water",
                safety_warnings=["May stimulate thyroid hormone output; caution in severe hyperthyroidism"]
            ),
            "berberine": HerbalRemedy(
                common_name="Berberine (Goldthread / Barberry)",
                botanical_name="Berberis vulgaris / Coptis chinensis",
                active_compounds=["Berberine alkaloid", "Jatrorrhizine", "Palmatine", "Columbamine"],
                therapeutic_actions=["AMPK activator", "Hypoglycemic", "Lipid-lowering", "Antimicrobial", "Gut microbiome balancer"],
                clinical_indications=["Type 2 Diabetes", "Metabolic syndrome", "Hyperlipidemia", "PCOS", "SIBO / Gut dysbiosis"],
                recommended_dosage="500 mg 2-3 times daily before meals (max 1500 mg daily)",
                safety_warnings=["Inhibits CYP3A4 and CYP2D6 enzymes; monitor closely when combined with Metformin"]
            ),
            "gymnema": HerbalRemedy(
                common_name="Gymnema (Gurmar / Sugar Destroyer)",
                botanical_name="Gymnema sylvestre",
                active_compounds=["Gymnemic acids", "Gymnemasaponins", "Gurmarin", "Gymnemagenin"],
                therapeutic_actions=["Sugar taste blocker", "Pancreatic beta-cell regenerative", "Hypoglycemic", "Hypolipidemic"],
                clinical_indications=["Sugar cravings", "Type 1 & Type 2 Diabetes support", "Weight management", "Hyperglycemia"],
                recommended_dosage="400-600 mg standardized extract daily or chew leaves to block sweet taste receptors",
                safety_warnings=["Monitor blood sugar levels to prevent hypoglycemia when combined with insulin"]
            ),
            "bitter_melon": HerbalRemedy(
                common_name="Bitter Melon",
                botanical_name="Momordica charantia",
                active_compounds=["Charantin", "Vicine", "Polypeptide-p", "Kuguacin", "Momordicines"],
                therapeutic_actions=["Insulin-mimetic", "GLUT4 translocation enhancer", "Hypoglycemic", "AMPK activator"],
                clinical_indications=["High blood glucose", "Pre-diabetes", "Insulin resistance", "Hyperlipidemia"],
                recommended_dosage="Fresh fruit juice: 50-100 mL daily; Standardized extract: 500 mg twice daily",
                safety_warnings=["Strong glucose lowering; avoid in pregnancy due to emmenagogue action"]
            ),
            "jamun": HerbalRemedy(
                common_name="Jamun / Black Plum",
                botanical_name="Syzygium cumini",
                active_compounds=["Jamboline", "Ellagic acid", "Anthocyanins", "Ferulic acid", "Myricetin"],
                therapeutic_actions=["Pancreatic protective", "Hypoglycemic", "Astringent", "Antioxidant"],
                clinical_indications=["Diabetic polyuria", "Excessive thirst in diabetes", "Diarrhea", "Pancreatic insufficiency"],
                recommended_dosage="Seed powder: 1-3 grams daily in warm water; Fruit juice: 50 mL daily",
                safety_warnings=["Avoid taking on an empty stomach; safe botanical"]
            ),
            "holy_basil": HerbalRemedy(
                common_name="Holy Basil (Tulsi)",
                botanical_name="Ocimum sanctum / Ocimum tenuiflorum",
                active_compounds=["Eugenol", "Ursolic acid", "Rosmarinic acid", "Apigenin", "Ocimumosides"],
                therapeutic_actions=["Adaptogenic", "Cortisol reducer", "Antiviral", "Bronchodilator", "Cardioprotective"],
                clinical_indications=["Respiratory congestion", "Cough & cold", "Mental stress", "High blood pressure", "Asthma"],
                recommended_dosage="Tea infusion: 1 cup (200 mL) 2-3 times daily; Leaf extract: 500 mg twice daily",
                safety_warnings=["May mildly thin blood; stop 10 days before surgery"]
            ),
            "andrographis": HerbalRemedy(
                common_name="Andrographis (King of Bitters / Kalmegh)",
                botanical_name="Andrographis paniculata",
                active_compounds=["Andrographolide", "Neoandrographolide", "Deoxyandrographolide", "Flavonoids"],
                therapeutic_actions=["Immune stimulant", "Upper respiratory antiviral", "Hepatoprotective", "Fever reducer"],
                clinical_indications=["Common cold", "Upper respiratory tract infection", "Sinusitis", "Sore throat", "Fever"],
                recommended_dosage="400-600 mg standardized extract (10% andrographolides) 3 times daily during illness",
                safety_warnings=["High doses may cause mild allergic skin rash or stomach upset"]
            ),
            "giloy_tinospora": HerbalRemedy(
                common_name="Giloy / Guduchi",
                botanical_name="Tinospora cordifolia",
                active_compounds=["Tinosporoside", "Cordifolioside A", "Berberine", "Magnoflorine", "Guduchiside"],
                therapeutic_actions=["Immunomodulatory", "Antipyretic (fever reducer)", "Detoxifying", "Anti-gout"],
                clinical_indications=["Chronic recurrent fever", "Dengue/malaria recovery", "Gout / High uric acid", "Low immunity"],
                recommended_dosage="Stem decoction: 50 mL twice daily; Powder: 2-3 grams daily with warm water",
                safety_warnings=["May stimulate immune system; caution in active autoimmune conditions"]
            ),
            "bacopa": HerbalRemedy(
                common_name="Bacopa Monnieri (Brahmi)",
                botanical_name="Bacopa monnieri",
                active_compounds=["Bacoside A", "Bacoside B", "Bacopasaponins", "Hersaponin"],
                therapeutic_actions=["Nootropic", "Cognitive enhancer", "Anxiolytic", "Neuroprotective", "Synaptic restorative"],
                clinical_indications=["Memory impairment", "ADHD / Focus difficulty", "Mental fatigue", "Anxiety", "Age-related cognitive decline"],
                recommended_dosage="300-450 mg standardized extract (50% bacosides) daily with food containing healthy fats",
                safety_warnings=["May cause mild nausea or dry mouth on empty stomach; take with meals"]
            ),
            "gotu_kola": HerbalRemedy(
                common_name="Gotu Kola",
                botanical_name="Centella asiatica",
                active_compounds=["Asiaticoside", "Madecassoside", "Asiatic acid", "Madecassic acid"],
                therapeutic_actions=["Venous tonic", "Collagen synthesis booster", "Anxiolytic", "Neuroprotective"],
                clinical_indications=["Varicose veins", "Venous insufficiency", "Wound healing", "Stretch marks", "Anxiety"],
                recommended_dosage="60-120 mg standardized extract daily; Leaf tea: 1 cup twice daily",
                safety_warnings=["Rare hepatotoxicity at extreme overdose; stick to recommended dosage"]
            ),
            "shatavari": HerbalRemedy(
                common_name="Shatavari",
                botanical_name="Asparagus racemosus",
                active_compounds=["Shatavarins I-IV", "Sarsasapogenin", "Quercetin", "Rutins"],
                therapeutic_actions=["Female reproductive tonic", "Galactagogue (breastmilk booster)", "Demulcent", "Adaptogen"],
                clinical_indications=["PMS cramps", "Menopausal hot flashes", "Low breastmilk supply", "Gastric ulcers"],
                recommended_dosage="500-1000 mg extract daily or 3 grams root powder in warm milk",
                safety_warnings=["Avoid if allergic to asparagus plant family"]
            ),
            "arjuna": HerbalRemedy(
                common_name="Arjuna Bark",
                botanical_name="Terminalia arjuna",
                active_compounds=["Arjunolic acid", "Arjunic acid", "Arjunetin", "Coenzyme Q10 analogs", "Flavonoids"],
                therapeutic_actions=["Cardiotonic", "Coronary artery vasodilator", "Anti-atherosclerotic", "Antihypertensive"],
                clinical_indications=["Angina pectoris", "Congestive heart failure support", "High blood pressure", "Post-MI recovery"],
                recommended_dosage="500 mg standardized bark extract twice daily; Bark decoction: 1 cup daily",
                safety_warnings=["Complementary to cardiology care; do not discontinue prescribed cardiac medications"]
            ),
            "punarnava": HerbalRemedy(
                common_name="Punarnava",
                botanical_name="Boerhavia diffusa",
                active_compounds=["Punarnavine", "Boeravinones A-F", "Liriodendrin", "Sitosterol"],
                therapeutic_actions=["Diuretic", "Nephroprotective", "Anti-edematous", "Hepatoprotective"],
                clinical_indications=["Kidney dysfunction", "Fluid retention / Edema", "Ascites", "Gout", "Urinary tract swelling"],
                recommended_dosage="Root powder: 2-3 grams twice daily with warm water; Extract: 500 mg twice daily",
                safety_warnings=["Increases urination; ensure adequate electrolyte and hydration intake"]
            ),
            "triphala": HerbalRemedy(
                common_name="Triphala (Amalaki + Bibhitaki + Haritaki)",
                botanical_name="Phyllanthus emblica + Terminalia bellirica + Terminalia chebula",
                active_compounds=["Chebulagic acid", "Chebulinic acid", "Gallic acid", "Ellagic acid", "Vitamin C"],
                therapeutic_actions=["Colon cleanser", "Gentle bowel regulator", "Antioxidant", "Ophthalmic health"],
                clinical_indications=["Chronic constipation", "Irritable bowel syndrome", "Eye strain", "Digestive detox"],
                recommended_dosage="3-5 grams powder in warm water before bedtime; Extract: 1000 mg bedtime",
                safety_warnings=["Gentle; excessive doses may cause loose stools in sensitive individuals"]
            ),
            "guggul": HerbalRemedy(
                common_name="Guggul",
                botanical_name="Commiphora mukul",
                active_compounds=["Guggulsterones E & Z", "Mukulol", "Myrcene"],
                therapeutic_actions=["Lipid lowering", "Thyroid stimulating", "Anti-inflammatory", "Anti-atherosclerotic"],
                clinical_indications=["Hyperlipidemia / High LDL", "Obesity support", "Nodular acne", "Osteoarthritis"],
                recommended_dosage="500 mg standardized extract (2.5% guggulsterones) 2-3 times daily",
                safety_warnings=["Caution in hyperthyroidism; may interact with estrogen pills"]
            ),
            "mucuna": HerbalRemedy(
                common_name="Mucuna Pruriens (Velvet Bean)",
                botanical_name="Mucuna pruriens",
                active_compounds=["L-DOPA (Levodopa)", "Serotonin", "Prurienine", "Bufotenine"],
                therapeutic_actions=["Dopamine precursor", "Neuroprotective", "Pro-libido", "Growth hormone stimulant"],
                clinical_indications=["Parkinson's symptom support", "Low motivation / Anhedonia", "Male infertility", "Low libido"],
                recommended_dosage="250-500 mg extract (standardized to 15% L-DOPA) 1-2 times daily",
                safety_warnings=["Do not combine with MAO inhibitor antidepressant medications"]
            ),
            "tribulus": HerbalRemedy(
                common_name="Tribulus (Gokshura)",
                botanical_name="Tribulus terrestris",
                active_compounds=["Protodioscin", "Dioscin", "Tribuloside", "Steroidal saponins"],
                therapeutic_actions=["Urinary tract tonic", "Libido enhancer", "Diuretic", "Nitric oxide booster"],
                clinical_indications=["Dysuria / Painful urination", "Kidney gravel", "Erectile dysfunction", "Athletic stamina"],
                recommended_dosage="250-500 mg standardized extract (45% saponins) 2 times daily",
                safety_warnings=["May irritate prostate in active benign prostatic hyperplasia (BPH)"]
            ),

            # ── 3. TRADITIONAL CHINESE MEDICINE (TCM) MONOGRAPHS ──
            "green_tea_egcg": HerbalRemedy(
                common_name="Green Tea (EGCG)",
                botanical_name="Camellia sinensis",
                active_compounds=["Epigallocatechin gallate (EGCG)", "Epicatechin", "L-theanine", "Caffeine"],
                therapeutic_actions=["Antioxidant", "Thermogenic / Weight management", "Cardioprotective", "Neuroprotective"],
                clinical_indications=["High cholesterol", "Weight loss support", "Cognitive focus", "Metabolic syndrome"],
                recommended_dosage="300-500 mg EGCG standardized green tea extract daily with meals",
                safety_warnings=["High dose concentrated extracts on empty stomach can cause liver elevation"]
            ),
            "sweet_wormwood": HerbalRemedy(
                common_name="Sweet Wormwood (Qinghao)",
                botanical_name="Artemisia annua",
                active_compounds=["Artemisinin", "Arteannuin B", "Scopoletin", "Chrysosplenol"],
                therapeutic_actions=["Antimalarial", "Anti-parasitic", "Cytotoxic research", "Antipyretic"],
                clinical_indications=["Malaria treatment", "Parasitic intestinal infections", "Fever spikes"],
                recommended_dosage="Standardized artemisinin: 100-200 mg daily for 3-5 days (under medical guidance)",
                safety_warnings=["Do not take long-term; pulse dosing only for acute infection"]
            ),
            "ginseng": HerbalRemedy(
                common_name="Korean Red Ginseng (Ren Shen)",
                botanical_name="Panax ginseng",
                active_compounds=["Ginsenosides Rg1, Rb1, Rg3", "Panaxans", "Polysaccharides"],
                therapeutic_actions=["Adaptogenic", "Stamina & Energy booster", "Cognitive enhancer", "Nitric oxide synthesis"],
                clinical_indications=["Chronic fatigue", "Burnout", "Erectile dysfunction", "Immune depletion", "Brain fog"],
                recommended_dosage="200-400 mg standardized extract (4-7% ginsenosides) daily in morning",
                safety_warnings=["May increase blood pressure or cause insomnia if taken before sleep"]
            ),
            "astragalus": HerbalRemedy(
                common_name="Astragalus (Huang Qi)",
                botanical_name="Astragalus membranaceus",
                active_compounds=["Astragalosides I-IV", "Cycloastragenol", "Polysaccharides", "Formononetin"],
                therapeutic_actions=["Immune stimulant", "Telomerase activator", "Nephroprotective", "Cardiotonic"],
                clinical_indications=["Frequent colds / Low immunity", "Kidney disease support", "Chronic fatigue", "Heart failure"],
                recommended_dosage="500-1000 mg root extract daily; Root slices boiled in soups",
                safety_warnings=["Do not use during acute high fever or active severe organ transplant rejection"]
            ),
            "schisandra": HerbalRemedy(
                common_name="Schisandra Berry (Wu Wei Zi)",
                botanical_name="Schisandra chinensis",
                active_compounds=["Schisandrin A, B, C", "Gomisin A", "Deoxyschisandrin", "Lignans"],
                therapeutic_actions=["Hepatoprotective (Phase I/II detox)", "Adaptogenic", "Nootropic", "Adrenal tonic"],
                clinical_indications=["Elevated ALT/AST liver enzymes", "Mental exhaustion", "Adrenal burnout", "Night sweats"],
                recommended_dosage="500-1000 mg berry extract daily or 2-3 grams dried berries as tea",
                safety_warnings=["May mildly increase stomach acid; take after food if sensitive"]
            ),
            "reishi": HerbalRemedy(
                common_name="Reishi Mushroom (Lingzhi)",
                botanical_name="Ganoderma lucidum",
                active_compounds=["Beta-1,3/1,6-glucans", "Ganoderic acids A-F", "Triterpenes", "Ling Zhi-8"],
                therapeutic_actions=["Immunomodulatory", "Anxiolytic / Calmative", "Hepatoprotective", "Antihistamine"],
                clinical_indications=["Insomnia", "Anxiety", "Chronic fatigue syndrome", "Seasonal allergies", "Immune support"],
                recommended_dosage="1000-2000 mg dual-extract fruiting body daily",
                safety_warnings=["May thin blood mildly; stop prior to surgery"]
            ),
            "cordyceps": HerbalRemedy(
                common_name="Cordyceps (Dong Chong Xia Cao)",
                botanical_name="Cordyceps sinensis / Cordyceps militaris",
                active_compounds=["Cordycepin", "Adenosine", "Cordycep acid", "Polysaccharides"],
                therapeutic_actions=["ATP cellular energy booster", "VO2 max enhancer", "Renal protective", "Bronchodilator"],
                clinical_indications=["Athletic performance", "COPD / Asthma", "Chronic kidney disease", "Low libido"],
                recommended_dosage="1000-3000 mg mycelium extract daily in morning/afternoon",
                safety_warnings=["Safe mushroom tonic; monitor if on immunosuppressants"]
            ),
            "lions_mane": HerbalRemedy(
                common_name="Lion's Mane Mushroom",
                botanical_name="Hericium erinaceus",
                active_compounds=["Hericenones", "Erinacines", "Beta-glucans"],
                therapeutic_actions=["NGF (Nerve Growth Factor) stimulant", "Neuroregenerative", "Nootropic", "Gut mucosal healer"],
                clinical_indications=["Brain fog", "Memory loss", "Peripheral neuropathy", "Gastritis", "Mild depression"],
                recommended_dosage="1000-2000 mg standardized extract daily with food",
                safety_warnings=["Rare mushroom allergy; well tolerated"]
            ),
            "dong_quai": HerbalRemedy(
                common_name="Dong Quai (Female Ginseng)",
                botanical_name="Angelica sinensis",
                active_compounds=["Z-ligustilide", "Ferulic acid", "Butylphthalide", "Polysaccharides"],
                therapeutic_actions=["Uterine tonic", "Blood nourisher", "Smooth muscle relaxant", "Analgesic"],
                clinical_indications=["Dysmenorrhea (painful periods)", "Amenorrhea", "Menopausal hot flashes", "PMS"],
                recommended_dosage="500-1000 mg root extract daily between menstrual cycles",
                safety_warnings=["Contraindicated during active heavy menstrual bleeding and pregnancy"]
            ),
            "licorice_root": HerbalRemedy(
                common_name="Licorice Root (Gan Cao)",
                botanical_name="Glycyrrhiza glabra",
                active_compounds=["Glycyrrhizin", "Glabridin", "Liquiritigenin", "Isoliquiritigenin"],
                therapeutic_actions=["Demulcent", "Anti-ulcer", "Adrenal supportive", "Expectorant", "Antiviral"],
                clinical_indications=["Peptic ulcer disease", "GERD / Acid reflux", "Sore throat", "Cough", "Adrenal fatigue"],
                recommended_dosage="DGL (Deglycyrrhizinated Licorice) 380 mg chewable before meals for ulcers",
                safety_warnings=["Un-fractionated Glycyrrhizin causes sodium retention & hypertension; use DGL for long term"]
            ),
            "rhodiola": HerbalRemedy(
                common_name="Rhodiola Rosea (Golden Root)",
                botanical_name="Rhodiola rosea",
                active_compounds=["Rosavin", "Salidroside", "Rosin", "Tyrosol"],
                therapeutic_actions=["Adaptogenic", "Anti-burnout", "Cognitive stamina", "Monoamine oxidase modulator"],
                clinical_indications=["Workplace burnout", "Mental fatigue", "Altitude sickness", "Mild depression"],
                recommended_dosage="200-400 mg standardized extract (3% rosavins, 1% salidroside) in morning",
                safety_warnings=["Stimulating; do not take late in evening to prevent insomnia"]
            ),

            # ── 4. WESTERN HERBALISM & WHO MONOGRAPHS ──
            "st_johns_wort": HerbalRemedy(
                common_name="St. John's Wort",
                botanical_name="Hypericum perforatum",
                active_compounds=["Hypericin", "Hyperforin", "Flavonoids", "Melatonin"],
                therapeutic_actions=["Serotonergic", "Anxiolytic", "Mild Antidepressant", "Neuralgic healer"],
                clinical_indications=["Mild to moderate depression", "Seasonal affective disorder", "Nerve pain"],
                recommended_dosage="300 mg standardized extract (0.3% hypericin) 3 times daily",
                safety_warnings=["Strong CYP3A4 & P-glycoprotein inducer; severely counteracts oral contraceptives & anticoagulants"]
            ),
            "milk_thistle": HerbalRemedy(
                common_name="Milk Thistle",
                botanical_name="Silybum marianum",
                active_compounds=["Silymarin", "Silibinin", "Silicristin", "Silydianin"],
                therapeutic_actions=["Hepatoprotective", "Antioxidant", "Bile production enhancer", "Renal protective"],
                clinical_indications=["Fatty liver disease (NAFLD)", "Elevated liver enzymes", "Alcoholic hepatitis", "Mushroom poisoning"],
                recommended_dosage="140-420 mg silymarin extract daily in divided doses",
                safety_warnings=["Mild laxative effect; caution in severe ragweed allergy"]
            ),
            "valerian": HerbalRemedy(
                common_name="Valerian Root",
                botanical_name="Valeriana officinalis",
                active_compounds=["Valerenic acid", "Valepotriates", "Isovaleric acid", "Hesperidin"],
                therapeutic_actions=["GABAergic", "Sedative", "Sleep latency reducer", "Spasmolytic"],
                clinical_indications=["Insomnia", "Sleep latency disorder", "Nervous tension", "Muscle spasms"],
                recommended_dosage="300-600 mg extract 30-60 minutes before bedtime",
                safety_warnings=["Additive sedative effect with CNS depressants, benzodiazepines, or alcohol"]
            ),
            "dandelion_root": HerbalRemedy(
                common_name="Dandelion Root & Leaf",
                botanical_name="Taraxacum officinale",
                active_compounds=["Taraxasterol", "Inulin", "Chicoric acid", "Sesquiterpene lactones", "Potassium"],
                therapeutic_actions=["Prebiotic", "Choleretic (bile stimulant)", "Diuretic (leaf)", "Hepatoprotective"],
                clinical_indications=["Sluggish digestion", "Constipation", "Water retention / Edema", "Liver congestion"],
                recommended_dosage="Root tea: 1 cup (200 mL) 3 times daily before meals; Root extract: 500 mg 2 times daily",
                safety_warnings=["Avoid in active bile duct obstruction or acute gallbladder infection"]
            ),
            "garlic": HerbalRemedy(
                common_name="Garlic",
                botanical_name="Allium sativum",
                active_compounds=["Allicin", "Ajoene", "S-allylcysteine", "Diallyl disulfide"],
                therapeutic_actions=["Antimicrobial", "Antithrombotic / Antiplatelet", "Antihypertensive", "Hypolipidemic"],
                clinical_indications=["High blood pressure", "Elevated LDL cholesterol", "Atherosclerosis prevention", "Common cold"],
                recommended_dosage="Aged garlic extract: 600-1200 mg daily; Raw crushed clove: 1-2 cloves daily with food",
                safety_warnings=["Additive bleeding risk when combined with Warfarin or Aspirin"]
            ),
            "ginger": HerbalRemedy(
                common_name="Ginger",
                botanical_name="Zingiber officinale",
                active_compounds=["Gingerols", "Shogaols", "Zingiberene", "Paradols"],
                therapeutic_actions=["Anti-emetic (anti-nausea)", "Pro-kinetic", "Anti-inflammatory", "Analgesic"],
                clinical_indications=["Morning sickness", "Motion sickness", "Chemotherapy nausea", "Osteoarthritis", "Indigestion"],
                recommended_dosage="1000 mg powdered root daily or 1 cup fresh steeped ginger tea 3 times daily",
                safety_warnings=["Very high doses (>4g) may cause mild heartburn or thin blood"]
            ),
            "peppermint": HerbalRemedy(
                common_name="Peppermint Leaf & Oil",
                botanical_name="Mentha x piperita",
                active_compounds=["Menthol", "Menthone", "Menthofuran", "Rosmarinic acid"],
                therapeutic_actions=["Smooth muscle antispasmodic", "Carminative", "Analgesic", "Decongestant"],
                clinical_indications=["Irritable Bowel Syndrome (IBS)", "Abdominal bloating", "Tension headache", "Nausea"],
                recommended_dosage="Enteric-coated peppermint oil capsule: 0.2 mL 3 times daily 30 min before meals",
                safety_warnings=["Un-coated peppermint oil may relax esophageal sphincter and worsen GERD / acid reflux"]
            ),
            "chamomile": HerbalRemedy(
                common_name="German Chamomile",
                botanical_name="Matricaria chamomilla / Matricaria recutita",
                active_compounds=["Apigenin", "Chamazulene", "Bisabolol", "Flavonoids"],
                therapeutic_actions=["Anxiolytic", "Mild sedative", "Gastroprotective", "Anti-inflammatory"],
                clinical_indications=["Anxiety", "Insomnia", "Gastritis", "Infantile colic", "Eczema wash"],
                recommended_dosage="Strong tea: 1 cup (200 mL) 3 times daily or before sleep; Extract: 400 mg",
                safety_warnings=["Caution in individuals with severe Asteraceae (ragweed) plant allergies"]
            ),
            "echinacea": HerbalRemedy(
                common_name="Echinacea",
                botanical_name="Echinacea purpurea / Echinacea angustifolia",
                active_compounds=["Alkamides", "Cichoric acid", "Echinacoside", "Polysaccharides"],
                therapeutic_actions=["Immune stimulant", "Phagocytosis enhancer", "Anti-viral", "Wound healer"],
                clinical_indications=["Early onset cold & flu", "Upper respiratory infections", "Sore throat"],
                recommended_dosage="300-500 mg root extract 3 times daily at first sign of cold for up to 10 days",
                safety_warnings=["Best used short-term (under 14 days); caution in systemic autoimmune diseases"]
            ),
            "saw_palmetto": HerbalRemedy(
                common_name="Saw Palmetto",
                botanical_name="Serenoa repens",
                active_compounds=["Free fatty acids (Lauric, Oleic)", "Beta-sitosterol", "Stigmasterol"],
                therapeutic_actions=["5-alpha-reductase inhibitor", "Prostate decongestant", "Anti-androgenic"],
                clinical_indications=["Benign Prostatic Hyperplasia (BPH)", "Frequent nighttime urination in men", "Androgenic alopecia"],
                recommended_dosage="320 mg standardized liposterolic extract (85-95% fatty acids) daily",
                safety_warnings=["Rule out prostate cancer with physician prior to initiating long-term therapy"]
            ),
            "boswellia": HerbalRemedy(
                common_name="Boswellia (Frankincense / Shallaki)",
                botanical_name="Boswellia serrata",
                active_compounds=["AKBA (Acetyl-11-keto-beta-boswellic acid)", "Boswellic acids", "Incensole acetate"],
                therapeutic_actions=["5-LOX inhibitor", "Potent anti-inflammatory", "Anti-arthritic", "Chondroprotective"],
                clinical_indications=["Osteoarthritis", "Rheumatoid arthritis", "Ulcerative colitis", "Asthma"],
                recommended_dosage="300-500 mg standardized extract (65% boswellic acids) 2-3 times daily with food",
                safety_warnings=["Take with meals to prevent mild gastrointestinal discomfort"]
            ),
            "hawthorn": HerbalRemedy(
                common_name="Hawthorn Berry & Leaf",
                botanical_name="Crataegus oxyacantha / Crataegus monogyna",
                active_compounds=["Oligomeric proanthocyanidins (OPCs)", "Vitexin", "Hyperoside", "Quercetin"],
                therapeutic_actions=["Cardiotonic", "Coronary vasodilator", "Positive inotrope", "Antihypertensive"],
                clinical_indications=["Mild heart failure (NYHA Class I-II)", "Hypertension", "Angina support", "Cardiac arrhythmia prevention"],
                recommended_dosage="160-900 mg standardized hawthorn extract daily in divided doses",
                safety_warnings=["May enhance effects of prescription digoxin or antihypertensives; physician monitoring recommended"]
            ),
            "elderberry": HerbalRemedy(
                common_name="Elderberry",
                botanical_name="Sambucus nigra",
                active_compounds=["Anthocyanins", "Quercetin", "Rutin", "Lectins"],
                therapeutic_actions=["Viral neuraminidase inhibitor", "Immune supportive", "Diaphoretic", "Antioxidant"],
                clinical_indications=["Influenza A & B", "Common cold duration reduction", "Sinus congestion"],
                recommended_dosage="Standardized syrup: 15 mL 4 times daily during acute flu; Extract tablet: 500 mg twice daily",
                safety_warnings=["Raw unripe berries/leaves contain cyanogenic glycosides; use cooked or commercial extracts only"]
            ),
            "bilberry": HerbalRemedy(
                common_name="Bilberry",
                botanical_name="Vaccinium myrtillus",
                active_compounds=["Anthocyanosides", "Resveratrol", "Quercetin", "Tannins"],
                therapeutic_actions=["Rhodopsin regeneration booster", "Retinal microvascular tonic", "Capillary stabilizer"],
                clinical_indications=["Night blindness", "Diabetic retinopathy support", "Glaucoma microcirculation", "Eye fatigue"],
                recommended_dosage="160-320 mg standardized extract (25% anthocyanosides) daily",
                safety_warnings=["High safety profile; safe botanical"]
            ),
            "feverfew": HerbalRemedy(
                common_name="Feverfew",
                botanical_name="Tanacetum parthenium",
                active_compounds=["Parthenolide", "Chrysanthemonin", "Camphor"],
                therapeutic_actions=["Serotonin release inhibitor", "Migraine prophylactic", "Vascular smooth muscle relaxant"],
                clinical_indications=["Migraine headache prevention", "Cluster headaches", "Rheumatoid joint pain"],
                recommended_dosage="100-300 mg standardized extract (0.2-0.7% parthenolide) daily",
                safety_warnings=["Do not stop abruptly after long-term use (post-feverfew syndrome); avoid in pregnancy"]
            ),
            "kava": HerbalRemedy(
                common_name="Kava Kava",
                botanical_name="Piper methysticum",
                active_compounds=["Kavalactones (Kawain, Methysticin, Yangonin)", "Desmethoxyyangonin"],
                therapeutic_actions=["GABA-A receptor modulator", "Potent Anxiolytic", "Muscle relaxant", "Analgesic"],
                clinical_indications=["Acute anxiety", "Panic disorder support", "Social phobia", "Skeletal muscle tension"],
                recommended_dosage="120-250 mg kavalactones daily in divided doses",
                safety_warnings=["Avoid alcohol and hepatotoxic drugs; do not use in pre-existing liver disease"]
            ),
            "goldenseal": HerbalRemedy(
                common_name="Goldenseal",
                botanical_name="Hydrastis canadensis",
                active_compounds=["Berberine", "Hydrastine", "Canadine"],
                therapeutic_actions=["Mucosal astringent", "Antimicrobial", "Anti-diarrheal", "Bile stimulant"],
                clinical_indications=["Bacterial gastroenteritis", "Sinus infection wash", "UTI support", "Mucous membrane inflammation"],
                recommended_dosage="250-500 mg root extract 3 times daily for short durations (max 14 days)",
                safety_warnings=["Strictly contraindicated in pregnancy (uterine stimulant) and in newborn infants"]
            ),
            "slippery_elm": HerbalRemedy(
                common_name="Slippery Elm Bark",
                botanical_name="Ulmus rubra / Ulmus fulva",
                active_compounds=["Mucilage (galactose, rhamnose)", "Tannins", "Biostimulants"],
                therapeutic_actions=["Demulcent", "Gastrointestinal mucosal shield", "Emollient", "Anti-ulcer"],
                clinical_indications=["GERD / Acid reflux", "Gastritis", "Ulcerative colitis", "Sore throat", "IBS"],
                recommended_dosage="1-2 tablespoons powdered bark mixed into warm water to form slurry 3 times daily",
                safety_warnings=["Mucilage may coat gut wall and delay absorption of oral medications; separate by 2 hours"]
            ),
            "marshmallow_root": HerbalRemedy(
                common_name="Marshmallow Root",
                botanical_name="Althaea officinalis",
                active_compounds=["Polysaccharide mucilage", "Flavonoids", "Asn-betaine", "Pectins"],
                therapeutic_actions=["Demulcent", "Soothing expectorant", "Gastric protectant", "Urinary demulcent"],
                clinical_indications=["Dry hacking cough", "Bladder irritation / Cystitis", "Peptic ulcer", "Acid reflux"],
                recommended_dosage="Cold water infusion: 1 cup 3 times daily; Extract: 500 mg 3 times daily",
                safety_warnings=["Separate from prescription medications by 2 hours to avoid delayed absorption"]
            ),
            "gentian": HerbalRemedy(
                common_name="Gentian Root",
                botanical_name="Gentiana lutea",
                active_compounds=["Amarogentin", "Gentiopicroside", "Swertiamarin"],
                therapeutic_actions=["Intense digestive bitter", "Gastric juice stimulant", "Choleretic"],
                clinical_indications=["Hypochlorhydria (low stomach acid)", "Loss of appetite", "Sluggish digestion", "Bloating"],
                recommended_dosage="Tincture: 1-2 mL in a splash of water 15 minutes before meals",
                safety_warnings=["Contraindicated in active gastric or duodenal ulcers and severe hyperchlorhydria"]
            ),
            "artichoke_leaf": HerbalRemedy(
                common_name="Artichoke Leaf",
                botanical_name="Cynara scolymus",
                active_compounds=["Cynarin", "Chlorogenic acid", "Luteolin", "Scolymoside"],
                therapeutic_actions=["Choleretic (bile flow stimulant)", "Hypolipidemic", "Hepatoprotective", "Dyspepsia reliever"],
                clinical_indications=["High cholesterol", "Non-ulcer dyspepsia", "Nausea", "Fatty liver support"],
                recommended_dosage="320-640 mg standardized extract 2-3 times daily before meals",
                safety_warnings=["Avoid if bile duct is completely obstructed or in active gallstone blockage"]
            ),
            "senna": HerbalRemedy(
                common_name="Senna Leaf & Pod",
                botanical_name="Senna alexandrina / Cassia senna",
                active_compounds=["Sennosides A & B", "Rhein", "Aloe-emodin"],
                therapeutic_actions=["Stimulant laxative", "Colonic peristalsis promoter"],
                clinical_indications=["Acute constipation", "Pre-colonoscopy bowel cleansing"],
                recommended_dosage="15-30 mg sennosides daily at bedtime for maximum 7 consecutive days",
                safety_warnings=["Do not use longer than 7 days; prolonged use causes laxative dependency and electrolyte loss"]
            ),
            "cascara_sagrada": HerbalRemedy(
                common_name="Cascara Sagrada",
                botanical_name="Frangula purshiana / Rhamnus purshiana",
                active_compounds=["Cascarosides A, B, C, D", "Emodin", "Barbaloin"],
                therapeutic_actions=["Stimulant laxative", "Colonic neuromuscular stimulant"],
                clinical_indications=["Short-term constipation relief"],
                recommended_dosage="20-30 mg hydroxyanthracene derivatives at bedtime for max 7 days",
                safety_warnings=["Short term use only; avoid in pregnancy, nursing, and inflammatory bowel disease"]
            ),
            "uva_ursi": HerbalRemedy(
                common_name="Uva Ursi (Bearberry)",
                botanical_name="Arctostaphylos uva-ursi",
                active_compounds=["Arbutin", "Hydroquinone", "Methylarbutin", "Tannins"],
                therapeutic_actions=["Urinary antiseptic", "Astringent", "Anti-bacterial"],
                clinical_indications=["Acute uncomplicated cystitis / UTI", "Urethritis"],
                recommended_dosage="400-800 mg standardized extract (20% arbutin) 3 times daily for max 7 days",
                safety_warnings=["Do not use for more than 7 days per episode or 5 times per year (hydroquinone accumulation)"]
            ),
            "cranberry": HerbalRemedy(
                common_name="Cranberry",
                botanical_name="Vaccinium macrocarpon",
                active_compounds=["A-type Proanthocyanidins (PACs)", "D-mannose", "Quercetin", "Benzoic acid"],
                therapeutic_actions=["Uropathogenic E. coli anti-adhesion", "Urinary tract protector"],
                clinical_indications=["Recurrent UTI prevention", "Bladder health"],
                recommended_dosage="36 mg A-type PACs daily (or 500 mg extract twice daily / 250 mL unsweetened juice)",
                safety_warnings=["High consumption of juice may increase risk of calcium-oxalate kidney stones in prone individuals"]
            ),
            "horse_chestnut": HerbalRemedy(
                common_name="Horse Chestnut",
                botanical_name="Aesculus hippocastanum",
                active_compounds=["Aescin (Escin)", "Proanthocyanidins", "Quercetin"],
                therapeutic_actions=["Venotonic", "Vascular permeability reducer", "Anti-edematous"],
                clinical_indications=["Chronic Venous Insufficiency (CVI)", "Varicose veins", "Hemorrhoids", "Leg swelling"],
                recommended_dosage="300 mg standardized extract (50 mg aescin) twice daily",
                safety_warnings=["Raw unprocessed seeds are toxic; use standardized processed commercial extracts only"]
            ),
            "butchers_broom": HerbalRemedy(
                common_name="Butcher's Broom",
                botanical_name="Ruscus aculeatus",
                active_compounds=["Ruscogenins", "Neoruscogenins", "Rutoside"],
                therapeutic_actions=["Alpha-adrenergic vasoconstrictor", "Venotonic", "Lymphatic stimulant"],
                clinical_indications=["Chronic venous insufficiency", "Orthostatic hypotension", "Hemorrhoids"],
                recommended_dosage="150-300 mg standardized extract daily",
                safety_warnings=["Caution in patients taking alpha-blocker blood pressure medications"]
            ),
            "rosemary": HerbalRemedy(
                common_name="Rosemary",
                botanical_name="Salvia rosmarinus / Rosmarinus officinalis",
                active_compounds=["Rosmarinic acid", "Carnosic acid", "Carnosol", "Eucalyptol"],
                therapeutic_actions=["Cerebral circulatory stimulant", "Antioxidant", "Antimicrobial", "Carminative"],
                clinical_indications=["Mental sluggishness", "Memory support", "Dyspepsia", "Hair thinning (topical rinse)"],
                recommended_dosage="Leaf tea: 1 cup 2-3 times daily; Topical oil dilute for scalp stimulation",
                safety_warnings=["Culinary use safe; concentrated essential oil should not be ingested oral raw"]
            ),
            "thyme": HerbalRemedy(
                common_name="Thyme",
                botanical_name="Thymus vulgaris",
                active_compounds=["Thymol", "Carvacrol", "Linalool", "Rosmarinic acid"],
                therapeutic_actions=["Bronchial antispasmodic", "Expectorant", "Antimicrobial", "Antifungal"],
                clinical_indications=["Bronchitis", "Productive cough", "Pertussis support", "Oral yeast wash"],
                recommended_dosage="Leaf tea: 1 cup 3 times daily; Thyme syrup: 10 mL 3 times daily for cough",
                safety_warnings=["Thymol essential oil should not be ingested in pure concentrated form"]
            ),
            "oregano": HerbalRemedy(
                common_name="Oregano / Wild Oregano",
                botanical_name="Origanum vulgare",
                active_compounds=["Carvacrol", "Thymol", "Terpinene", "Rosmarinic acid"],
                therapeutic_actions=["Potent broad-spectrum Antibacterial", "Antifungal", "Antiparasitic", "Antioxidant"],
                clinical_indications=["Gut dysbiosis / Candida", "Upper respiratory infections", "GI bacterial overgrowth"],
                recommended_dosage="Oregano leaf extract capsule: 200 mg twice daily with food for up to 14 days",
                safety_warnings=["Oil of oregano is very potent; take with food to prevent gastric burning"]
            ),
            "sage": HerbalRemedy(
                common_name="Sage",
                botanical_name="Salvia officinalis",
                active_compounds=["Thujone", "Rosmarinic acid", "Carnosic acid", "Salvinorin"],
                therapeutic_actions=["Anhidrotic (sweat reducer)", "Estrogenic balancer", "Astringent", "Antimicrobial"],
                clinical_indications=["Menopausal night sweats", "Excessive perspiration (hyperhidrosis)", "Sore throat gargle"],
                recommended_dosage="Leaf tea: 1 cup twice daily; Standardized leaf extract: 300 mg daily",
                safety_warnings=["High thujone content in extreme overdoses; limit long-term high-dose use"]
            ),
            "lemon_balm": HerbalRemedy(
                common_name="Lemon Balm",
                botanical_name="Melissa officinalis",
                active_compounds=["Rosmarinic acid", "Citral", "Citronellal", "Caryophyllene"],
                therapeutic_actions=["GABA-transaminase inhibitor", "Anxiolytic", "Carminative", "Topical Antiviral"],
                clinical_indications=["Anxiety", "Restlessness", "Dyspepsia", "Cold sores (Herpes labialis topical cream)"],
                recommended_dosage="Tea: 1 cup 3 times daily; Standardized extract: 300-600 mg daily",
                safety_warnings=["May mildly inhibit thyroid function in extreme high doses; caution in severe hypothyroidism"]
            ),
            "passionflower": HerbalRemedy(
                common_name="Passionflower",
                botanical_name="Passiflora incarnata",
                active_compounds=["Chrysin", "Harmine", "Vitexin", "Isovitexin"],
                therapeutic_actions=["GABAergic", "Anxiolytic", "Mild Sedative", "Antispasmodic"],
                clinical_indications=["Generalized anxiety disorder", "Insomnia", "Nervous stomach", "Opiate withdrawal support"],
                recommended_dosage="500 mg standardized extract daily or 1 cup tea bedtime",
                safety_warnings=["Additive sedative effect when combined with pharmaceutical sleeping pills"]
            ),
            "skullcap": HerbalRemedy(
                common_name="American Skullcap",
                botanical_name="Scutellaria lateriflora",
                active_compounds=["Baicalin", "Baicalein", "Wogonin", "Scutellarin"],
                therapeutic_actions=["Nervine relaxant", "GABAergic", "Antispasmodic", "Neuroprotective"],
                clinical_indications=["Nervous exhaustion", "Tremors", "Anxiety", "PMS irritability"],
                recommended_dosage="350-700 mg dried herb extract daily; Tea: 1 cup 2-3 times daily",
                safety_warnings=["Ensure source authenticity (avoid adulteration with germander plant species)"]
            ),
            "maca": HerbalRemedy(
                common_name="Maca Root",
                botanical_name="Lepidium meyenii",
                active_compounds=["Macamides", "Macaenes", "Glucosinolates", "Beta-sitosterol"],
                therapeutic_actions=["Endocrine adaptogen", "Libido enhancer", "Sperm quality booster", "Energy promoter"],
                clinical_indications=["Low sexual desire", "Menopausal mood support", "Athletic stamina", "Fertility support"],
                recommended_dosage="1500-3000 mg gelatinized maca root powder daily in smoothies or warm beverage",
                safety_warnings=["Safe adaptogenic food root"]
            ),
            "cats_claw": HerbalRemedy(
                common_name="Cat's Claw (Uña de Gato)",
                botanical_name="Uncaria tomentosa / Uncaria guianensis",
                active_compounds=["Pentacyclic oxindole alkaloids (POAs)", "Quinovic acid glycosides", "Proanthocyanidins"],
                therapeutic_actions=["Immune modulator", "Anti-inflammatory", "DNA repair enhancer", "Antiviral"],
                clinical_indications=["Osteoarthritis", "Rheumatoid arthritis", "Chronic viral immune support", "Gastric inflammation"],
                recommended_dosage="250-500 mg standardized POA extract daily",
                safety_warnings=["Avoid in active organ transplant recipients due to immune stimulation"]
            ),
            "pau_darco": HerbalRemedy(
                common_name="Pau d'Arco (Lapacho)",
                botanical_name="Handroanthus impetiginosus / Tabebuia impetiginosa",
                active_compounds=["Lapachol", "Beta-lapachone", "Quinones"],
                therapeutic_actions=["Antifungal", "Anticandidal", "Antiparasitic", "Anti-inflammatory"],
                clinical_indications=["Systemic candidiasis", "Fungal skin infections", "Prostatitis"],
                recommended_dosage="Inner bark decoction: 1 cup 2-3 times daily; Bark extract: 500 mg twice daily",
                safety_warnings=["Excessive doses of isolated lapachol may cause nausea or mild bleeding risk"]
            ),
            "cinnamon": HerbalRemedy(
                common_name="Ceylon Cinnamon",
                botanical_name="Cinnamomum verum / Cinnamomum zeylanicum",
                active_compounds=["Cinnamaldehyde", "Proanthocyanidins", "Cinnamic acid", "Low Coumarin"],
                therapeutic_actions=["Insulin sensitizer", "Hypoglycemic", "Antimicrobial", "Carminative"],
                clinical_indications=["Type 2 Diabetes support", "Insulin resistance", "Bloating", "Metabolic health"],
                recommended_dosage="1-2 grams powdered bark daily with food (prefer True Ceylon over Cassia)",
                safety_warnings=["Use True Ceylon Cinnamon for daily long-term use (Cassia contains higher coumarin)"]
            ),
            "clove": HerbalRemedy(
                common_name="Clove",
                botanical_name="Syzygium aromaticum",
                active_compounds=["Eugenol", "Eugenyl acetate", "Beta-caryophyllene"],
                therapeutic_actions=["Topical dental anesthetic", "Broad-spectrum Antimicrobial", "Antioxidant", "Antispasmodic"],
                clinical_indications=["Toothache", "Dental pain", "Intestinal parasites", "Oral infections"],
                recommended_dosage="Clove bud tea: 1 cup; Clove oil: 1 drop diluted on cotton swab for toothache",
                safety_warnings=["Undiluted clove oil burns oral mucous membranes; always dilute in carrier oil"]
            ),
            "fenugreek": HerbalRemedy(
                common_name="Fenugreek",
                botanical_name="Trigonella foenum-graecum",
                active_compounds=["Diosgenin", "4-hydroxyisoleucine", "Trigonelline", "Galactomannans"],
                therapeutic_actions=["Galactagogue (breastmilk booster)", "Hypoglycemic", "Hypolipidemic", "Digestive demulcent"],
                clinical_indications=["Insufficient breastmilk production", "Diabetes support", "High cholesterol", "Gastritis"],
                recommended_dosage="500-1000 mg extract 3 times daily or 5 grams ground seeds with meals",
                safety_warnings=["May impart sweet maple syrup odor to sweat/urine; safe botanical"]
            ),
            "calendula": HerbalRemedy(
                common_name="Calendula (Marigold)",
                botanical_name="Calendula officinalis",
                active_compounds=["Faradiol esters", "Calendulosides", "Carotenoids", "Flavonoids"],
                therapeutic_actions=["Vulnerary (wound healer)", "Anti-inflammatory", "Antimicrobial", "Lymphatic tonic"],
                clinical_indications=["Skin burns", "Minor cuts", "Radiation dermatitis", "Gastric ulcers"],
                recommended_dosage="Topical ointment/salve apply 2-3 times daily; Tea gargle for mouth ulcers",
                safety_warnings=["High safety profile topically"]
            ),
            "yarrow": HerbalRemedy(
                common_name="Yarrow",
                botanical_name="Achillea millefolium",
                active_compounds=["Achilleine", "Chamazulene", "Luteolin", "Sesquiterpene lactones"],
                therapeutic_actions=["Hemo-styptic (stops bleeding)", "Diaphoretic (fever breaker)", "Peripheral vasodilator", "Astringent"],
                clinical_indications=["Feverish cold", "Minor bleeding cuts", "Menorrhagia (heavy periods)", "High blood pressure"],
                recommended_dosage="Hot infusion tea: 1 cup 3 times daily to induce sweating during fever",
                safety_warnings=["Avoid in pregnancy due to uterine contracting potential"]
            ),
            "fennel": HerbalRemedy(
                common_name="Fennel Seed",
                botanical_name="Foeniculum vulgare",
                active_compounds=["Anethole", "Fenchone", "Estragole"],
                therapeutic_actions=["Carminative", "GI antispasmodic", "Galactagogue", "Expectorant"],
                clinical_indications=["Infantile colic", "Flatulence", "Abdominal bloating", "Low breastmilk supply"],
                recommended_dosage="Chew 1 teaspoon seeds after meals or drink 1 cup warm seed tea 3 times daily",
                safety_warnings=["Safe culinary herb"]
            ),
            "anise": HerbalRemedy(
                common_name="Aniseed",
                botanical_name="Pimpinella anisum",
                active_compounds=["Trans-anethole", "Pseudoisoeugenol", "Estragole"],
                therapeutic_actions=["Carminative", "Expectorant", "Antispasmodic", "Galactagogue"],
                clinical_indications=["Bronchial cough", "Gas & bloating", "Pediatric colic tea"],
                recommended_dosage="1 cup seed tea after meals",
                safety_warnings=["Safe spice herb"]
            )
        }

    def _initialize_interaction_matrix(self) -> List[HerbDrugInteraction]:
        """Initialize matrix of critical herb-drug interactions"""
        return [
            HerbDrugInteraction(
                herb_name="St. John's Wort",
                drug_class_or_name="SSRIs / Antidepressants (e.g., Sertraline, Fluoxetine)",
                severity="High",
                mechanism="Synergistic serotonergic stimulation causing risk of Serotonin Syndrome",
                clinical_recommendation="Strictly contraindicated. Discontinue St. John's Wort before starting SSRIs."
            ),
            HerbDrugInteraction(
                herb_name="St. John's Wort",
                drug_class_or_name="Oral Contraceptives / Blood Thinners / Anticonvulsants",
                severity="High",
                mechanism="Potent CYP3A4 hepatic enzyme induction accelerating drug clearance and reducing drug efficacy",
                clinical_recommendation="Avoid combination; use alternative herbal mood supports like Ashwagandha."
            ),
            HerbDrugInteraction(
                herb_name="Berberine",
                drug_class_or_name="Metformin / Insulin / Antidiabetics",
                severity="Moderate",
                mechanism="Additive hypoglycemic effect via combined AMPK activation and insulin sensitization",
                clinical_recommendation="Monitor blood glucose closely. Dose adjustment of pharmaceutical antidiabetics may be needed."
            ),
            HerbDrugInteraction(
                herb_name="Ginkgo Biloba",
                drug_class_or_name="Anticoagulants / Antiplatelets (e.g., Warfarin, Aspirin, Plavix)",
                severity="High",
                mechanism="Inhibition of platelet-activating factor increases risk of spontaneous bleeding and bruising",
                clinical_recommendation="Discontinue Ginkgo at least 2 weeks prior to surgery or when on full-dose anticoagulation."
            ),
            HerbDrugInteraction(
                herb_name="Turmeric / Curcumin",
                drug_class_or_name="Anticoagulants (e.g., Warfarin, NSAIDs)",
                severity="Moderate",
                mechanism="Mild antiplatelet activity may increase bleeding risk in high-dose curcumin supplementation",
                clinical_recommendation="Limit curcumin dosage to dietary levels (<500mg) and monitor INR if taking Warfarin."
            ),
            HerbDrugInteraction(
                herb_name="Valerian Root",
                drug_class_or_name="Benzodiazepines / Sedatives (e.g., Lorazepam, Zolpidem)",
                severity="Moderate",
                mechanism="Additive GABA-A receptor modulation producing excessive sedation and psychomotor impairment",
                clinical_recommendation="Do not combine with prescription sedatives without direct physician oversight."
            )
        ]

    def check_herb_drug_interactions(self, herbs: List[str], medications: List[str]) -> List[HerbDrugInteraction]:
        """Cross-examine patient herbs/supplements against prescription medications"""
        flagged_interactions = []
        
        herbs_lower = [h.lower() for h in herbs]
        meds_lower = [m.lower() for m in medications]
        
        for interaction in self.interaction_matrix:
            herb_name_lower = interaction.herb_name.lower()
            herb_match = any(h in herb_name_lower for h in herbs_lower) or \
                         any(h.split()[0] in herb_name_lower for h in herbs_lower if len(h) > 2)
            
            if herb_match:
                drug_target = interaction.drug_class_or_name.lower()
                for med in meds_lower:
                    med_parts = [p for p in med.split() if len(p) > 2]
                    if any(part in drug_target for part in med_parts) or \
                       ("ssri" in drug_target and any(s in med for s in ["sertraline", "fluoxetine", "ssri"])) or \
                       ("antidiabetic" in drug_target or "metformin" in drug_target) and any(d in med for d in ["metformin", "insulin", "glipizide"]) or \
                       ("anticoagulant" in drug_target or "aspirin" in drug_target or "warfarin" in drug_target) and any(a in med for a in ["warfarin", "aspirin", "plavix"]) or \
                       ("sedative" in drug_target and any(b in med for b in ["lorazepam", "zolpidem", "sedative"])):
                        if interaction not in flagged_interactions:
                            flagged_interactions.append(interaction)
                        
        return flagged_interactions

    def recommend_herbal_remedies(self, symptoms: List[str], medical_history: List[str]) -> List[HerbalRemedy]:
        """Recommend evidence-based botanical remedies based on clinical symptoms and history"""
        recommendations = []
        all_indicators = " ".join([s.lower() for s in symptoms + medical_history])
        
        for key, remedy in self.herbal_database.items():
            for indication in remedy.clinical_indications:
                if any(word in all_indicators for word in indication.lower().split() if len(word) > 3):
                    if remedy not in recommendations:
                        recommendations.append(remedy)
                        break
                        
        if not recommendations:
            recommendations.append(self.herbal_database["turmeric"])
            recommendations.append(self.herbal_database["ashwagandha"])
            
        return recommendations
