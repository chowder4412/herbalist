"""
Botanical Anatomy & Morphological Authentication Engine for Herbalist AI
Provides:
1. Toxic Look-Alike Authentication Guard (morphological diagnostic keys to prevent fatal ingestion of look-alike twins).
2. Plant Tissue Anatomy -> Scientific Thermodynamic Extraction Physics (Decoction vs Infusion vs Cold Maceration based on cellular structure).
"""

from typing import Dict, Any, Optional, List

TOXIC_LOOKALIKES_REGISTRY: Dict[str, Dict[str, Any]] = {
    "wild garlic": {
        "botanical_name": "Allium ursinum",
        "common_name": "Wild Garlic / Ramsons",
        "toxic_twins": [
            {
                "twin_name": "Lily of the Valley",
                "twin_botanical": "Convallaria majalis",
                "danger_level": "FATAL (Cardiac Glycosides / Convallatoxin)",
                "morphological_key": "Lily of the Valley has 2 leaves growing from a single sheath, non-glossy underside, and ABSOLUTELY NO garlic aroma when crushed.",
                "safe_verification": "Crush leaf: Must produce a strong, unmistakable pungent garlic scent. If odorless or sweet, DO NOT INGEST."
            },
            {
                "twin_name": "Autumn Crocus / Meadow Saffron",
                "twin_botanical": "Colchicum autumnale",
                "danger_level": "FATAL (Colchicine Cellular Toxin)",
                "morphological_key": "Autumn Crocus leaves are thick, stiff, erect without stalks/petioles, emerging in spring without flowers and odorless.",
                "safe_verification": "Wild garlic leaves have distinct single slender petioles (stalks) emerging individually from the ground with strong allium aroma."
            }
        ]
    },
    "wild carrot": {
        "botanical_name": "Daucus carota",
        "common_name": "Wild Carrot / Queen Anne's Lace",
        "toxic_twins": [
            {
                "twin_name": "Poison Hemlock",
                "twin_botanical": "Conium maculatum",
                "danger_level": "FATAL (Neurotoxic Coniine / Respiratory Paralysis)",
                "morphological_key": "Poison Hemlock has completely SMOOTH, HAIRLESS stems with distinct PURPLE BLOTCHES/splotches and a musty 'mousy' odor. Queen Anne's Lace has HAIRY solid-green stems with NO purple spots.",
                "safe_verification": "Examine the stem: Queen Anne's Lace has hairs ('The Queen has hairy legs'). Look for a single dark-purple central floret in the flower umbel."
            },
            {
                "twin_name": "Water Hemlock",
                "twin_botanical": "Cicuta maculata",
                "danger_level": "FATAL (Cicutoxin Neurotoxin)",
                "morphological_key": "Water Hemlock leaf veins end in the NOTCHES between teeth, never at the tips. Chambers inside root base exude yellow oily toxic sap.",
                "safe_verification": "Never harvest umbellifers near standing water or wetlands without expert botanical magnification."
            }
        ]
    },
    "comfrey": {
        "botanical_name": "Symphytum officinale",
        "common_name": "Comfrey / Knitbone",
        "toxic_twins": [
            {
                "twin_name": "Foxglove",
                "twin_botanical": "Digitalis purpurea",
                "danger_level": "FATAL (Cardiac Digoxin / Digitoxin Overdose)",
                "morphological_key": "Foxglove leaves are soft, velvety, downy with toothed margins and non-winged leaf stalks. Comfrey leaves have stiff bristly/sandpapery hairs and winged leaf bases that run down along the stem.",
                "safe_verification": "Feel the leaf texture: Comfrey is coarse and prickly to the touch with decurrent leaf bases running down the main stalk."
            }
        ]
    },
    "elderberry": {
        "botanical_name": "Sambucus nigra",
        "common_name": "Black Elderberry",
        "toxic_twins": [
            {
                "twin_name": "Dwarf Elder / Danewort",
                "twin_botanical": "Sambucus ebulus",
                "danger_level": "SEVERE TOXICITY (Cyanogenic Glucosides & Ebulin)",
                "morphological_key": "Dwarf Elder is an herbaceous non-woody plant (dies to ground in winter, max 1.5m), produces upright flat-topped flower heads, and smells foul/rank. True Elderberry is a woody tree/shrub (3–10m) with drooping umbels.",
                "safe_verification": "Harvest only from woody multi-stemmed trees/shrubs where ripe berry clusters droop heavily downwards."
            }
        ]
    },
    "star anise": {
        "botanical_name": "Illicium verum",
        "common_name": "Chinese Star Anise",
        "toxic_twins": [
            {
                "twin_name": "Japanese Star Anise",
                "twin_botanical": "Illicium anisatum",
                "danger_level": "SEVERE NEUROTOXIN (Anisatin & Shikimin Seizure Inducers)",
                "morphological_key": "Japanese Star Anise seed pods are smaller, asymmetrical, with irregular beaks and a strong camphor/terpentine-like odor rather than pure sweet licorice aroma.",
                "safe_verification": "True Chinese Star Anise has 8 uniform star points with smooth rounded seed carpels and sweet anethole fragrance."
            }
        ]
    },
    "stinging nettle": {
        "botanical_name": "Urtica dioica",
        "common_name": "Stinging Nettle",
        "toxic_twins": [
            {
                "twin_name": "White Deadnettle",
                "twin_botanical": "Lamium album",
                "danger_level": "BENIGN / NON-TOXIC LOOK-ALIKE",
                "morphological_key": "Deadnettle lacks stinging trichomes (hairs), has square stems and conspicuous white two-lipped (labiate) flowers.",
                "safe_verification": "Stinging nettle has stinging silica needles on stems and underside of serrated opposite leaves."
            }
        ]
    }
}


def check_toxic_lookalikes(query: str) -> Optional[Dict[str, Any]]:
    """Scan botanical query for high-risk toxic look-alike warnings with morphological identification keys."""
    q_lower = query.lower()
    for key, data in TOXIC_LOOKALIKES_REGISTRY.items():
        if key in q_lower or data["botanical_name"].lower() in q_lower or data["common_name"].lower() in q_lower:
            return {
                "matched_species": data["common_name"],
                "botanical_name": data["botanical_name"],
                "has_lookalike_warning": True,
                "toxic_twins": data["toxic_twins"],
                "botanical_authentication_notice": f"⚠️ Morphological Authentication Clearance Required: '{data['common_name']}' has dangerous twin look-alikes. Verify key structures before processing."
            }
    return None


def get_plant_anatomy_profile(plant_name: str, part_used: str = "") -> Dict[str, Any]:
    """
    Determine plant tissue anatomy and thermodynamic extraction physics.
    Maps cellular structures to boiling decoction, covered infusion, or cold maceration.
    """
    part_lower = (part_used or "").lower()
    name_lower = plant_name.lower()

    # 1. Mucilaginous storage tissue (Slippery elm, Marshmallow, Plantain)
    if any(m in name_lower or m in part_lower for m in ["slippery elm", "marshmallow", "plantago", "plantain", "mucilage", "althea"]):
        return {
            "primary_tissue_type": "Mucilage-Secreting Storage Parenchyma & Phloem Fibers",
            "secretory_structures": "Specialized mucilaginous cellular cavities",
            "active_compound_location": "Inner bark phloem and root storage cells",
            "recommended_extraction": "Cold Aqueous Maceration (Room temp or cool water steep for 4–8 hours)",
            "extraction_physics_rationale": "High heat breaks down mucilaginous polysaccharide polymers and creates unpalatable gelatinous coagulation. Cold aqueous extraction yields peak demulcent mucosal coating.",
            "recommended_temp_c": "20°C - 25°C",
            "simmer_time_min": 0,
            "steep_time_min": 240
        }

    # 2. Hard Lignified Roots, Rhizomes, Barks, and Seeds (Ginger, Licorice, Ashwagandha, Willow, Cinchona)
    if any(r in part_lower or r in name_lower for r in ["root", "rhizome", "bark", "wood", "seed", "cortex", "tuber", "corm", "ginger", "willow", "cinnamon", "ashwagandha", "licorice", "artemisia annua root"]):
        return {
            "primary_tissue_type": "Lignified Sclerenchyma, Periderm & Medullary Rays",
            "secretory_structures": "Internal resin ducts & cortical oleoresin cells",
            "active_compound_location": "Deep secondary xylem, phloem fibers and root cortex",
            "recommended_extraction": "Rolling Aqueous Decoction (Covered pot simmer at 95°C–100°C for 8–12 mins)",
            "extraction_physics_rationale": "Thick lignified secondary cell walls (sclerenchyma fibers) require prolonged thermal energy and water convection to lyse cell walls and extract deep polyphenolic alkaloids and saponins.",
            "recommended_temp_c": "95°C - 100°C",
            "simmer_time_min": 10,
            "steep_time_min": 5
        }

    # 3. Delicate Flowers, Buds & Volatile Petals (Chamomile, Passionflower, Hibiscus flowers)
    if any(f in part_lower or f in name_lower for f in ["flower", "petal", "bud", "corolla", "chamomile", "hibiscus", "passionflower", "flos"]):
        return {
            "primary_tissue_type": "Delicate Floral Parenchyma & Glandular Papillae",
            "secretory_structures": "Epidermal glandular trichomes & petal essential oil pockets",
            "active_compound_location": "Outer petal epidermal cells and secretory hairs",
            "recommended_extraction": "Gentle Covered Infusion (Pour 80°C–85°C water over specimen; steep COVERED for 5 mins)",
            "extraction_physics_rationale": "Boiling causes rapid vaporization of delicate monoterpenes (chamazulene, bisabolol) and heat denaturation of anthocyanins. Keeping the pot covered traps therapeutic condensation.",
            "recommended_temp_c": "80°C - 85°C",
            "simmer_time_min": 0,
            "steep_time_min": 5
        }

    # 4. Standard Leaf & Aerial Tops (Moringa, Artemisia, Neem, Basil, Peppermint, Bitter Leaf)
    return {
        "primary_tissue_type": "Photosynthetic Chlorenchyma & Spongy Mesophyll",
        "secretory_structures": "Glandular peltate trichomes & stomatal crypts",
        "active_compound_location": "Leaf mesophyll and external epidermal glands",
        "recommended_extraction": "Standard Covered Aqueous Infusion (Pour 88°C–92°C hot water; steep covered for 6–8 mins)",
        "extraction_physics_rationale": "Thin parenchymal cell walls readily release active flavonoids and bitter lactones without heavy boiling, preserving enzymatic and volatile integrity.",
        "recommended_temp_c": "88°C - 92°C",
        "simmer_time_min": 0,
        "steep_time_min": 7
    }
