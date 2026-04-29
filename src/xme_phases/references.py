from __future__ import annotations

from textwrap import dedent

REFERENCES: dict[str, dict[str, str]] = {
    "HGNC": {
        "label": "HGNC gene symbols and gene-family membership",
        "citation": "Gray KA, Yates B, Seal RL, Wright MW, Bruford EA. genenames.org: the HGNC resources in 2015. Nucleic Acids Research. 2015;43(D1):D1079-D1085. doi:10.1093/nar/gku1071. PMID:25361968.",
        "url": "https://www.genenames.org/download/",
        "doi": "10.1093/nar/gku1071",
    },
    "XMETDB": {
        "label": "XMetDB xenobiotic biotransformations",
        "citation": "Spjuth O, Rydberg P, Willighagen EL, Evelo CT, Jeliazkova N. XMetDB: an open access database for xenobiotic metabolism. Journal of Cheminformatics. 2016;8:47. doi:10.1186/s13321-016-0161-3. PMID:27651835.",
        "url": "https://jcheminf.biomedcentral.com/articles/10.1186/s13321-016-0161-3",
        "doi": "10.1186/s13321-016-0161-3",
    },
    "BRENDA": {
        "label": "BRENDA enzyme functional and reaction data",
        "citation": "Hauenstein J, Jeske L, Jade A, Krull M, Dummer K, Koblitz J, et al. BRENDA in 2026: a Global Core Biodata Resource for functional enzyme and metabolic data within the DSMZ Digital Diversity. Nucleic Acids Research. 2026;54(D1):D527-D534. doi:10.1093/nar/gkaf1113.",
        "url": "https://www.brenda-enzymes.org/",
        "doi": "10.1093/nar/gkaf1113",
    },
    "CLINPGX": {
        "label": "ClinPGx/PharmGKB pharmacogenomic annotations",
        "citation": "Gong L, Whirl-Carrillo M, Klein TE. PharmGKB, an Integrated Resource of Pharmacogenomic Knowledge. Current Protocols. 2021;1(8):e226. doi:10.1002/cpz1.226. PMID:34387941.",
        "url": "https://api.pharmgkb.org/",
        "doi": "10.1002/cpz1.226",
    },
    "PHARMVAR": {
        "label": "PharmVar star-allele nomenclature",
        "citation": "Gaedigk A, Ingelman-Sundberg M, Miller NA, Leeder JS, Whirl-Carrillo M, Klein TE; PharmVar Steering Committee. The Pharmacogene Variation (PharmVar) Consortium. Clinical Pharmacology & Therapeutics. 2018;103(3):399-401. doi:10.1002/cpt.910. PMID:29134625.",
        "url": "https://www.pharmvar.org/",
        "doi": "10.1002/cpt.910",
    },
    "TCDB": {
        "label": "Transporter Classification Database",
        "citation": "Saier MH Jr, Reddy VS, Moreno-Hagelsieb G, Hendargo KJ, Zhang Y, Iddamsetty V, et al. The Transporter Classification Database (TCDB): 2021 update. Nucleic Acids Research. 2021;49(D1):D461-D467. doi:10.1093/nar/gkaa1004.",
        "url": "https://tcdb.org/",
        "doi": "10.1093/nar/gkaa1004",
    },
    "FDA_DDI": {
        "label": "FDA drug interaction tables for CYP enzymes and transporters",
        "citation": "U.S. Food and Drug Administration. Drug Development and Drug Interactions: Table of Substrates, Inhibitors and Inducers. Accessed April 29, 2026.",
        "url": "https://www.fda.gov/drugs/drug-interactions-labeling/drug-development-and-drug-interactions-table-substrates-inhibitors-and-inducers",
        "doi": "",
    },
    "ISTRANSBASE": {
        "label": "ISTransbase drug transporter substrates/inhibitors",
        "citation": "Peng J, Yi J, Yang G, Huang Z, Cao D. ISTransbase: an online database for inhibitor and substrate of drug transporters. Database (Oxford). 2024;2024:baae053. doi:10.1093/database/baae053. PMID:38943608.",
        "url": "https://istransbase.scbdd.com/",
        "doi": "10.1093/database/baae053",
    },
    "SLC_TABLES": {
        "label": "SLC Tables solute-carrier family and member curation",
        "citation": "BioParadigms. SLC Tables: solute carrier gene families and members. Accessed April 29, 2026.",
        "url": "https://www.bioparadigms.org/slc/",
        "doi": "",
    },
}


def references_as_bibtex() -> str:
    """Return a compact BibTeX file for the built-in data sources."""
    return dedent(
        """
        @article{HGNC2015,
          title={genenames.org: the HGNC resources in 2015},
          author={Gray, Kristian A and Yates, Bethan and Seal, Ruth L and Wright, Mathew W and Bruford, Elspeth A},
          journal={Nucleic Acids Research},
          volume={43},
          number={D1},
          pages={D1079--D1085},
          year={2015},
          doi={10.1093/nar/gku1071}
        }

        @article{XMetDB2016,
          title={XMetDB: an open access database for xenobiotic metabolism},
          author={Spjuth, Ola and Rydberg, Patrik and Willighagen, Egon L and Evelo, Chris T and Jeliazkova, Nina},
          journal={Journal of Cheminformatics},
          volume={8},
          pages={47},
          year={2016},
          doi={10.1186/s13321-016-0161-3}
        }

        @article{BRENDA2026,
          title={BRENDA in 2026: a Global Core Biodata Resource for functional enzyme and metabolic data within the DSMZ Digital Diversity},
          author={Hauenstein, Julia and Jeske, Lisa and Jade, Antje and Krull, Mathias and Dummer, Katrin and Koblitz, Julia and others},
          journal={Nucleic Acids Research},
          volume={54},
          number={D1},
          pages={D527--D534},
          year={2026},
          doi={10.1093/nar/gkaf1113}
        }

        @article{PharmGKB2021,
          title={PharmGKB, an Integrated Resource of Pharmacogenomic Knowledge},
          author={Gong, Li and Whirl-Carrillo, Michelle and Klein, Teri E},
          journal={Current Protocols},
          volume={1},
          number={8},
          pages={e226},
          year={2021},
          doi={10.1002/cpz1.226}
        }

        @article{PharmVar2018,
          title={The Pharmacogene Variation (PharmVar) Consortium: Incorporation of the Human Cytochrome P450 (CYP) Allele Nomenclature Database},
          author={Gaedigk, Andrea and Ingelman-Sundberg, Magnus and Miller, Neil A and Leeder, J Steven and Whirl-Carrillo, Michelle and Klein, Teri E},
          journal={Clinical Pharmacology & Therapeutics},
          volume={103},
          number={3},
          pages={399--401},
          year={2018},
          doi={10.1002/cpt.910}
        }

        @article{TCDB2021,
          title={The Transporter Classification Database (TCDB): 2021 update},
          author={Saier, Milton H Jr and Reddy, Vamsee S and Moreno-Hagelsieb, Gabriel and Hendargo, Kevin J and Zhang, Yichi and others},
          journal={Nucleic Acids Research},
          volume={49},
          number={D1},
          pages={D461--D467},
          year={2021},
          doi={10.1093/nar/gkaa1004}
        }

        @misc{FDADDI,
          title={Drug Development and Drug Interactions: Table of Substrates, Inhibitors and Inducers},
          author={{U.S. Food and Drug Administration}},
          howpublished={\\url{https://www.fda.gov/drugs/drug-interactions-labeling/drug-development-and-drug-interactions-table-substrates-inhibitors-and-inducers}},
          note={Accessed 2026-04-29}
        }

        @article{ISTransbase2024,
          title={ISTransbase: an online database for inhibitor and substrate of drug transporters},
          author={Peng, Jinfu and Yi, Jiacai and Yang, Guoping and Huang, Zhijun and Cao, Dongsheng},
          journal={Database},
          volume={2024},
          pages={baae053},
          year={2024},
          doi={10.1093/database/baae053}
        }

        @misc{SLCTables,
          title={SLC Tables: solute carrier gene families and members},
          author={{BioParadigms}},
          howpublished={\\url{https://www.bioparadigms.org/slc/}},
          note={Accessed 2026-04-29}
        }
        """
    ).strip() + "\n"


def citation_for(ref_id: str) -> str:
    try:
        return REFERENCES[ref_id]["citation"]
    except KeyError as exc:
        raise KeyError(f"Unknown reference id: {ref_id}") from exc
